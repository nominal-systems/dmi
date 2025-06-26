const { MongoClient } = require('mongodb');

// Read environment variables
const mongoURI = process.env.MONGO_URI;
const dateCutoffStr = process.env.DATE_CUTOFF;
const collectionNames = ['internal_events'];

// Optional knobs (override via env if needed)
const BATCH_SIZE = parseInt(process.env.BATCH_SIZE, 10) || 100;
const DELAY_MS = parseInt(process.env.DELAY_MS, 10) || 200;
const DEFAULT_RETRY_MS = 1000;
const N_BATCH_CHECKPOINT = parseInt(process.env.N_BATCH_CHECKPOINT, 10) || 5000;

// Validation checks
if (!mongoURI) {
  console.error('Error: MONGO_URI environment variable is not set');
  process.exit(1);
}
if (!dateCutoffStr) {
  console.error('Error: DATE_CUTOFF environment variable is not set (format: YYYY-MM-DD)');
  process.exit(1);
}

// Parse cutoff date
const cutoffDate = new Date(dateCutoffStr);
if (isNaN(cutoffDate.getTime())) {
  console.error(`Error: Invalid DATE_CUTOFF format. Please use YYYY-MM-DD`);
  process.exit(1);
}

// Simple sleep helper
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

(async function () {
  const client = new MongoClient(mongoURI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });

  try {
    await client.connect();
    console.log(`Connected to MongoDB. Cutoff date: ${cutoffDate.toISOString().split('T')[0]}`);
    const db = client.db();

    for (const collectionName of collectionNames) {
      console.log(`\n--- Processing collection: ${collectionName} ---`);
      const collection = db.collection(collectionName);

      // Initial stats checkpoint before deletion loop
      try {
        const stats = await db.command({ collStats: collectionName });
        const sizeGB = (stats.size / (1024 ** 3)).toFixed(2);
        const docCount = await collection.countDocuments();
        console.log(
          `Checkpoint before deletion: documents = ${new Intl.NumberFormat('en-US').format(
            docCount
          )}, size = ${sizeGB} GB`
        );
      } catch (e) {
        console.warn(`Could not get initial stats for ${collectionName}: ${e.message}`);
      }

      let totalDeleted = 0;
      let batchCount = 0;

      while (true) {
        batchCount++;

        // 1) Fetch a small batch of _id's older than cutoffDate
        let docs;
        try {
          docs = await collection
            .find({ createdAt: { $lt: cutoffDate } })
            .sort({ _id: 1 })
            .limit(BATCH_SIZE)
            .project({ _id: 1 })
            .toArray();
        } catch (findErr) {
          console.error(`Batch ${batchCount}: Error fetching docs: ${findErr.message}`);
          break;
        }

        if (!docs.length) {
          console.log(`No more documents older than cutoff in ${collectionName}.`);
          break;
        }

        const idsToDelete = docs.map((d) => d._id);

        // 2) Delete that batch, retrying on 429
        let deletedThisBatch = 0;
        let attempt = 0;
        while (true) {
          attempt++;
          try {
            const deleteResult = await collection.deleteMany({ _id: { $in: idsToDelete } });
            deletedThisBatch = deleteResult.deletedCount;
            totalDeleted += deletedThisBatch;
            console.log(
              `Batch ${batchCount}: deleted ${deletedThisBatch} (cumulative ${totalDeleted})`
            );
            break; // exit retry loop
          } catch (err) {
            const isTooManyRequests = err.code === 16500 || err.codeName === 'RequestRateTooLarge';
            if (isTooManyRequests) {
              const retryAfter = err.errorResponse?.RetryAfterMs || DEFAULT_RETRY_MS;
              console.warn(
                `Batch ${batchCount} attempt ${attempt}: 429 - retrying in ${retryAfter} ms`
              );
              await sleep(retryAfter);
              continue; // retry same batch
            } else {
              console.error(
                `Batch ${batchCount} attempt ${attempt}: Unexpected delete error: ${err.message}`
              );
              deletedThisBatch = 0;
              break;
            }
          }
        }

        if (deletedThisBatch === 0) {
          // No documents deleted this batch (after retries) → exit loop
          console.log(`Batch ${batchCount}: 0 deleted. Exiting delete loop for ${collectionName}.`);
          break;
        }

        // 3) Every N_BATCH_CHECKPOINT batches, log a stats checkpoint
        if (batchCount % N_BATCH_CHECKPOINT === 0) {
          try {
            const stats = await db.command({ collStats: collectionName });
            const sizeGB = (stats.size / (1024 ** 3)).toFixed(2);
            const docCount = await collection.countDocuments();
            console.log(
              `Checkpoint at batch ${batchCount}: documents = ${new Intl.NumberFormat(
                'en-US'
              ).format(docCount)}, size = ${sizeGB} GB`
            );
          } catch (e) {
            console.warn(`Could not get stats at batch ${batchCount}: ${e.message}`);
          }
        }

        // 4) Wait before next batch to smooth RU/s
        await sleep(DELAY_MS);
      }

      // Final stats after deletion loop
      try {
        const finalStats = await db.command({ collStats: collectionName });
        const finalSizeGB = (finalStats.size / (1024 ** 3)).toFixed(2);
        const finalCount = await collection.countDocuments();
        console.log(
          `Final checkpoint: documents = ${new Intl.NumberFormat('en-US').format(
            finalCount
          )}, size = ${finalSizeGB} GB`
        );
      } catch (e) {
        console.warn(`Could not get final stats for ${collectionName}: ${e.message}`);
      }

      console.log(`Total documents deleted from ${collectionName}: ${totalDeleted}`);
    }
  } catch (error) {
    console.error('Error occurred during cleanup:', error);
  } finally {
    await client.close();
    console.log('MongoDB connection closed');
  }
})();
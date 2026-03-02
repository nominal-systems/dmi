const { MongoClient } = require('mongodb');

// Read environment variables
const mongoURI = process.env.MONGO_URI;
const dateCutoffStr = process.env.DATE_CUTOFF;
// Collection names to clean
const collectionsEnv = process.env.COLLECTIONS || '';
const collectionNames = collectionsEnv
  .split(',')
  .map((c) => c.trim())
  .filter(Boolean);

// Optional knobs (override via env if needed)
const BATCH_SIZE = parseInt(process.env.BATCH_SIZE, 10) || 100;
const DELAY_MS = parseInt(process.env.DELAY_MS, 10) || 200;
const DEFAULT_RETRY_MS = 1000;
const N_BATCH_CHECKPOINT = parseInt(process.env.N_BATCH_CHECKPOINT, 10) || 5000;
const MAX_BACKOFF_MS = parseInt(process.env.MAX_BACKOFF_MS, 10) || 30000;
const JITTER_MS = parseInt(process.env.JITTER_MS, 10) || 250;
const BACKOFF_BASE_MS = parseInt(process.env.BACKOFF_BASE_MS, 10) || 1000;
const DELETE_STRATEGY = (process.env.DELETE_STRATEGY || 'many').toLowerCase();

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

function singleLineError(err) {
  if (!err) return '';
  const msg = err.message || String(err);
  return msg.replace(/\s+/g, ' ').trim();
}

function getRetryAfterMs(err) {
  const retryAfter = err?.errorResponse?.RetryAfterMs;
  if (Number.isFinite(retryAfter) && retryAfter > 0) return retryAfter;
  return 0;
}

function computeBackoffMs(attempt, err) {
  const retryAfter = getRetryAfterMs(err);
  const base = Math.max(retryAfter, BACKOFF_BASE_MS);
  const exp = Math.min(attempt - 1, 6);
  const jitter = Math.floor(Math.random() * (JITTER_MS + 1));
  return Math.min(MAX_BACKOFF_MS, base * Math.pow(2, exp) + jitter);
}

function isRateLimited(err) {
  return err?.code === 16500 || err?.codeName === 'RequestRateTooLarge' || err?.code === 429;
}

async function withRateLimitRetry(operationName, fn) {
  let attempt = 0;
  while (true) {
    attempt++;
    try {
      return await fn();
    } catch (err) {
      if (!isRateLimited(err)) {
        throw err;
      }
      const backoff = computeBackoffMs(attempt, err);
      console.warn(
        `${operationName}: rate limited; retrying in ${backoff} ms (attempt ${attempt}, error=${err.code || err.codeName || 'unknown'} msg="${singleLineError(
          err
        )}")`
      );
      await sleep(backoff);
    }
  }
}

(async function () {
  const sanitizedUri = mongoURI.replace(/\/\/([^@]+)@/, '//<redacted>@');
  console.log(`Starting cleanup. URI=${sanitizedUri}`);
  console.log(
    `Options: BATCH_SIZE=${BATCH_SIZE}, DELAY_MS=${DELAY_MS}, N_BATCH_CHECKPOINT=${N_BATCH_CHECKPOINT}`
  );
  console.log(`Delete strategy: ${DELETE_STRATEGY}`);
  console.log(
    `Collections (${collectionNames.length}): ${collectionNames.length ? collectionNames.join(', ') : '(none)'}`
  );

  const client = new MongoClient(mongoURI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });

  try {
    await client.connect();
    console.log(`Connected to MongoDB. Cutoff date: ${cutoffDate.toISOString().split('T')[0]}`);
    const db = client.db();
    console.log(`Database: ${db.databaseName || '(default from URI)'}`);

    if (!collectionNames.length) {
      console.warn(
        'No collections specified. Set COLLECTIONS="col1,col2" to run deletions. Exiting.'
      );
      return;
    }

    for (const collectionName of collectionNames) {
      console.log(`\n--- Processing collection: ${collectionName} ---`);
      const collection = db.collection(collectionName);

      // Initial stats checkpoint before deletion loop
      try {
        const stats = await withRateLimitRetry(
          `collStats(${collectionName}) initial`,
          () => db.command({ collStats: collectionName })
        );
        const sizeGB = (stats.size / (1024 ** 3)).toFixed(2);
        const docCount = await withRateLimitRetry(
          `countDocuments(${collectionName}) initial`,
          () => collection.countDocuments()
        );
        console.log(
          `Checkpoint before deletion: documents = ${new Intl.NumberFormat('en-US').format(
            docCount
          )}, size = ${sizeGB} GB`
        );
      } catch (e) {
        console.warn(
          `Could not get initial stats for ${collectionName}: ${singleLineError(e)}`
        );
      }

      let totalDeleted = 0;
      let batchCount = 0;

      while (true) {
        batchCount++;

        // 1) Fetch a small batch of _id's older than cutoffDate
        let docs;
        try {
          docs = await withRateLimitRetry(`find(${collectionName}) batch ${batchCount}`, () =>
            collection
              .find({ createdAt: { $lt: cutoffDate } })
              .sort({ _id: 1 })
              .limit(BATCH_SIZE)
              .project({ _id: 1 })
              .toArray()
          );
        } catch (findErr) {
          console.error(
            `Batch ${batchCount}: Error fetching docs: ${singleLineError(findErr)}`
          );
          break;
        }

        if (!docs.length) {
          console.log(`No more documents older than cutoff in ${collectionName}.`);
          break;
        }

        const idsToDelete = docs.map((d) => d._id);

        // 2) Delete that batch, retrying on 429 and transient batch write errors
        let deletedThisBatch = 0;
        let attempt = 0;
        while (true) {
          attempt++;
          try {
            if (DELETE_STRATEGY === 'one') {
              for (let i = 0; i < idsToDelete.length; i++) {
                const id = idsToDelete[i];
                const res = await withRateLimitRetry(
                  `deleteOne(${collectionName}) batch ${batchCount} doc ${i + 1}`,
                  () => collection.deleteOne({ _id: id })
                );
                deletedThisBatch += res.deletedCount || 0;
              }
            } else {
              const deleteResult = await collection.deleteMany({ _id: { $in: idsToDelete } });
              deletedThisBatch = deleteResult.deletedCount;
            }
            totalDeleted += deletedThisBatch;
            console.log(
              `Batch ${batchCount}: deleted ${deletedThisBatch} (cumulative ${totalDeleted})`
            );
            break; // exit retry loop
          } catch (err) {
            const isTooManyRequests = isRateLimited(err);
            const isBatchWriteError = err.code === 16 || /Batch write error/i.test(err.message || '');
            if (isTooManyRequests || isBatchWriteError) {
              const backoff = computeBackoffMs(attempt, err);
              const reason = isTooManyRequests ? 'rate limited' : 'batch write error';
              console.warn(
                `Batch ${batchCount} attempt ${attempt}: ${reason} - retrying in ${backoff} ms (error=${err.code || err.codeName || 'unknown'} msg="${singleLineError(
                  err
                )}")`
              );
              await sleep(backoff);
              continue; // retry same batch
            }

            console.error(
              `Batch ${batchCount} attempt ${attempt}: Unexpected delete error: ${singleLineError(
                err
              )}`
            );
            deletedThisBatch = 0;
            break;
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
            const stats = await withRateLimitRetry(
              `collStats(${collectionName}) batch ${batchCount}`,
              () => db.command({ collStats: collectionName })
            );
            const sizeGB = (stats.size / (1024 ** 3)).toFixed(2);
            const docCount = await withRateLimitRetry(
              `countDocuments(${collectionName}) batch ${batchCount}`,
              () => collection.countDocuments()
            );
            console.log(
              `Checkpoint at batch ${batchCount}: documents = ${new Intl.NumberFormat(
                'en-US'
              ).format(docCount)}, size = ${sizeGB} GB`
            );
          } catch (e) {
            console.warn(
              `Could not get stats at batch ${batchCount}: ${singleLineError(e)}`
            );
          }
        }

        // 4) Wait before next batch to smooth RU/s
        await sleep(DELAY_MS);
      }

      // Final stats after deletion loop
      try {
        const finalStats = await withRateLimitRetry(
          `collStats(${collectionName}) final`,
          () => db.command({ collStats: collectionName })
        );
        const finalSizeGB = (finalStats.size / (1024 ** 3)).toFixed(2);
        const finalCount = await withRateLimitRetry(
          `countDocuments(${collectionName}) final`,
          () => collection.countDocuments()
        );
        console.log(
          `Final checkpoint: documents = ${new Intl.NumberFormat('en-US').format(
            finalCount
          )}, size = ${finalSizeGB} GB`
        );
      } catch (e) {
        console.warn(
          `Could not get final stats for ${collectionName}: ${singleLineError(e)}`
        );
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

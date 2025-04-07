const { MongoClient } = require('mongodb');

// Read environment variables
const mongoURI = process.env.MONGO_URI;
const dateCutoffStr = process.env.DATE_CUTOFF;
const collectionNames = ['external_requests', 'events']

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
  console.error(`Error: Invalid DATE_CUTOFF format. Please use YYYY-MM-DD format.`);
  process.exit(1);
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

    // Process collections sequentially
    for (const collectionName of collectionNames) {
      console.log(`\n--- Processing collection: ${collectionName} ---`);
      const collection = db.collection(collectionName);

      // Get collection stats
      try {
        const stats = await db.command({ collStats: collectionName });
        const collectionSizeInGB = (stats.size / (1024 ** 3)).toFixed(2);
        console.log(`Collection size before deletion: ${collectionSizeInGB} GB`);
      } catch (error) {
        console.warn(`Could not get stats for collection ${collectionName}: ${error.message}`);
      }

      let totalDeleted = 0;

      while (true) {
        // Get document count before deletion
        const documentCount = await collection.countDocuments();
        console.log(`Deleting docs from ${collectionName}\t\tCount: ${new Intl.NumberFormat('en-US').format(documentCount)}`);

        try {
          // Perform deletion with a timeout
          const deleteResult = await collection.deleteMany(
            { createdAt: { $lt: cutoffDate } },
            { maxTimeMS: 5000 } // Timeout in milliseconds
          );

          if (deleteResult.deletedCount === 0) {
            console.log(`No more documents to delete in ${collectionName}.`);
            break;
          }
          totalDeleted += deleteResult.deletedCount;
          console.log(`Deleted ${deleteResult.deletedCount} documents (total: ${totalDeleted})`);
        } catch (error) {
          if (error.code === 50) { // Timeout error
            console.warn('Delete operation timed out. Continuing...');
          } else {
            console.error(`Unexpected error in ${collectionName}:`, error);
            break;
          }
        }
      }

      // Get final collection stats
      try {
        const finalStats = await db.command({ collStats: collectionName });
        const finalCollectionSizeInGB = (finalStats.size / (1024 ** 3)).toFixed(2);
        console.log(`Final collection size for ${collectionName}: ${finalCollectionSizeInGB} GB`);
      } catch (error) {
        console.warn(`Could not get final stats for collection ${collectionName}: ${error.message}`);
      }
    }
  } catch (error) {
    console.error('Error occurred:', error);
  } finally {
    await client.close();
    console.log('MongoDB connection closed');
  }
})();

import { PutCommand, GetCommand, ScanCommand, BatchWriteCommand } from '@aws-sdk/lib-dynamodb';
import { dynamoDocClient } from '../aws-clients.js';
import { config } from '../config.js';

/**
 * Amazon DynamoDB: The Tracking Ledger.
 * A highly responsive database used exclusively to keep a precise log of which
 * customer records have been successfully synchronized, which are pending, and when they were last updated.
 */

/**
 * Record a single customer sync event into the ledger.
 */
export const recordCustomerSync = async (customerRecord, batchId, status = 'SYNCED') => {
  const timestamp = new Date().toISOString();
  const ledgerItem = {
    customerId: customerRecord.customerId,
    salesforceId: customerRecord.salesforceId,
    email: customerRecord.email,
    fullName: customerRecord.fullName,
    tier: customerRecord.tier,
    syncStatus: status, // SYNCED | PENDING | ERROR
    checksum: customerRecord.checksum,
    batchId: batchId || `batch-${Date.now()}`,
    lastSyncTimestamp: timestamp,
    lastModifiedInCrm: customerRecord.lastModifiedInCrm,
    version: customerRecord.version || 1,
    auditTrail: {
      syncedBy: 'AWS-Lambda-Customer-Sync-Engine',
      system: 'Enterprise-Data-Platform',
      statusMessage: `Successfully synchronized record with Salesforce (${status})`,
    },
  };

  const command = new PutCommand({
    TableName: config.dynamoLedgerTable,
    Item: ledgerItem,
  });

  await dynamoDocClient.send(command);
  return ledgerItem;
};

/**
 * Batch update multiple customer ledger records.
 */
export const batchRecordCustomerSync = async (customerRecords, batchId, status = 'SYNCED') => {
  const timestamp = new Date().toISOString();
  const putRequests = customerRecords.map((record) => ({
    PutRequest: {
      Item: {
        customerId: record.customerId,
        salesforceId: record.salesforceId,
        email: record.email,
        fullName: record.fullName,
        tier: record.tier,
        syncStatus: status,
        checksum: record.checksum,
        batchId: batchId || `batch-${Date.now()}`,
        lastSyncTimestamp: timestamp,
        lastModifiedInCrm: record.lastModifiedInCrm,
      },
    },
  }));

  // Batch write items (up to 25 per DynamoDB request chunk)
  const chunkSize = 25;
  const results = [];
  for (let i = 0; i < putRequests.length; i += chunkSize) {
    const chunk = putRequests.slice(i, i + chunkSize);
    const command = new BatchWriteCommand({
      RequestItems: {
        [config.dynamoLedgerTable]: chunk,
      },
    });
    const res = await dynamoDocClient.send(command);
    results.push(res);
  }

  return { totalSynced: customerRecords.length, batches: results.length };
};

/**
 * Retrieves the tracking ledger state for a specific customer.
 */
export const getCustomerLedgerEntry = async (customerId) => {
  const command = new GetCommand({
    TableName: config.dynamoLedgerTable,
    Key: { customerId },
  });
  const response = await dynamoDocClient.send(command);
  return response.Item || null;
};

/**
 * Lists the latest records in the synchronization ledger.
 */
export const listLedgerEntries = async (limit = 20) => {
  const command = new ScanCommand({
    TableName: config.dynamoLedgerTable,
    Limit: limit,
  });
  const response = await dynamoDocClient.send(command);
  return response.Items || [];
};

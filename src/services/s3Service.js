import { PutObjectCommand, GetObjectCommand, ListObjectsV2Command } from '@aws-sdk/client-s3';
import { s3Client } from '../aws-clients.js';
import { config } from '../config.js';

/**
 * Amazon S3: The Secure Staging Area.
 * Acts as a temporary, high-capacity holding zone for massive batches of customer data
 * while they are being processed in transit.
 */

/**
 * Stages a raw incoming batch of customer records in Amazon S3.
 */
export const stageCustomerBatch = async (batchId, rawRecords) => {
  const key = `staging/batches/${batchId}/raw-customers.json`;
  const payload = {
    batchId,
    recordCount: rawRecords.length,
    stagedAt: new Date().toISOString(),
    records: rawRecords,
  };

  const command = new PutObjectCommand({
    Bucket: config.s3StagingBucket,
    Key: key,
    Body: JSON.stringify(payload, null, 2),
    ContentType: 'application/json',
    Metadata: {
      'batch-id': batchId,
      'record-count': String(rawRecords.length),
    },
  });

  const response = await s3Client.send(command);
  return {
    bucket: config.s3StagingBucket,
    key,
    recordCount: rawRecords.length,
    etag: response.ETag,
  };
};

/**
 * Archives processed and synchronized customer records to permanent S3 storage.
 */
export const archiveProcessedBatch = async (batchId, processedRecords, syncSummary = {}) => {
  const key = `archives/batches/${batchId}/synced-customers.json`;
  const payload = {
    batchId,
    syncedAt: new Date().toISOString(),
    summary: syncSummary,
    records: processedRecords,
  };

  const command = new PutObjectCommand({
    Bucket: config.s3StagingBucket,
    Key: key,
    Body: JSON.stringify(payload, null, 2),
    ContentType: 'application/json',
  });

  const response = await s3Client.send(command);
  return {
    bucket: config.s3StagingBucket,
    key,
    etag: response.ETag,
  };
};

/**
 * Retrieves staged customer batch from S3.
 */
export const getStagedBatch = async (key) => {
  const command = new GetObjectCommand({
    Bucket: config.s3StagingBucket,
    Key: key,
  });
  const response = await s3Client.send(command);
  const content = await response.Body.transformToString();
  return JSON.parse(content);
};

/**
 * Lists all staged batches in S3.
 */
export const listStagedBatches = async (prefix = 'staging/batches/') => {
  const command = new ListObjectsV2Command({
    Bucket: config.s3StagingBucket,
    Prefix: prefix,
  });
  const response = await s3Client.send(command);
  return response.Contents || [];
};

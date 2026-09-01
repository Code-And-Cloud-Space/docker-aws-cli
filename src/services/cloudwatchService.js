import { PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';
import { PutLogEventsCommand, CreateLogStreamCommand } from '@aws-sdk/client-cloudwatch-logs';
import { cloudWatchClient, cloudWatchLogsClient } from '../aws-clients.js';
import { config } from '../config.js';

/**
 * Amazon CloudWatch: Enterprise Monitoring, Observability & Compliance.
 * Centralizes data tracking, monitors throughput, latency, error retries,
 * and maintains an encrypted, auditable compliance log.
 */

/**
 * Publishes operational and business metrics for customer synchronization.
 */
export const publishSyncMetric = async (metricName, value = 1, unit = 'Count', dimensions = []) => {
  try {
    const command = new PutMetricDataCommand({
      Namespace: config.cloudwatchNamespace,
      MetricData: [
        {
          MetricName: metricName,
          Value: value,
          Unit: unit,
          Timestamp: new Date(),
          Dimensions: [
            { Name: 'Service', Value: 'EnterpriseCustomerSync' },
            { Name: 'Environment', Value: config.nodeEnv },
            ...dimensions,
          ],
        },
      ],
    });
    return await cloudWatchClient.send(command);
  } catch (err) {
    console.warn(`[CloudWatch Metric] Warning: Failed to emit metric "${metricName}":`, err.message);
  }
};

/**
 * Emits comprehensive batch sync metrics in one call.
 */
export const recordBatchMetrics = async (summary = {}) => {
  const { totalRecords = 0, syncedCount = 0, errorCount = 0, durationMs = 0 } = summary;

  await Promise.allSettled([
    publishSyncMetric('RecordsProcessed', totalRecords, 'Count'),
    publishSyncMetric('RecordsSyncedSuccess', syncedCount, 'Count'),
    publishSyncMetric('RecordsSyncErrors', errorCount, 'Count'),
    publishSyncMetric('BatchSyncDurationMs', durationMs, 'Milliseconds'),
  ]);
};

/**
 * Records structured security audit logs for compliance tracking.
 */
export const logAuditTrail = async (auditEntry) => {
  const logStreamName = `sync-audit-${new Date().toISOString().slice(0, 10)}`;
  const logPayload = {
    timestamp: new Date().toISOString(),
    compliance: 'SOC2-HIPAA-Compliant-Audit-Log',
    source: 'AWS-Lambda-Customer-Sync',
    ...auditEntry,
  };

  try {
    // Attempt to create stream if not present
    await cloudWatchLogsClient.send(new CreateLogStreamCommand({
      logGroupName: config.logGroupName,
      logStreamName,
    })).catch(() => {});

    const command = new PutLogEventsCommand({
      logGroupName: config.logGroupName,
      logStreamName,
      logEvents: [
        {
          timestamp: Date.now(),
          message: JSON.stringify(logPayload),
        },
      ],
    });

    return await cloudWatchLogsClient.send(command);
  } catch (err) {
    console.warn('[CloudWatch Logs] Warning: Logging fallback:', err.message);
  }
};

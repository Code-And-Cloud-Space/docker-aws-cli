import { StartExecutionCommand, DescribeExecutionCommand } from '@aws-sdk/client-sfn';
import { sfnClient } from '../aws-clients.js';
import { config } from '../config.js';

/**
 * AWS Step Functions (SFN): The Digital Project Manager.
 * Orchestrates the entire synchronization workflow, dictating the order of operations,
 * managing schedules, and handling automated retries if a system is temporarily unavailable.
 */

/**
 * Initiates the multi-step Enterprise Customer Synchronization workflow.
 */
export const triggerCustomerSyncWorkflow = async (batchId, syncOptions = {}) => {
  const executionName = `sync-batch-${batchId}-${Date.now()}`;
  const inputPayload = {
    batchId,
    workflow: 'EnterpriseCustomerDataSynchronization',
    initiatedAt: new Date().toISOString(),
    source: syncOptions.source || 'Salesforce-CRM',
    target: 'Enterprise-Data-Platform',
    options: {
      retryAttempts: 3,
      stageToS3: true,
      updateLedger: true,
      emitMetrics: true,
      ...syncOptions,
    },
  };

  const command = new StartExecutionCommand({
    stateMachineArn: config.sfnStateMachineArn,
    name: executionName,
    input: JSON.stringify(inputPayload),
  });

  const response = await sfnClient.send(command);
  return {
    executionArn: response.executionArn,
    startDate: response.startDate,
    executionName,
    batchId,
  };
};

/**
 * Retrieves the live status of a Step Function workflow execution.
 */
export const getSyncWorkflowExecution = async (executionArn) => {
  const command = new DescribeExecutionCommand({
    executionArn,
  });
  return await sfnClient.send(command);
};

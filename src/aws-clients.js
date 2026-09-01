import { S3Client } from '@aws-sdk/client-s3';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { SFNClient } from '@aws-sdk/client-sfn';
import { CloudWatchClient } from '@aws-sdk/client-cloudwatch';
import { CloudWatchLogsClient } from '@aws-sdk/client-cloudwatch-logs';
import { SecretsManagerClient } from '@aws-sdk/client-secrets-manager';
import { config } from './config.js';

const isTestOrLocal = process.env.NODE_ENV === 'test' || Boolean(config.endpoint);

const clientConfig = {
  region: config.region,
  maxAttempts: isTestOrLocal ? 1 : 3,
  ...(config.endpoint && { endpoint: config.endpoint }),
  ...(isTestOrLocal && {
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'test',
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'test',
    },
  }),
};

// 1. S3 Client (forcePathStyle enabled for LocalStack compatibility)
export const s3Client = new S3Client({
  ...clientConfig,
  ...(config.endpoint && { forcePathStyle: true }),
});

// 2. DynamoDB & Document Client
const rawDynamoClient = new DynamoDBClient(clientConfig);
export const dynamoDocClient = DynamoDBDocumentClient.from(rawDynamoClient, {
  marshallOptions: {
    removeUndefinedValues: true,
    convertEmptyValues: true,
  },
});

// 3. Step Functions (SFN) Client
export const sfnClient = new SFNClient(clientConfig);

// 4. CloudWatch Metrics & Logs Clients
export const cloudWatchClient = new CloudWatchClient(clientConfig);
export const cloudWatchLogsClient = new CloudWatchLogsClient(clientConfig);

// 5. Secrets Manager Client
export const secretsManagerClient = new SecretsManagerClient(clientConfig);

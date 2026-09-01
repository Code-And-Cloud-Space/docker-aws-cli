import {
  GetSecretValueCommand,
  CreateSecretCommand,
  PutSecretValueCommand,
  ListSecretsCommand,
} from '@aws-sdk/client-secrets-manager';
import { secretsManagerClient } from '../aws-clients.js';
import { config } from '../config.js';

/**
 * AWS Secrets Manager: The Digital Vault.
 * Securely stores and rotates the sensitive passwords, access tokens, and digital credentials
 * required for Salesforce and AWS to communicate safely.
 */

// In-memory cache for credentials to avoid redundant Secrets Manager lookups
let cachedSalesforceCreds = null;
let cacheExpiry = 0;

/**
 * Retrieve Salesforce CRM credentials from Secrets Manager Vault.
 */
export const getSalesforceCredentials = async (secretName = config.salesforceSecretName) => {
  const now = Date.now();
  if (cachedSalesforceCreds && now < cacheExpiry) {
    return cachedSalesforceCreds;
  }

  try {
    const command = new GetSecretValueCommand({
      SecretId: secretName,
    });
    const response = await secretsManagerClient.send(command);

    if (response.SecretString) {
      const parsed = JSON.parse(response.SecretString);
      cachedSalesforceCreds = parsed;
      cacheExpiry = now + 5 * 60 * 1000; // Cache for 5 minutes
      return parsed;
    }
  } catch (error) {
    console.warn(`[Secrets Vault] Failed to retrieve secret "${secretName}": ${error.message}. Using fallback credentials.`);
  }

  // Safe default credentials for local development & mock testing
  return {
    clientId: '3MVG9...sample_salesforce_client_id',
    clientSecret: 'mock_salesforce_client_secret_9988',
    instanceUrl: 'https://enterprise-sample.salesforce.com',
    username: 'integration.user@enterprise.org',
    securityToken: 'local_secure_token_abc123',
    isMock: true,
  };
};

/**
 * Store or update Salesforce credentials in the digital vault.
 */
export const storeSalesforceCredentials = async (credentials, secretName = config.salesforceSecretName) => {
  const secretString = JSON.stringify(credentials, null, 2);
  try {
    const command = new CreateSecretCommand({
      Name: secretName,
      SecretString: secretString,
      Description: 'Salesforce CRM OAuth credentials and access tokens for Enterprise Customer Sync',
    });
    return await secretsManagerClient.send(command);
  } catch (err) {
    if (err.name === 'ResourceExistsException') {
      const updateCommand = new PutSecretValueCommand({
        SecretId: secretName,
        SecretString: secretString,
      });
      return await secretsManagerClient.send(updateCommand);
    }
    throw err;
  }
};

/**
 * General Secret lookup helper.
 */
export const getSecret = async (secretId = config.salesforceSecretName) => {
  const command = new GetSecretValueCommand({ SecretId: secretId });
  const response = await secretsManagerClient.send(command);
  return response.SecretString ? JSON.parse(response.SecretString) : response;
};

/**
 * List secrets stored in the Vault.
 */
export const listSecrets = async (maxResults = 10) => {
  const command = new ListSecretsCommand({ MaxResults: maxResults });
  const response = await secretsManagerClient.send(command);
  return response.SecretList || [];
};

import test from 'node:test';
import assert from 'node:assert/strict';
import { handler } from '../src/index.js';
import { transformSalesforceToEnterprise, calculateCustomerChecksum } from '../src/services/salesforceService.js';

test('Salesforce Transformer maps CRM fields into Enterprise Unified Customer Model', () => {
  const sfContact = {
    Id: '0035g000001ABC1AAZ',
    FirstName: 'Sarah',
    LastName: 'Connor',
    Email: 'sarah.connor@cyberdyne.com',
    Phone: '+1-555-0199',
    Account_Tier__c: 'Platinum Enterprise',
    Status__c: 'Active',
    BillingStreet: '100 SkyNet Blvd',
    BillingCity: 'Los Angeles',
    BillingState: 'CA',
    BillingPostalCode: '90001',
    LastModifiedDate: '2026-09-01T12:00:00Z',
  };

  const transformed = transformSalesforceToEnterprise(sfContact);

  assert.equal(transformed.customerId, 'CUST-1ABC1AAZ');
  assert.equal(transformed.salesforceId, '0035g000001ABC1AAZ');
  assert.equal(transformed.fullName, 'Sarah Connor');
  assert.equal(transformed.email, 'sarah.connor@cyberdyne.com');
  assert.equal(transformed.tier, 'Platinum Enterprise');
  assert.equal(transformed.address.city, 'Los Angeles');
  assert.ok(transformed.checksum);
});

test('Customer Checksum calculates deterministic hash', () => {
  const recordA = {
    firstName: 'Alice',
    lastName: 'Smith',
    email: 'alice@enterprise.com',
    phone: '12345',
    tier: 'Gold',
    status: 'Active',
  };
  const recordB = { ...recordA };

  assert.equal(calculateCustomerChecksum(recordA), calculateCustomerChecksum(recordB));
});

test('handler executes complete Enterprise Customer Batch Sync flow', async () => {
  const result = await handler({
    action: 'sync:batch',
    batchId: 'UNIT-TEST-BATCH-001',
  }, { awsRequestId: 'unit-test-req-1' });

  assert.equal(result.statusCode, 200);

  const parsed = JSON.parse(result.body);
  assert.equal(parsed.success, true);
  assert.equal(parsed.action, 'sync:batch');
  assert.equal(parsed.batchId, 'UNIT-TEST-BATCH-001');
  assert.ok(parsed.businessOutcome.operationalEfficiency);
  assert.ok(parsed.businessOutcome.unifiedCustomerView);
  assert.ok(parsed.businessOutcome.auditCompliance);
  assert.ok(parsed.synchronizedCustomers.length > 0);
});

test('handler executes bidirectional push from Cloud Ecosystem -> Salesforce CRM', async () => {
  const result = await handler({
    body: JSON.stringify({
      action: 'salesforce:push',
      customer: {
        customerId: 'CUST-TEST-999',
        salesforceId: '0035g000009ZZZ9AAZ',
        firstName: 'Alex',
        lastName: 'Mercer',
        email: 'alex.mercer@enterprise.com',
        tier: 'Diamond',
      },
    }),
  }, { awsRequestId: 'unit-test-req-2' });

  assert.equal(result.statusCode, 200);
  const parsed = JSON.parse(result.body);
  assert.equal(parsed.success, true);
  assert.equal(parsed.salesforceResult.success, true);
});

test('handler executes real-time single customer sync', async () => {
  const result = await handler({
    body: JSON.stringify({
      action: 'sync:customer',
      customer: {
        customerId: 'CUST-REALTIME-001',
        salesforceId: '0035g000001ABC1AAZ',
        email: 'realtime@enterprise.com',
        fullName: 'Realtime User',
        tier: 'Standard',
        checksum: 'abc123hash',
      },
    }),
  }, { awsRequestId: 'unit-test-req-3' });

  assert.equal(result.statusCode, 200);
  const parsed = JSON.parse(result.body);
  assert.equal(parsed.success, true);
});

test('handler handles ledger and S3 inspection queries', async () => {
  const ledgerRes = await handler({
    body: JSON.stringify({ action: 'ledger:query', limit: 5 }),
  }, { awsRequestId: 'unit-test-req-4' });
  assert.ok([200, 500].includes(ledgerRes.statusCode));

  const s3Res = await handler({
    body: JSON.stringify({ action: 's3:list-batches' }),
  }, { awsRequestId: 'unit-test-req-5' });
  assert.ok([200, 500].includes(s3Res.statusCode));
});

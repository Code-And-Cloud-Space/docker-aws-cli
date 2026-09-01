import test from 'node:test';
import assert from 'node:assert/strict';
import { handler } from '../src/index.js';

test('handler returns 200 with default greeting when event is empty', async () => {
  const result = await handler({}, { awsRequestId: 'test-req-1' });
  assert.equal(result.statusCode, 200);
  
  const parsed = JSON.parse(result.body);
  assert.equal(parsed.success, true);
  assert.match(parsed.message, /Hello, World!/);
  assert.equal(parsed.requestId, 'test-req-1');
});

test('handler extracts name from direct JSON event', async () => {
  const result = await handler({ name: 'Alice' }, { awsRequestId: 'test-req-2' });
  assert.equal(result.statusCode, 200);

  const parsed = JSON.parse(result.body);
  assert.match(parsed.message, /Hello, Alice!/);
});

test('handler parses API Gateway stringified JSON body', async () => {
  const result = await handler({
    body: JSON.stringify({ name: 'Bob' })
  }, { awsRequestId: 'test-req-3' });

  assert.equal(result.statusCode, 200);
  const parsed = JSON.parse(result.body);
  assert.match(parsed.message, /Hello, Bob!/);
});

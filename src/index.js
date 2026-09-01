/**
 * AWS Lambda handler entry point.
 * Compatible with AWS Lambda Node.js 20+ runtime & Docker container images.
 *
 * @param {Object} event - AWS Lambda event object (API Gateway, direct invocation, SQS, etc.)
 * @param {Object} context - AWS Lambda execution context
 * @returns {Promise<Object>} Response object (HTTP response formatted for API Gateway or custom payload)
 */
export const handler = async (event = {}, context = {}) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] Incoming Request - RequestId: ${context.awsRequestId || 'local-test'}`);
  console.log('Event payload:', JSON.stringify(event, null, 2));

  // Determine request payload (handles API Gateway body or direct JSON invocation)
  let parsedBody = {};
  if (event.body) {
    try {
      parsedBody = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } catch {
      parsedBody = { raw: event.body };
    }
  } else {
    parsedBody = event;
  }

  const name = parsedBody?.name || event?.queryStringParameters?.name || 'World';

  const responseBody = {
    success: true,
    message: `Hello, ${name}! Your Node.js Docker container is running seamlessly on AWS Lambda.`,
    timestamp,
    requestId: context.awsRequestId || 'local-execution',
    environment: process.env.NODE_ENV || 'production',
    data: {
      receivedEvent: event,
    },
  };

  // Standard API Gateway / Lambda Function URL response format
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': true,
    },
    body: JSON.stringify(responseBody, null, 2),
  };
};

// If run directly via `node src/index.js` for quick local testing without Docker
if (process.argv[1]?.endsWith('src/index.js')) {
  console.log('--- Running local direct execution test ---');
  handler({ name: 'Local Developer' }, { awsRequestId: 'local-run-123' })
    .then((res) => console.log('Handler output:\n', res))
    .catch((err) => console.error('Handler error:', err));
}

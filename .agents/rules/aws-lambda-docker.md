---
trigger: always_on
description: Guidelines for developing and modifying Node.js AWS Lambda Docker functions
---

# AWS Lambda Container Development Guidelines

1. **Lambda Handler Signature**:
   - Always maintain `export const handler = async (event, context) => { ... }`.
   - Ensure the handler gracefully handles both direct invocations (`event.name`) and API Gateway proxy integrations (`JSON.parse(event.body)`).

2. **Docker Best Practices for Lambda**:
   - The base image should be the official AWS Lambda image: `public.ecr.aws/lambda/nodejs:<version>`.
   - Files must be placed relative to `${LAMBDA_TASK_ROOT}`.
   - The `CMD` format is `[ "path/to/file.handlerFunction" ]` without file extension in the handler string (e.g., `src/index.handler`).

3. **Dependencies & Packaging**:
   - Only install production dependencies (`npm ci --omit=dev` or `npm install --omit=dev`) inside the container.
   - Keep image size lean and fast to minimize cold start latency.

# Antigravity Project Configuration: Node.js AWS Lambda Docker

Welcome to the **Node.js AWS Lambda Docker** project. This repository contains a production-ready containerized Node.js application designed to run locally and deploy to AWS Lambda via container images (Amazon ECR).

## Project Structure
- `src/index.js` - Main entry point containing the AWS Lambda `handler(event, context)`.
- `Dockerfile` - AWS Lambda Node.js base container setup.
- `docker-compose.yml` - Docker compose configuration for running and testing the Lambda Runtime Interface Emulator locally on port 9000.
- `test/` - Unit tests using Node.js test runner (`npm test`).
- `.agents/rules/` - Antigravity agent guidelines and best practices for this codebase.

## Developer Workflows
- **Run Unit Tests**: `npm test`
- **Build Container**: `npm run docker:build`
- **Run Container Locally**: `npm run docker:run` or `npm run docker:compose`
- **Test Local Container**: `npm run docker:test` (sends a POST event to the local emulator)

## Coding Conventions
- Use modern JavaScript (ES Modules, `import`/`export`).
- Ensure handler returns standard AWS Lambda / API Gateway response objects (`statusCode`, `headers`, `body` as stringified JSON).
- Avoid bundling local OS dependencies or global paths inside the Docker container.

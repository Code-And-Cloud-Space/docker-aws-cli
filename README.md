# Dockerized Node.js AWS Lambda Application

A production-ready Dockerized Node.js project built for local development and direct deployment to **AWS Lambda** as a container image. Configured with **Antigravity CLI** agent rules and workflows.

---

## 📁 Project Structure

```
.
├── .agents/
│   └── rules/
│       └── aws-lambda-docker.md   # Antigravity agent guidelines for Lambda Docker
├── src/
│   └── index.js                   # Lambda handler function (ES Modules)
├── test/
│   └── handler.test.js            # Native Node.js unit tests
├── .dockerignore                  # Files excluded from Docker builds
├── .gitignore                     # Git ignore rules for Node, Docker, OS
├── AGENTS.md                      # Antigravity project context & instructions
├── docker-compose.yml             # Local container runner with Lambda Emulator
├── Dockerfile                     # AWS Lambda Node.js container definition
├── package.json                   # Project metadata and NPM scripts
└── README.md                      # Documentation & deployment guide
```

---

## 🚀 Quick Start (Local Development)

### 1. Run Unit Tests
```bash
npm test
```

### 2. Direct Node.js Execution
You can invoke the handler directly without Docker:
```bash
npm start
```

---

## 🐳 Running with Docker (Local Lambda Emulator)

The Dockerfile uses the official AWS Lambda Node.js base image (`public.ecr.aws/lambda/nodejs:20`), which comes with the built-in **AWS Lambda Runtime Interface Emulator (RIE)** for local testing.

### 1. Build the Docker Image
```bash
npm run docker:build
# Or: docker build -t node-aws-lambda:latest .
```

### 2. Run the Container Locally
```bash
npm run docker:run
# Or: docker compose up
```
*The container will start listening on port `9000` (mapped to internal emulator port `8080`).*

### 3. Test Invocation via `curl`
While the container is running, send a test payload in a separate terminal:
```bash
npm run docker:test
```
Or run directly:
```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"name": "Developer"}'
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": true
  },
  "body": "{\n  \"success\": true,\n  \"message\": \"Hello, Developer! Your Node.js Docker container is running seamlessly on AWS Lambda.\",\n  ...\n}"
}
```

---

## ☁️ Deploying to AWS Lambda via Amazon ECR

### Step 1: Authenticate Docker with Amazon ECR
Replace `<AWS_REGION>` and `<AWS_ACCOUNT_ID>` with your AWS credentials:
```bash
aws ecr get-login-password --region <AWS_REGION> | \
  docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com
```

### Step 2: Create an ECR Repository (if not already created)
```bash
aws ecr create-repository \
  --repository-name node-aws-lambda \
  --region <AWS_REGION>
```

### Step 3: Tag and Push Image to ECR
```bash
docker tag node-aws-lambda:latest <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/node-aws-lambda:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/node-aws-lambda:latest
```

### Step 4: Create or Update AWS Lambda Function

#### Option A: Create New Lambda Function
```bash
aws lambda create-function \
  --function-name node-docker-lambda \
  --package-type Image \
  --code ImageUri=<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/node-aws-lambda:latest \
  --role arn:aws:iam::<AWS_ACCOUNT_ID>:role/<YOUR_LAMBDA_EXECUTION_ROLE> \
  --region <AWS_REGION>
```

#### Option B: Update Existing Lambda Function Code
```bash
aws lambda update-function-code \
  --function-name node-docker-lambda \
  --image-uri <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/node-aws-lambda:latest \
  --region <AWS_REGION>
```

---

## 🤖 Antigravity CLI Integration

This workspace is fully configured for Google Antigravity CLI:
- [AGENTS.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/AGENTS.md): Provides project context, scripts, and workflows.
- [.agents/rules/aws-lambda-docker.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.agents/rules/aws-lambda-docker.md): Provides coding conventions and deployment guidelines for AI agent pair programming.

# AWS Lambda Node.js 20 Official Base Image
# Includes the Lambda Runtime Interface Client & Local Runtime Interface Emulator (RIE)
FROM public.ecr.aws/lambda/nodejs:20

# Set working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy package manifests
COPY package*.json ./

# Install production dependencies only
RUN if [ -f package-lock.json ]; then npm ci --omit=dev; else npm install --omit=dev; fi

# Copy application source code
COPY src/ ./src/

# Command handler: [file.function] (relative to LAMBDA_TASK_ROOT)
CMD [ "src/index.handler" ]

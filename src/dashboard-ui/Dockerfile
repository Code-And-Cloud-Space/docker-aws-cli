FROM node:20-alpine

WORKDIR /app

# Install Vercel CLI globally
RUN npm install -g vercel

COPY package.json ./
COPY vercel.json ./
COPY index.html ./
COPY app.js ./

EXPOSE 3000

ENV PORT=3000

CMD ["vercel", "dev", "--listen", "0.0.0.0:3000", "--yes"]

FROM node:20-alpine

WORKDIR /app

# Install Vercel's official Serve CLI and Vercel CLI
RUN npm install -g serve vercel

COPY package.json ./
COPY vercel.json ./
COPY index.html ./
COPY app.js ./

EXPOSE 3000

ENV PORT=3000

CMD ["serve", "-s", ".", "-l", "3000"]

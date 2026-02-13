# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Configure npm for production reliability
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-timeout 300000 && \
    npm config set audit false && \
    npm config set fund false

# Copy package files first (for better Docker layer caching)
COPY package*.json ./

# Install dependencies with npm ci (clean install for production)
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit

# Copy application source
COPY . .

# Build the application (outputs ./dist)
RUN npm run build

# Runtime stage: serve the built SPA via nginx (production-grade)
FROM nginx:1.29-alpine3.22 AS production

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config (SPA fallback + /health)
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80


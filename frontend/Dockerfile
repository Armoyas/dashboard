# Frontend Dockerfile for Next.js 15 Dashboard
# Multi-stage build with standalone output

# ---- Base Stage ----
FROM node:20-alpine AS base
WORKDIR /app
ENV NODE_ENV=production

# ---- Builder Stage ----
FROM base AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use --legacy-peer-deps for compatibility)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build Next.js app with standalone output
RUN npm run build

# ---- Runner Stage ----
FROM node:20-alpine AS runner
WORKDIR /app

# Set NODE_ENV
ENV NODE_ENV=production
ENV NODE_PORT=3000
ENV PORT=3000

# Copy standalone build
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./public/_next/static
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the app
CMD ["node", "server.js"]

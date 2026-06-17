# syntax=docker/dockerfile:1.6
# Multi-stage build: deps -> builder -> runner.
# Designed to be ignored entirely by Vercel (Vercel only reads package.json /
# next.config.mjs / tsconfig.json). Nothing here mutates those files, so the
# existing Vercel deployment is unaffected.

# ── Stage 1: deps ─────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# --legacy-peer-deps: vite@7 (transitive via @vitejs/plugin-react) declares a
# strict @types/node peer that our pinned 20.14 falls below. Types-only peer,
# benign at runtime.
RUN npm ci --legacy-peer-deps

# ── Stage 2: builder ──────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Bake NEXT_PUBLIC_API_BASE into the client bundle at build time.
ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
RUN npm run build

# ── Stage 3: runner ───────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next             ./.next
COPY --from=builder /app/public            ./public
COPY --from=builder /app/package.json      ./package.json
COPY --from=builder /app/package-lock.json ./package-lock.json
COPY --from=builder /app/node_modules      ./node_modules

# Shrink the runtime tree: drop devDeps (vitest, RTL, jsdom, vite-tsconfig-paths,
# @vitejs/plugin-react, etc.) that were copied in via the full node_modules.
RUN npm prune --omit=dev --legacy-peer-deps

# Non-root user (alpine syntax: addgroup/adduser are busybox, no --create-home).
RUN addgroup -S appuser && adduser -S appuser -G appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 3100

# package.json `start` script already binds -p 3100 — no edit needed.
CMD ["npm", "start"]

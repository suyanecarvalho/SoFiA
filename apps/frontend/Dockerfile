FROM node:20-alpine AS pruner
WORKDIR /app
RUN corepack enable
COPY turbo.json package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/ packages/
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm exec turbo prune --scope=frontend --docker
FROM node:20-alpine AS installer
WORKDIR /app
RUN corepack enable
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=installer /app/ .
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo run build --filter=frontend
FROM node:20-alpine AS runner
WORKDIR /app
RUN corepack enable && pnpm add serve
COPY --from=builder /app/apps/frontend/dist ./dist
EXPOSE 5173
CMD ["pnpm", "exec", "serve", "-s", "dist", "-l", "5173"]
FROM node:20-alpine AS development
WORKDIR /app
RUN corepack enable
COPY --from=installer /app/ .
COPY . .
EXPOSE 5173
CMD ["pnpm", "--filter", "frontend", "run", "dev", "--host"]
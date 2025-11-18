# Stage 1: Create a pruned monorepo subset for the 'frontend' app
FROM node:20-alpine AS pruner
WORKDIR /app

RUN corepack enable

# Copy all package manifests and the lockfile
COPY turbo.json package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# IMPORTANT: Copy the manifests from all apps and packages
# This is needed for pnpm to install everything correctly
COPY apps/ apps/
COPY packages/ packages/

# Install ALL dependencies from the lockfile. This is the robust way
# to ensure the 'turbo' CLI is available and correctly linked.
RUN pnpm install --frozen-lockfile

# Copy the rest of the source code (for pruning). Some files will be
# copied again, but this is safe and ensures everything is present.
COPY . .

# CORRECTED: Add the --docker flag to create the 'json' and 'full' subdirectories
RUN pnpm exec turbo prune --scope=frontend --docker


# Stage 2: Install dependencies for the pruned subset (this part is now correct)
FROM node:20-alpine AS installer
WORKDIR /app
RUN corepack enable
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile


# Stage 3: Build the application (for production) (this part is now correct)
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=installer /app/ .
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo run build --filter=frontend


# Stage 4: Final, lightweight production image (for production) (this part is unchanged)
FROM node:20-alpine AS runner
WORKDIR /app
RUN corepack enable && pnpm add serve
COPY --from=builder /app/apps/frontend/dist ./dist
EXPOSE 5173
CMD ["pnpm", "exec", "serve", "-s", "dist", "-l", "5173"]


# Stage 5: A stage for running the development server (this part is unchanged)
FROM node:20-alpine AS development
WORKDIR /app
RUN corepack enable
COPY --from=installer /app/ .
COPY . .
EXPOSE 5173
CMD ["pnpm", "--filter", "frontend", "run", "dev", "--host"]
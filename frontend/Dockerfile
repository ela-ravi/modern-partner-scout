# =============================================================================
# PartnerScout AI — Frontend Dockerfile
# Multi-stage build:
#   Stage 1 (build)  — Node 20: install deps + build static files
#   Stage 2 (serve)  — Nginx Alpine: serve the production bundle
# =============================================================================

# =============================================================================
# STAGE 1: Build the React/Vite application
# =============================================================================
FROM node:20-alpine AS build

WORKDIR /app

# -- Install dependencies first (cached layer) --------------------------------
# Copying package files separately lets Docker skip `npm ci` when only source
# code changes, saving ~30-60s on rebuilds
COPY package.json package-lock.json ./
RUN npm ci

# -- Copy source code ----------------------------------------------------------
COPY . .

# -- Vite environment variables ------------------------------------------------
# These ARGs are passed at build time via `docker compose build --build-arg`
# Vite inlines them into the JS bundle (import.meta.env.VITE_*)
ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

# Convert ARGs to ENVs so Vite can read them during `npm run build`
ENV VITE_API_URL=$VITE_API_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

# -- Build the production bundle -----------------------------------------------
# Output goes to /app/dist
RUN npm run build

# =============================================================================
# STAGE 2: Serve with Nginx
# =============================================================================
FROM nginx:1.27-alpine AS serve

# -- Copy custom Nginx config for SPA routing ----------------------------------
# This config handles client-side routing by falling back to index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# -- Copy built assets from the build stage ------------------------------------
COPY --from=build /app/dist /usr/share/nginx/html

# -- Expose port 80 inside the container ---------------------------------------
# The outer Nginx reverse proxy routes traffic to this container
EXPOSE 80

# -- Start Nginx in the foreground ---------------------------------------------
# "daemon off" keeps the process in the foreground so Docker can manage it
CMD ["nginx", "-g", "daemon off;"]

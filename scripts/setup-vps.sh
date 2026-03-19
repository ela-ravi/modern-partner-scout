#!/bin/bash
# =============================================================================
# PartnerScout AI — One-Time VPS Setup Script
#
# Run this ONCE on a fresh Hostinger KVM2 VPS (Ubuntu 24.04) to:
#   1. Install Docker and Docker Compose plugin
#   2. Clone the repository
#   3. Set up directory permissions
#
# Usage (SSH into your VPS first, then run):
#   curl -sSL https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/scripts/setup-vps.sh | bash
#   — or —
#   scp scripts/setup-vps.sh root@YOUR_VPS_IP:/tmp/ && ssh root@YOUR_VPS_IP 'bash /tmp/setup-vps.sh'
#
# After this script runs, all future deployments are handled by GitHub Actions.
# You should NOT need to SSH into the VPS again for routine operations.
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, and pipe failures

# -- Color output for readability ---------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

log()  { echo -e "${GREEN}[SETUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# -- Step 1: Update system packages -------------------------------------------
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# -- Step 2: Install Docker ---------------------------------------------------
# Check if Docker is already installed
if command -v docker &> /dev/null; then
    log "Docker is already installed: $(docker --version)"
else
    log "Installing Docker..."

    # Install prerequisites
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker apt repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine + Compose plugin
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    log "Docker installed: $(docker --version)"
fi

# -- Step 3: Verify Docker Compose plugin --------------------------------------
if docker compose version &> /dev/null; then
    log "Docker Compose plugin: $(docker compose version)"
else
    warn "Docker Compose plugin not found. Please install it manually."
    exit 1
fi

# -- Step 4: Install Git (if not present) --------------------------------------
if ! command -v git &> /dev/null; then
    log "Installing Git..."
    apt-get install -y git
fi

# -- Step 5: Clone the repository ---------------------------------------------
DEPLOY_DIR="/opt/partner-scout"

if [ -d "$DEPLOY_DIR" ]; then
    log "Directory $DEPLOY_DIR already exists, pulling latest..."
    cd "$DEPLOY_DIR"
    git pull origin main
else
    log "Cloning repository to $DEPLOY_DIR..."
    # IMPORTANT: Replace this URL with your actual GitHub repo URL
    # For private repos, set up a deploy key or use HTTPS with a token
    git clone https://github.com/YOUR_ORG/YOUR_REPO.git "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# -- Step 6: Set permissions ---------------------------------------------------
# Ensure the deploy directory is owned by the current user
log "Setting directory permissions..."
chown -R "$(whoami):$(whoami)" "$DEPLOY_DIR"

# -- Step 7: Create backend .env placeholder -----------------------------------
# GitHub Actions will overwrite this on the first deploy, but having a file
# prevents Docker Compose from erroring out if you run it manually first
if [ ! -f "$DEPLOY_DIR/backend/.env" ]; then
    log "Creating placeholder backend/.env..."
    cat > "$DEPLOY_DIR/backend/.env" << 'EOF'
# Placeholder — GitHub Actions will overwrite this on deploy
ENVIRONMENT=production
EOF
fi

# -- Step 8: Enable Docker to start on boot -----------------------------------
log "Enabling Docker to start on boot..."
systemctl enable docker
systemctl start docker

# -- Done! ---------------------------------------------------------------------
log "============================================="
log "  VPS setup complete!"
log "============================================="
log ""
log "Next steps:"
log "  1. Add your VPS SSH key to GitHub Secrets"
log "  2. Add all required env vars to GitHub Secrets"
log "  3. Push to 'main' or trigger the workflow manually"
log ""
log "The GitHub Actions workflow will handle everything from here."
log "No more SSH needed for routine deployments!"

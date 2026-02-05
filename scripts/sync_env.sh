#!/usr/bin/env bash
# Wrapper for setup/sync_env.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_SCRIPT="${SCRIPT_DIR}/../setup/sync_env.sh"

if [[ ! -f "${SETUP_SCRIPT}" ]]; then
    echo "Error: ${SETUP_SCRIPT} not found"
    exit 1
fi

exec "${SETUP_SCRIPT}" "$@"

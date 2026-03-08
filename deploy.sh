#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "${ROOT_DIR}/docker-compose.yml" ]; then
  echo "docker-compose.yml not found in ${ROOT_DIR}"
  exit 1
fi

if [ ! -x "${ROOT_DIR}/scripts/deploy/remote-deploy.sh" ]; then
  chmod +x "${ROOT_DIR}/scripts/deploy/remote-deploy.sh"
fi

APP_DIR="${ROOT_DIR}" COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-mojo}" bash "${ROOT_DIR}/scripts/deploy/remote-deploy.sh"

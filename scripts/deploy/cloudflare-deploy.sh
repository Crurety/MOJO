#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRANGLER_VERSION="${WRANGLER_VERSION:-3.60.1}"
CLOUDFLARE_FRONTEND_PROJECT="${CLOUDFLARE_FRONTEND_PROJECT:-mojo-frontend}"
CLOUDFLARE_ADMIN_PROJECT="${CLOUDFLARE_ADMIN_PROJECT:-mojo-admin}"
CLOUDFLARE_DEPLOY_BRANCH="${CLOUDFLARE_DEPLOY_BRANCH:-${GITHUB_REF_NAME:-main}}"
CLOUDFLARE_APPLY_D1_SCHEMA="${CLOUDFLARE_APPLY_D1_SCHEMA:-false}"
CLOUDFLARE_D1_DATABASE="${CLOUDFLARE_D1_DATABASE:-mojo-prod}"

log() {
  printf '[cloudflare-deploy] %s\n' "$*"
}

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log "Missing required command: ${cmd}"
    exit 1
  fi
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    log "Missing required environment variable: ${name}"
    exit 1
  fi
}

run_wrangler() {
  local workdir="$1"
  shift
  (
    cd "$workdir"
    npx --yes "wrangler@${WRANGLER_VERSION}" "$@"
  )
}

build_project() {
  local project_dir="$1"
  local project_name="$2"

  log "Installing dependencies for ${project_name}"
  (
    cd "$project_dir"
    npm ci
  )

  log "Building ${project_name}"
  (
    cd "$project_dir"
    npm run build
  )
}

deploy_pages_project() {
  local project_dir="$1"
  local project_name="$2"

  log "Deploying Pages project ${project_name} from ${project_dir}/dist"
  run_wrangler "$project_dir" pages deploy dist --project-name "$project_name" --branch "$CLOUDFLARE_DEPLOY_BRANCH"
}

main() {
  require_command node
  require_command npm
  require_env CLOUDFLARE_API_TOKEN
  require_env CLOUDFLARE_ACCOUNT_ID

  log "Starting Cloudflare deployment for branch ${CLOUDFLARE_DEPLOY_BRANCH}"
  log "Using frontend project ${CLOUDFLARE_FRONTEND_PROJECT}, admin project ${CLOUDFLARE_ADMIN_PROJECT}"

  build_project "${ROOT_DIR}/frontend" "frontend"
  build_project "${ROOT_DIR}/admin" "admin"

  log "Installing dependencies for cf-worker"
  (
    cd "${ROOT_DIR}/cf-worker"
    npm ci
  )

  if [[ "${CLOUDFLARE_APPLY_D1_SCHEMA}" == "true" ]]; then
    log "Applying D1 schema to ${CLOUDFLARE_D1_DATABASE}"
    run_wrangler "${ROOT_DIR}/cf-worker" d1 execute "${CLOUDFLARE_D1_DATABASE}" --remote --file ./schema.sql
  else
    log "Skipping D1 schema apply"
  fi

  log "Deploying worker mojo-api"
  run_wrangler "${ROOT_DIR}/cf-worker" deploy

  deploy_pages_project "${ROOT_DIR}/frontend" "${CLOUDFLARE_FRONTEND_PROJECT}"
  deploy_pages_project "${ROOT_DIR}/admin" "${CLOUDFLARE_ADMIN_PROJECT}"

  log "Cloudflare deployment completed"
}

main "$@"

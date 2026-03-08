#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/opt/mojo}"
COMMIT_SHA="${COMMIT_SHA:-}"
LOCK_DIR="${APP_DIR}/.deploy-cache"

log() {
  printf '[deploy] %s\n' "$*"
}

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log "Missing required command: ${cmd}"
    exit 1
  fi
}

detect_compose() {
  if docker compose version >/dev/null 2>&1; then
    DC=(docker compose)
    return
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    DC=(docker-compose)
    return
  fi
  log "Docker Compose is not installed"
  exit 1
}

cleanup_legacy_containers() {
  local legacy_names=(
    ai-platform-backend
    ai-platform-celery-beat
    ai-platform-celery-cleanup
    ai-platform-celery-default
    ai-platform-celery-notification
    ai-platform-celery-operation
    ai-platform-mongodb
    ai-platform-mysql
    ai-platform-nginx
    ai-platform-redis
  )

  for name in "${legacy_names[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -Fxq "$name"; then
      log "Removing legacy container: ${name}"
      docker rm -f "$name" >/dev/null || true
    fi
  done
}

build_web_project() {
  local project="$1"
  local lock_file="${APP_DIR}/${project}/package-lock.json"
  local marker_file="${LOCK_DIR}/${project}.lock.sha256"
  local current_hash
  local marker_hash
  local need_install=1

  if [[ ! -f "$lock_file" ]]; then
    log "Missing lock file for ${project}: ${lock_file}"
    exit 1
  fi

  current_hash="$(sha256sum "$lock_file" | awk '{print $1}')"
  marker_hash=""

  if [[ -f "$marker_file" ]]; then
    marker_hash="$(cat "$marker_file")"
  fi

  if [[ -d "${APP_DIR}/${project}/node_modules" && "$current_hash" == "$marker_hash" ]]; then
    need_install=0
  fi

  pushd "${APP_DIR}/${project}" >/dev/null
  if [[ "$need_install" -eq 1 ]]; then
    log "Installing ${project} dependencies"
    npm ci --prefer-offline --no-audit
    printf '%s\n' "$current_hash" >"$marker_file"
  else
    log "Skipping npm ci for ${project}; lock file unchanged"
  fi

  log "Building ${project}"
  npm run build
  popd >/dev/null
}

check_http() {
  local name="$1"
  local url="$2"
  local retries="${3:-30}"
  local sleep_seconds="${4:-3}"
  local attempt=1

  while [[ "$attempt" -le "$retries" ]]; do
    if curl -fsS --max-time 5 "$url" >/dev/null; then
      log "Healthy: ${name} (${url})"
      return 0
    fi
    sleep "$sleep_seconds"
    attempt=$((attempt + 1))
  done

  log "Unhealthy: ${name} (${url})"
  return 1
}

main() {
  require_command docker
  require_command git
  require_command curl
  require_command sha256sum
  detect_compose

  if [[ ! -d "$APP_DIR" ]]; then
    log "Application directory not found: ${APP_DIR}"
    exit 1
  fi

  cd "$APP_DIR"
  if [[ ! -f docker-compose.yml ]]; then
    log "docker-compose.yml not found in ${APP_DIR}"
    exit 1
  fi

  mkdir -p "$LOCK_DIR"

  export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-mojo}"
  if [[ -z "$COMMIT_SHA" ]]; then
    if git rev-parse --short=12 HEAD >/dev/null 2>&1; then
      COMMIT_SHA="$(git rev-parse --short=12 HEAD)"
    else
      COMMIT_SHA="local"
    fi
  fi
  export MOJO_IMAGE_TAG="$COMMIT_SHA"
  log "Using COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}, MOJO_IMAGE_TAG=${MOJO_IMAGE_TAG}"

  cleanup_legacy_containers

  if command -v npm >/dev/null 2>&1; then
    build_web_project "frontend"
    build_web_project "admin"
  else
    log "npm not found; skipping web build"
  fi

  if [[ ! -d "${APP_DIR}/frontend/dist" || ! -d "${APP_DIR}/admin/dist" ]]; then
    log "frontend/admin dist not found. Install npm and build assets before deploy."
    exit 1
  fi

  log "Validating compose file"
  "${DC[@]}" config >/dev/null

  local wait_args=()
  if "${DC[@]}" up --help | grep -q -- '--wait'; then
    wait_args=(--wait --wait-timeout 300)
  fi

  log "Starting services"
  local max_up_retries="${DEPLOY_UP_RETRIES:-3}"
  local up_attempt=1
  while true; do
    if "${DC[@]}" up -d --build --remove-orphans "${wait_args[@]}"; then
      break
    fi

    if [[ "$up_attempt" -ge "$max_up_retries" ]]; then
      log "docker compose up failed after ${up_attempt} attempts; printing logs"
      "${DC[@]}" ps || true
      "${DC[@]}" logs --tail=200 backend || true
      "${DC[@]}" logs --tail=120 nginx || true
      exit 1
    fi

    log "docker compose up attempt ${up_attempt}/${max_up_retries} failed; retrying in 15s"
    up_attempt=$((up_attempt + 1))
    sleep 15
  done

  log "Running alembic migrations"
  if ! "${DC[@]}" exec -T backend alembic upgrade head; then
    log "alembic migration failed; continuing with running services"
  fi

  check_http "backend-health" "http://127.0.0.1:8000/health" 40 3
  check_http "nginx-root" "http://127.0.0.1/" 40 3
  check_http "nginx-admin" "http://127.0.0.1/admin/" 40 3
  check_http "nginx-health" "http://127.0.0.1/health" 40 3

  log "Deployment completed successfully"
  "${DC[@]}" ps
}

main "$@"

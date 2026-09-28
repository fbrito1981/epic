#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${EPIC_HOST:-nano-server}"
WEBROOT="/etc/apps/webapps/epic"
CONFDIR="/etc/apps/conf/epic"
COMPOSE="/home/user/docker-compose.yml"

tar -C "$ROOT" \
  --exclude ".git" \
  --exclude "docs" \
  --exclude "deploy" \
  --exclude "README.md" \
  --exclude ".gitignore" \
  -czf - . | ssh "$REMOTE" "cat > /tmp/epic-site.tgz"

scp "$ROOT/deploy/nginx.conf" "$ROOT/deploy/ensure-service.py" "$REMOTE:/tmp/"

ssh "$REMOTE" "sudo mkdir -p '$WEBROOT' '$CONFDIR' \
  && sudo find '$WEBROOT' -mindepth 1 -delete \
  && sudo tar -xzf /tmp/epic-site.tgz -C '$WEBROOT' \
  && sudo cp /tmp/nginx.conf '$CONFDIR/nginx.conf' \
  && sudo python3 /tmp/ensure-service.py '$COMPOSE' \
  && sudo docker compose -f '$COMPOSE' up -d --no-deps epic \
  && curl -fsS -o /dev/null -w 'local:%{http_code}\n' http://127.0.0.1:8091/"

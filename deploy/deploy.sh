#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${EPIC_HOST:-nano-server}"
STAGE="/tmp/epic-site"
WEBROOT="/etc/apps/webapps/epic"
CONFDIR="/etc/apps/conf/epic"
COMPOSE="/home/user/docker-compose.yml"

rsync -az --delete \
  --exclude ".git/" \
  --exclude "docs/" \
  --exclude "deploy/" \
  --exclude "README.md" \
  --exclude ".gitignore" \
  "$ROOT/" "$REMOTE:$STAGE/"

rsync -az \
  "$ROOT/deploy/nginx.conf" \
  "$ROOT/deploy/ensure-service.py" \
  "$REMOTE:/tmp/"

ssh "$REMOTE" "sudo mkdir -p '$WEBROOT' '$CONFDIR' \
  && sudo rsync -a --delete '$STAGE/' '$WEBROOT/' \
  && sudo cp /tmp/nginx.conf '$CONFDIR/nginx.conf' \
  && sudo python3 /tmp/ensure-service.py '$COMPOSE' \
  && sudo docker compose -f '$COMPOSE' up -d --no-deps epic \
  && curl -fsS -o /dev/null -w 'local:%{http_code}\n' http://127.0.0.1:8091/"

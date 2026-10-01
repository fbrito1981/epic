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

scp "$ROOT/deploy/nginx.conf" "$ROOT/deploy/ensure-service.py" "$ROOT/deploy/form-server.py" "$ROOT/deploy/mail.env.example" "$REMOTE:/tmp/"

ssh "$REMOTE" "sudo mkdir -p '$WEBROOT' '$CONFDIR' \
  && sudo find '$WEBROOT' -mindepth 1 -delete \
  && sudo tar -xzf /tmp/epic-site.tgz -C '$WEBROOT' \
  && sudo cp /tmp/nginx.conf '$CONFDIR/nginx.conf' \
  && sudo cp /tmp/form-server.py '$CONFDIR/form-server.py' \
  && sudo test -f '$CONFDIR/mail.env' || sudo cp /tmp/mail.env.example '$CONFDIR/mail.env' \
  && sudo python3 /tmp/ensure-service.py '$COMPOSE' \
  && sudo docker compose -f '$COMPOSE' up -d --no-deps --force-recreate epic-form \
  && sudo docker compose -f '$COMPOSE' up -d --no-deps epic \
  && sudo docker exec epic nginx -s reload \
  && curl -fsS -o /dev/null -w 'local:%{http_code}\n' http://127.0.0.1:8091/ \
  && curl -sS -o /dev/null -w 'form:%{http_code}\n' -X POST http://127.0.0.1:8091/api/garantia -H 'Content-Type: application/json' -d '{}'"

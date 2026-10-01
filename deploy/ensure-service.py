#!/usr/bin/env python3
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text()
block = """
  epic:
    image: nginx:1.27-alpine
    container_name: epic
    restart: unless-stopped
    ports:
      - "127.0.0.1:8091:80"
    volumes:
      - /etc/apps/webapps/epic:/usr/share/nginx/html:ro
      - /etc/apps/conf/epic/nginx.conf:/etc/nginx/conf.d/default.conf:ro
"""
if "container_name: epic" not in text:
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + block)
    text = path.read_text()
    print("compose: servicio epic agregado")
else:
    print("compose: servicio epic ya estaba")

form = """
  epic-form:
    image: python:3.12-alpine
    container_name: epic-form
    restart: unless-stopped
    env_file:
      - /etc/apps/conf/epic/mail.env
    command: ["python", "-u", "/app/form-server.py"]
    volumes:
      - /etc/apps/conf/epic/form-server.py:/app/form-server.py:ro
"""
if "container_name: epic-form" not in text:
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + form)
    print("compose: servicio epic-form agregado")
else:
    print("compose: servicio epic-form ya estaba")

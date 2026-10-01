#!/usr/bin/env python3
"""Recibe el formulario de garantía y lo manda por SMTP a info@fuerz4.com.

El primer paso manda un código de 8 dígitos al email del cliente.
La solicitud se envía recién cuando ese código vuelve confirmado.
"""

import hmac
import json
import os
import re
import secrets
import smtplib
import threading
import time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
MAIL_TO = os.environ.get("MAIL_TO", "info@fuerz4.com")
MAIL_FROM = os.environ.get("MAIL_FROM", "info@fuerz4.com")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"

FIELDS = (
    ("nombre", ("nombre", "Nombre completo"), 120, False),
    ("direccion", ("direccion", "Dirección y localidad"), 200, False),
    ("telefono", ("telefono", "Teléfono"), 40, False),
    ("email", ("email", "Email"), 120, False),
    ("comentarios", ("comentarios", "Comentarios"), 2000, True),
)
LABELS = {
    "nombre": "Nombre completo",
    "direccion": "Dirección y localidad",
    "telefono": "Teléfono",
    "email": "Email",
    "comentarios": "Comentarios",
}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9]{8,15}$")
HITS = {}
PENDING = {}
LOCK = threading.Lock()
WINDOW = 3600
LIMIT = 8
CODE_TTL = 15 * 60
MAX_ATTEMPTS = 5


def client_ip(handler):
    forwarded = handler.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()[:80]
    return handler.client_address[0]


def too_many(ip):
    now = time.time()
    recent = [stamp for stamp in HITS.get(ip, []) if now - stamp < WINDOW]
    if len(recent) >= LIMIT:
        HITS[ip] = recent
        return True
    recent.append(now)
    HITS[ip] = recent
    return False


def clean(value, limit, keep_lines):
    text = str(value or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(ch if ch == "\n" or ch >= " " else " " for ch in text)
    if not keep_lines:
        text = " ".join(text.split())
    else:
        text = "\n".join(line.strip() for line in text.split("\n")).strip()
    return text[:limit].strip()


def first(data, names):
    for name in names:
        if name in data and data[name]:
            value = data[name]
            return value[0] if isinstance(value, list) else value
    return ""


def parse_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0 or length > 20000:
        raise ValueError("cuerpo inválido")
    raw = handler.rfile.read(length)
    content_type = handler.headers.get("Content-Type", "")
    if "application/json" in content_type:
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("cuerpo inválido")
        return payload
    parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] for key, values in parsed.items()}


def message_for(values):
    lines = [f"{LABELS[key]}: {values[key]}" for key in ("nombre", "direccion", "telefono", "email")]
    lines.append("")
    lines.append("Comentarios:")
    lines.append(values["comentarios"])
    return "\n".join(lines)


def code_message(code):
    return (
        "Tu código para enviar la solicitud de garantía de EPIC Sound System es:\n\n"
        f"{code}\n\n"
        "Tiene 8 dígitos y vence en 15 minutos. Si no pediste este código, ignorá este mensaje."
    )


def send_mail(subject, recipient, body, reply_to=""):
    if DRY_RUN:
        return
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("correo no configurado")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = recipient
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)


def values_from(data):
    values = {}
    for key, names, limit, keep_lines in FIELDS:
        values[key] = clean(first(data, names), limit, keep_lines)
        if not values[key]:
            raise ValueError("faltan datos")
    values["email"] = values["email"].lower()
    if not EMAIL_RE.match(values["email"]):
        raise ValueError("email inválido")
    values["telefono"] = "".join(ch for ch in values["telefono"] if ch.isdigit())
    if not PHONE_RE.match(values["telefono"]):
        raise ValueError("teléfono inválido")
    return values


def purge(now):
    expired = [token for token, item in PENDING.items() if item["expires"] <= now]
    for token in expired:
        del PENDING[token]
    overflow = len(PENDING) - 100
    if overflow > 0:
        oldest = sorted(PENDING, key=lambda token: PENDING[token]["expires"])[:overflow]
        for token in oldest:
            del PENDING[token]


def start_code(values):
    now = time.time()
    code = f"{secrets.randbelow(100_000_000):08d}"
    token = secrets.token_urlsafe(24)
    with LOCK:
        purge(now)
        stale = [key for key, item in PENDING.items() if item["email"] == values["email"]]
        for key in stale:
            del PENDING[key]
        PENDING[token] = {
            "values": values,
            "code": code,
            "email": values["email"],
            "expires": now + CODE_TTL,
            "attempts": 0,
        }
    send_mail(
        "Código de verificación — EPIC Sound System",
        values["email"],
        code_message(code),
        MAIL_TO,
    )
    print("garantia: código enviado", flush=True)
    payload = {"ok": True, "token": token}
    if DRY_RUN:
        payload["codigo"] = code
    return payload


def confirm_code(data):
    token = clean(first(data, ("token",)), 80, False)
    code = "".join(ch for ch in clean(first(data, ("codigo", "código")), 16, False) if ch.isdigit())[:8]
    with LOCK:
        purge(time.time())
        item = PENDING.get(token)
        if item is None:
            raise ValueError("código vencido")
        item["attempts"] += 1
        matches = len(code) == 8 and hmac.compare_digest(code, item["code"])
        if item.get("sending") or item["attempts"] > MAX_ATTEMPTS or not matches:
            if item["attempts"] > MAX_ATTEMPTS:
                del PENDING[token]
            raise ValueError("código incorrecto")
        item["sending"] = True
        values = item["values"]
    try:
        send_mail(
            "Garantía EPIC Sound System",
            MAIL_TO,
            message_for(values),
            values["email"],
        )
    except Exception:
        with LOCK:
            current = PENDING.get(token)
            if current is not None:
                current["sending"] = False
                current["attempts"] -= 1
        raise
    with LOCK:
        PENDING.pop(token, None)
    print("garantia: enviado", flush=True)
    return {"ok": True}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/garantia":
            self.respond(404, {"ok": False, "error": "no encontrado"})
            return
        try:
            data = parse_body(self)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.respond(400, {"ok": False, "error": "datos inválidos"})
            return
        step = clean(first(data, ("paso",)), 20, False)
        if step == "confirmar":
            try:
                self.respond(200, confirm_code(data))
            except ValueError as error:
                self.respond(400, {"ok": False, "error": str(error)})
            except Exception as error:
                print(f"garantia: no se envió ({type(error).__name__})", flush=True)
                self.respond(502, {"ok": False, "error": "no se pudo enviar"})
            return
        if step != "codigo":
            self.respond(400, {"ok": False, "error": "datos inválidos"})
            return
        with LOCK:
            if too_many(client_ip(self)):
                self.respond(429, {"ok": False, "error": "demasiadas solicitudes"})
                return
        if clean(first(data, ("_honey",)), 80, False):
            self.respond(200, {"ok": True, "token": secrets.token_urlsafe(24)})
            return
        try:
            values = values_from(data)
        except ValueError as error:
            self.respond(400, {"ok": False, "error": str(error)})
            return
        try:
            self.respond(200, start_code(values))
        except Exception as error:
            print(f"garantia: no se envió ({type(error).__name__})", flush=True)
            self.respond(502, {"ok": False, "error": "no se pudo enviar"})

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/health":
            self.respond(200, {"ok": True})
            return
        self.respond(404, {"ok": False, "error": "no encontrado"})

    def respond(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"garantia escuchando en {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

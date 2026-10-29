#!/usr/bin/env python3
"""SQL Crack v1.0.0 — local, simulation-only training dashboard.
No outbound requests, SQL execution, network attacks, or real database access.
"""
from __future__ import annotations

import csv
import io
import json
import mimetypes
import re
import secrets
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DUMPS = DATA / "dumps"
LOG_FILE = DATA / "events.jsonl"
LOCK = threading.RLock()
VERSION = "v1.0.0"
SCENARIOS = {
    "baseline": ("Temel güvenlik kontrolü", "INFO", "Temel örnek işlem tamamlandı."),
    "quote": ("Tırnak karakteri kontrolü", "WARNING", "Tırnak kullanımı örnek senaryoda işaretlendi."),
    "union": ("UNION ifadesi kontrolü", "WARNING", "Örnek SQL anahtar sözcüğü tespit simülasyonu tamamlandı."),
    "timing": ("Zaman tabanlı kontrol", "WARNING", "Zaman tabanlı davranış simüle edildi; gecikme uygulanmadı."),
    "error": ("Hata yönetimi kontrolü", "WARNING", "Örnek hata mesajı algılama senaryosu tamamlandı."),
    "dump": ("Sahte SQL dump", "INFO", "Yalnızca sentetik kayıtlarla örnek .sql dosyası oluşturuldu."),
}
TARGETS = {"demo-app", "training-box", "login-mock", "catalog-mock"}
MAX_BODY = 8 * 1024
MAX_EVENTS = 10000


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def setup():
    DUMPS.mkdir(parents=True, exist_ok=True)
    LOG_FILE.touch(exist_ok=True)


def read_logs() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    with LOCK:
        # Cap memory for long-running demos; never interpret file contents as commands.
        with LOG_FILE.open("r", encoding="utf-8") as fp:
            lines = fp.readlines()[-MAX_EVENTS:]
    entries = []
    for line in lines:
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                entries.append(obj)
        except (ValueError, TypeError):
            continue
    return entries


def append_log(entry: dict):
    with LOCK:
        with LOG_FILE.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
        # Prevent unbounded disk growth without losing recent events.
        if LOG_FILE.stat().st_size > 3 * 1024 * 1024:
            lines = LOG_FILE.read_text(encoding="utf-8").splitlines()[-MAX_EVENTS:]
            LOG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dump_listing():
    result = []
    for p in sorted(DUMPS.glob("demo_dump_*.sql"), key=lambda p: p.stat().st_mtime, reverse=True):
        if p.is_file():
            result.append({"name": p.name, "bytes": p.stat().st_size,
                           "created": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")})
    return result


def generate_dump():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"demo_dump_{stamp}_{secrets.token_hex(3)}.sql"
    content = (f"-- SQL Crack {VERSION} | SIMULATION ONLY\n"
               "-- Completely synthetic educational data; no external DB was queried.\n"
               "CREATE TABLE demo_users (id INTEGER PRIMARY KEY, username VARCHAR(50), role VARCHAR(30));\n"
               "INSERT INTO demo_users (id, username, role) VALUES\n"
               "(1, 'demo_admin', 'example'),\n"
               "(2, 'guest_sample', 'training'),\n"
               "(3, 'local_tester', 'training');\n")
    with LOCK:
        (DUMPS / name).write_text(content, encoding="utf-8")
    return name


def validate_dump_name(name):
    return isinstance(name, str) and re.fullmatch(r"demo_dump_\d{8}_\d{6}_[0-9a-f]{6}\.sql", name) is not None


class Handler(BaseHTTPRequestHandler):
    server_version = "SQLCrack/1.0"
    sys_version = ""

    def log_message(self, fmt, *args):
        # Quiet server: no logging submitted query strings or test input.
        pass

    def _valid_host(self):
        # Deny non-loopback Host headers to reduce DNS rebinding risks.
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        return host in ("127.0.0.1", "localhost", "[::1]")

    def _origin_ok(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        parsed = urlsplit(origin)
        return parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost") and parsed.port == self.server.server_port

    def _send(self, data: bytes, typ: str, status=200, filename=None):
        self.send_response(status)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, obj, status=200):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def _error(self, msg, status=400):
        self._json({"ok": False, "error": msg}, status)

    def do_GET(self):
        if not self._valid_host():
            return self._error("Geçersiz adres", 403)
        parsed = urlsplit(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        if path == "/api/health":
            return self._json({"ok": True, "version": VERSION, "mode": "simulation-only"})
        if path == "/api/state":
            entries = read_logs()
            return self._json({"ok": True, "logs": entries,
                               "total": len(entries), "warnings": sum(x.get("level") == "WARNING" for x in entries),
                               "dumps": dump_listing()})
        if path == "/api/export":
            entries = read_logs()
            fmt = query.get("format", ["json"])[0]
            if fmt == "csv":
                out = io.StringIO(newline="")
                writer = csv.writer(out)
                writer.writerow(["id", "time", "target", "scenario", "level", "result", "input_length"])
                for x in entries:
                    writer.writerow([x.get(k, "") for k in ("id", "time", "target", "scenario", "level", "result", "input_length")])
                return self._send(out.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8", filename="sql-crack-logs.csv")
            if fmt != "json":
                return self._error("Desteklenmeyen format")
            payload = {"app": "SQL Crack", "version": VERSION, "mode": "simulation-only", "events": entries}
            return self._send(json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
                              "application/json; charset=utf-8", filename="sql-crack-logs.json")
        if path == "/api/dump":
            name = query.get("name", [""])[0]
            if not validate_dump_name(name):
                return self._error("Dosya adı geçersiz", 400)
            file = DUMPS / name
            if not file.is_file():
                return self._error("Dosya bulunamadı", 404)
            return self._send(file.read_bytes(), "application/sql; charset=utf-8", filename=name)
        if path in ("/", "/index.html", "/style.css", "/app.js", "/assets/sql-crack-logo.png"):
            local = "index.html" if path == "/" else path.lstrip("/")
            file = ROOT / local
            if not file.is_file():
                return self._error("Dosya bulunamadı", 404)
            typ = mimetypes.guess_type(str(file))[0] or "application/octet-stream"
            if typ.startswith(("text/", "application/javascript")):
                typ += "; charset=utf-8"
            return self._send(file.read_bytes(), typ)
        return self._error("Sayfa bulunamadı", 404)

    def do_POST(self):
        if not self._valid_host() or not self._origin_ok():
            return self._error("Bu istek engellendi", 403)
        path = urlsplit(self.path).path
        if path not in ("/api/run", "/api/clear", "/api/dumps/delete"):
            return self._error("Bilinmeyen işlem", 404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._error("Geçersiz boyut")
        if not 0 <= size <= MAX_BODY:
            return self._error("İstek boyutu geçersiz", 413)
        try:
            obj = json.loads(self.rfile.read(size)) if size else {}
            if not isinstance(obj, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self._error("Geçersiz JSON")
        if path == "/api/clear":
            with LOCK:
                LOG_FILE.write_text("", encoding="utf-8")
            return self._json({"ok": True, "message": "Günlükler temizlendi"})
        if path == "/api/dumps/delete":
            name = obj.get("name")
            if not validate_dump_name(name):
                return self._error("Geçersiz dosya adı")
            with LOCK:
                file = DUMPS / name
                if not file.is_file():
                    return self._error("Dosya bulunamadı", 404)
                file.unlink()
            return self._json({"ok": True, "message": "Örnek dosya silindi"})
        scenario = obj.get("scenario", "")
        target = obj.get("target", "")
        custom = obj.get("input", "")
        if scenario not in SCENARIOS or target not in TARGETS or not isinstance(custom, str) or len(custom) > 200:
            return self._error("Senaryo, hedef veya metin geçersiz")
        label, severity, result = SCENARIOS[scenario]
        flagged = bool(re.search(r"('|--|;|\bunion\b|\bselect\b|\bsleep\s*\()", custom, flags=re.IGNORECASE))
        # Do not store the text (it might include private content); store only its length and flag.
        if flagged and scenario != "dump":
            severity = "WARNING"
            result = "Yerel metin sınıflandırıcısı uyarısı — gerçek açık tespiti değildir."
        name = generate_dump() if scenario == "dump" else None
        event = {"id": secrets.token_hex(6), "time": now(), "target": target,
                 "scenario": label, "scenario_key": scenario, "level": severity,
                 "result": result, "input_length": len(custom), "dump": name}
        append_log(event)
        return self._json({"ok": True, "event": event, "dump": name})


def main():
    setup()
    port = None
    for candidate in range(8000, 8011):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    if port is None:
        print("[HATA] 8000-8010 arası portlar kullanılıyor. CMD penceresinden kontrol edin.")
        return 1
    url = f"http://127.0.0.1:{port}"
    print(f"SQL Crack {VERSION} | TarikPro43391")
    print(f"[OK] Web paneli: {url}")
    print(f"[OK] Günlükler: {LOG_FILE}")
    print(f"[OK] Demo dump klasörü: {DUMPS}")
    print("[INFO] Durdurmak için CTRL+C tuşlarına basın.")
    try:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\n[OK] Sunucu durduruldu.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

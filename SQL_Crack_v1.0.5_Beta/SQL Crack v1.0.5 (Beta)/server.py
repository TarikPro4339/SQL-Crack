#!/usr/bin/env python3
"""SQL Crack v1.0.5 (Beta) — eğitim simülasyonları ve izinli, zararsız HTTP kontrolü.
SQL enjeksiyonu, saldırı yükü veya veritabanı erişimi yoktur.
"""
from __future__ import annotations

import csv
import os
from collections import deque
import io
import json
import mimetypes
import re
import secrets
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from safe_probes import run_safe_probe, ScopeError, rate_limit_snapshot
from insights import build_report, build_safety

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DUMPS = DATA / "dumps"
LOG_FILE = DATA / "events.jsonl"
LOCK = threading.RLock()
VERSION = "v1.0.5 (Beta)"
RELEASE_CHANNEL = "Beta"
DISPLAY_VERSION = VERSION
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
START_MONOTONIC = time.monotonic()
MONITOR_LOCK = threading.Lock()
MONITOR_SAMPLES = deque(maxlen=200)
MONITOR_TOTAL = 0
DENIAL_LOCK = threading.Lock()
RECENT_DENIALS = deque(maxlen=200)


def monitor_snapshot():
    with MONITOR_LOCK:
        sample = list(MONITOR_SAMPLES)
        total = MONITOR_TOTAL
    latency = round(sum(x[1] for x in sample) / len(sample), 1) if sample else None
    return {"online": True, "uptime_seconds": int(time.monotonic() - START_MONOTONIC),
            "requests_total": total, "recent_responses": len(sample),
            "average_local_ms": latency,
            "recent_server_errors": sum(x[0] >= 500 for x in sample),
            "last_status": sample[-1][0] if sample else None}


def record_denial():
    # Store no URL, user input or credentials: only the time of a blocked check.
    with DENIAL_LOCK:
        RECENT_DENIALS.append(time.monotonic())


def denial_count():
    cut = time.monotonic() - 3600
    with DENIAL_LOCK:
        while RECENT_DENIALS and RECENT_DENIALS[0] < cut:
            RECENT_DENIALS.popleft()
        return len(RECENT_DENIALS)


def scope_overview():
    try:
        config = json.loads((ROOT / "scope.json").read_text(encoding="utf-8"))
        values = config.get("approved_urls", [])
        if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
            raise ValueError()
        return {"valid": True, "approved_count": len(values)}
    except (OSError, ValueError, AttributeError, TypeError):
        return {"valid": False, "approved_count": 0}



def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def setup():
    DUMPS.mkdir(parents=True, exist_ok=True)
    LOG_FILE.touch(exist_ok=True)


def read_logs() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    with LOCK:
        # Limit RAM even when the log file is unexpectedly huge.
        with LOG_FILE.open("r", encoding="utf-8", errors="replace") as fp:
            lines = list(deque(fp, maxlen=MAX_EVENTS))
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
        # Atomically replace the old file when it grows; cap memory usage.
        if LOG_FILE.stat().st_size > 3 * 1024 * 1024:
            with LOG_FILE.open("r", encoding="utf-8", errors="replace") as fp:
                lines = deque(fp, maxlen=MAX_EVENTS)
            temp = LOG_FILE.with_suffix(".jsonl.tmp")
            try:
                with temp.open("w", encoding="utf-8") as fp:
                    fp.writelines(lines)
                os.replace(temp, LOG_FILE)
            finally:
                temp.unlink(missing_ok=True)


def dump_listing():
    # A dump can be deleted while the UI is refreshing; that should not crash /api/state.
    result = []
    for path in DUMPS.glob("demo_dump_*.sql"):
        try:
            if not path.is_file() or not validate_dump_name(path.name):
                continue
            stat = path.stat()
        except OSError:
            continue
        result.append({"name": path.name, "bytes": stat.st_size,
                       "created": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                       "_mtime": stat.st_mtime})
    result.sort(key=lambda entry: entry["_mtime"], reverse=True)
    for entry in result:
        entry.pop("_mtime", None)
    return result


def generate_dump():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"demo_dump_{stamp}_{secrets.token_hex(3)}.sql"
    content = (f"-- SQL Crack {DISPLAY_VERSION} | SIMULATION ONLY\n"
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
    server_version = "SQLCrack/v1.0.5 (Beta)"
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
        global MONITOR_TOTAL
        elapsed = round((time.monotonic() - getattr(self, "_request_started", time.monotonic())) * 1000, 1)
        with MONITOR_LOCK:
            MONITOR_TOTAL += 1
            MONITOR_SAMPLES.append((status, elapsed))
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

    def _read_logs_or_error(self):
        """Return a JSON error rather than abruptly closing a client connection."""
        try:
            return read_logs()
        except OSError:
            self._error("Günlükler okunamadı. data klasörü izinlerini kontrol edin.", 500)
            return None

    def do_GET(self):
        self._request_started = time.monotonic()
        if not self._valid_host():
            return self._error("Geçersiz adres", 403)
        parsed = urlsplit(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        if path == "/api/health":
            return self._json({"ok": True, "version": VERSION, "release_channel": RELEASE_CHANNEL, "display_version": DISPLAY_VERSION, "mode": "safe-lab"})
        if path == "/api/monitor":
            return self._json({"ok": True, "monitor": monitor_snapshot()})
        if path == "/api/reports":
            entries = self._read_logs_or_error()
            if entries is None:
                return
            return self._json({"ok": True, "report": build_report(entries)})
        if path == "/api/safety":
            entries = self._read_logs_or_error()
            if entries is None:
                return
            safety = build_safety(entries, denial_count(), rate_limit_snapshot(), scope_overview())
            return self._json({"ok": True, "safety": safety})
        if path == "/api/state":
            entries = self._read_logs_or_error()
            if entries is None:
                return
            return self._json({"ok": True, "logs": entries,
                               "total": len(entries), "warnings": sum(x.get("level") == "WARNING" for x in entries),
                               "dumps": dump_listing()})
        if path == "/api/export":
            entries = self._read_logs_or_error()
            if entries is None:
                return
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
            payload = {"app": "SQL Crack", "version": VERSION, "release_channel": RELEASE_CHANNEL, "display_version": DISPLAY_VERSION, "mode": "simulation-only", "events": entries}
            return self._send(json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
                              "application/json; charset=utf-8", filename="sql-crack-logs.json")
        if path == "/api/dump":
            name = query.get("name", [""])[0]
            if not validate_dump_name(name):
                return self._error("Dosya adı geçersiz", 400)
            file = DUMPS / name
            if not file.is_file():
                return self._error("Dosya bulunamadı", 404)
            try:
                content = file.read_bytes()
            except OSError:
                return self._error("Dosya okunamadı", 500)
            return self._send(content, "application/sql; charset=utf-8", filename=name)
        if path in ("/", "/index.html", "/style.css", "/app.js", "/assets/sql-crack-logo.png"):
            local = "index.html" if path == "/" else path.lstrip("/")
            file = ROOT / local
            if not file.is_file():
                return self._error("Dosya bulunamadı", 404)
            typ = mimetypes.guess_type(str(file))[0] or "application/octet-stream"
            if typ.startswith(("text/", "application/javascript")):
                typ += "; charset=utf-8"
            try:
                content = file.read_bytes()
            except OSError:
                return self._error("Arayüz dosyası okunamadı. Klasör izinlerini kontrol edin.", 500)
            return self._send(content, typ)
        return self._error("Sayfa bulunamadı", 404)

    def do_POST(self):
        self._request_started = time.monotonic()
        if not self._valid_host() or not self._origin_ok():
            return self._error("Bu istek engellendi", 403)
        path = urlsplit(self.path).path
        if path not in ("/api/run", "/api/clear", "/api/dumps/delete", "/api/safe-probe"):
            return self._error("Bilinmeyen işlem", 404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._error("Geçersiz boyut")
        if not 0 <= size <= MAX_BODY:
            return self._error("İstek boyutu geçersiz", 413)
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            return self._error("JSON içerik türü gerekli", 415)
        try:
            obj = json.loads(self.rfile.read(size)) if size else {}
            if not isinstance(obj, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self._error("Geçersiz JSON")
        if path == "/api/safe-probe":
            try:
                report = run_safe_probe(
                    obj.get("url"), obj.get("count"), obj.get("confirmed"),
                    self.server.server_port, ROOT / "scope.json"
                )
            except ScopeError as exc:
                record_denial()
                return self._error(str(exc), 400)
            except Exception:
                # No traceback or exception details exposed in HTTP responses.
                return self._error("Güvenli HTTP kontrolü tamamlanamadı", 502)
            checks = report["checks"]
            successes = sum(isinstance(x.get("status"), int) and 200 <= x["status"] < 400 for x in checks)
            failures = len(checks) - successes
            avg_ms = round(sum(x["ms"] for x in checks) / len(checks), 1)
            # Aggregate-only metrics: do not persist generated params or response contents.
            stats = {"requests": len(checks), "successes": successes, "failures": failures,
                     "avg_ms": avg_ms}
            entry = {"id": secrets.token_hex(6), "time": now(),
                     "target": report["target"], "scenario": "İzinli zararsız HTTP kontrolü",
                     "scenario_key": "safe-probe", "level": "WARNING" if failures else "INFO",
                     "result": f"{len(checks)} güvenli GET · {successes} başarılı · {failures} yanıtsız/hatalı",
                     "input_length": 0, "dump": None, "probe_stats": stats}
            try:
                append_log(entry)
            except OSError:
                return self._error("Kontrol tamamlandı ama log kaydedilemedi", 500)
            return self._json({"ok": True, "report": report, "event": entry})
        if path == "/api/clear":
            try:
                with LOCK:
                    LOG_FILE.write_text("", encoding="utf-8")
            except OSError:
                return self._error("Günlük dosyası temizlenemedi. Klasör izinlerini kontrol edin.", 500)
            return self._json({"ok": True, "message": "Günlükler temizlendi"})
        if path == "/api/dumps/delete":
            name = obj.get("name")
            if not validate_dump_name(name):
                return self._error("Geçersiz dosya adı")
            try:
                with LOCK:
                    file = DUMPS / name
                    if not file.is_file():
                        return self._error("Dosya bulunamadı", 404)
                    file.unlink()
            except OSError:
                return self._error("Örnek dosya silinemedi. Dosya izinlerini kontrol edin.", 500)
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
        try:
            name = generate_dump() if scenario == "dump" else None
        except OSError:
            return self._error("Örnek dosya oluşturulamadı. Klasör izinlerini kontrol edin.", 500)
        event = {"id": secrets.token_hex(6), "time": now(), "target": target,
                 "scenario": label, "scenario_key": scenario, "level": severity,
                 "result": result, "input_length": len(custom), "dump": name}
        try:
            append_log(event)
        except OSError:
            # A failed log write must not leave an untracked synthetic dump behind.
            if name is not None:
                try:
                    (DUMPS / name).unlink(missing_ok=True)
                except OSError:
                    pass
            return self._error("Kayıt dosyasına yazılamadı. Klasör izinlerini kontrol edin.", 500)
        return self._json({"ok": True, "event": event, "dump": name})


def main():
    try:
        setup()
    except OSError as exc:
        print(f"[HATA] Kayıt klasörü hazırlanamadı: {exc}")
        return 1
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
    print(f"SQL Crack {DISPLAY_VERSION} | TarikPro43391")
    print(f"[OK] Web paneli: {url}")
    print(f"[OK] Günlükler: {LOG_FILE}")
    print(f"[OK] Demo dump klasörü: {DUMPS}")
    print("[INFO] Durdurmak için CTRL+C tuşlarına basın.")
    try:
        # Open automatically after socket listen succeeds, without blocking the server.
        timer = threading.Timer(0.7, lambda: webbrowser.open(url))
        timer.daemon = True
        timer.start()
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\n[OK] Sunucu durduruldu.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Dar kapsamlı, zararsız GET kontrolleri. SQL payload, kimlik bilgisi veya içerik toplama yok."""
from __future__ import annotations

import http.client
from collections import deque
import threading
import ipaddress
import json
import secrets
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlencode

MAX_CHECKS = 3
MAX_CHECKS_PER_MINUTE = 6
DELAY_SECONDS = 0.8
_USAGE = deque()
_USAGE_LOCK = threading.Lock()

class ScopeError(ValueError):
    pass

class DenyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate(url, count, confirmed, server_port, scope_file: Path) -> str:
    if confirmed is not True:
        raise ScopeError("İzin onayı gerekli")
    if type(count) is not int or not 1 <= count <= MAX_CHECKS:
        raise ScopeError("Kontrol sayısı 1-3 arasında olmalı")
    if not isinstance(url, str) or len(url) > 350 or url != url.strip():
        raise ScopeError("Geçerli ve kısa bir URL girin")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        raise ScopeError("Geçersiz URL") from None
    if (parsed.username or parsed.password or parsed.query or parsed.fragment or
        not parsed.hostname or not parsed.path.startswith('/')):
        raise ScopeError("URL kimlik bilgisi, sorgu parametresi veya fragment içeremez")

    self_url = f"http://127.0.0.1:{server_port}/api/health"
    if url == self_url:
        return url

    # Explicit exact URL allowlist is required for all other URLs.
    try:
        config = json.loads(scope_file.read_text(encoding="utf-8"))
        approved = config.get("approved_urls", [])
        if not isinstance(approved, list) or any(not isinstance(s, str) for s in approved):
            raise ValueError()
    except (OSError, ValueError, AttributeError):
        raise ScopeError("scope.json dosyası okunamadı veya geçersiz") from None
    if url not in approved:
        raise ScopeError("Hedef scope.json izin listesinde değil")
    if parsed.scheme != 'https' or port not in (None,443):
        raise ScopeError("Harici izinli adresler yalnızca HTTPS 443 kullanabilir")
    # Block private, loopback, link-local, multicast and reserved resolved addresses.
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or not all(ipaddress.ip_address(addr[4][0]).is_global for addr in addresses):
            raise ScopeError("Harici adres genel erişimli bir IP olmalı")
    except (socket.gaierror, ValueError):
        raise ScopeError("Hedef DNS çözümlemesi başarısız") from None
    return url


def run_safe_probe(url, count, confirmed, port, scope_file: Path):
    url = validate(url, count, confirmed, port, scope_file)
    # Global cap prevents repeated API calls from turning benign requests into a load test.
    with _USAGE_LOCK:
        timestamp = time.monotonic()
        while _USAGE and _USAGE[0] < timestamp - 60:
            _USAGE.popleft()
        if len(_USAGE) + count > MAX_CHECKS_PER_MINUTE:
            raise ScopeError("Hız sınırı: Dakikada en fazla 6 kontrol. Lütfen sonra tekrar dene")
        _USAGE.extend([timestamp] * count)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), DenyRedirect()
    )
    checks = []
    for i in range(count):
        if i:
            time.sleep(DELAY_SECONDS)
        param = 'sc_' + secrets.token_hex(4)
        value = 'demo_' + secrets.token_hex(6)
        full_url = url + '?' + urlencode({param: value})
        request = urllib.request.Request(full_url, headers={
            'User-Agent': 'SQL-Crack-SafeCheck/v1.0.5 (Beta)',
            'Accept': '*/*'
        }, method='GET')
        started = time.monotonic()
        status = None
        try:
            with opener.open(request, timeout=3) as res:
                status = res.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            exc.close()
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
            pass
        elapsed = round((time.monotonic() - started)*1000)
        checks.append({'param':param, 'status':status, 'ms':elapsed,
                       'note': 'Yanıt alınamadı' if status is None else 'HTTP durum kodu gözlemlendi'})
    return {'target':url, 'checks':checks,
            'note':'Zararsız rastgele değerler kullanıldı; yanıt içeriği okunmadı, SQL enjeksiyonu denenmedi.'}


def rate_limit_snapshot():
    """Read the existing rate limiter state without sending any network requests."""
    with _USAGE_LOCK:
        now = time.monotonic()
        while _USAGE and _USAGE[0] < now - 60:
            _USAGE.popleft()
        used = len(_USAGE)
    return {"used": used, "remaining": max(0, MAX_CHECKS_PER_MINUTE - used),
            "limit_per_minute": MAX_CHECKS_PER_MINUTE, "max_per_run": MAX_CHECKS}

"""Read-only, defensive reporting for SQL Crack v1.0.5 (Beta)."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timedelta, timezone
import math


def parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def safe_int(value, maximum=100000):
    """Ignore unexpected/malformed historical fields instead of breaking the UI."""
    if isinstance(value, bool):
        return 0
    try:
        n = int(value)
    except (TypeError, ValueError, OverflowError):
        return 0
    return n if 0 <= n <= maximum else 0


def safe_ms(value):
    try:
        n = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return n if math.isfinite(n) and 0 <= n <= 60000 else 0.0


def summarise(entries):
    probes = [e.get("probe_stats") for e in entries if e.get("scenario_key") == "safe-probe"]
    checks = successes = failures = 0
    weighted_ms = 0.0
    for item in probes:
        if not isinstance(item, dict):
            continue
        reqs = safe_int(item.get("requests"))
        ok = min(reqs, safe_int(item.get("successes")))
        bad = min(reqs - ok, safe_int(item.get("failures")))
        checks += reqs
        successes += ok
        failures += bad
        weighted_ms += safe_ms(item.get("avg_ms")) * reqs
    return {"events": len(entries), "warnings": sum(e.get("level") == "WARNING" for e in entries),
            "checks": checks, "successful_checks": successes, "failed_checks": failures,
            "success_percent": round(100 * successes / checks, 1) if checks else None,
            "avg_probe_ms": round(weighted_ms / checks, 1) if checks else None}


def build_report(logs, at=None):
    at = at or datetime.now(timezone.utc)
    prior_start = at - timedelta(hours=48)
    curr_start = at - timedelta(hours=24)
    current, previous = [], []
    for entry in logs:
        if not isinstance(entry, dict):
            continue
        moment = parse_time(entry.get("time"))
        if moment is None or moment > at:
            continue
        if moment >= curr_start:
            current.append(entry)
        elif moment >= prior_start:
            previous.append(entry)
    curr, prev = summarise(current), summarise(previous)
    breakdown = Counter()
    for entry in current:
        label = entry.get("scenario", "Bilinmiyor")
        breakdown[label[:80] if isinstance(label, str) else "Bilinmiyor"] += 1
    return {"window_hours": 24, "current": curr, "previous": prev,
            "event_delta": curr["events"] - prev["events"],
            "top_scenarios": [{"name": name, "events": count} for name, count in breakdown.most_common(5)],
            "note": "Son 24 saat önceki 24 saatle karşılaştırılır. Eski kontrol günlüklerinde yanıt süresi bulunmayabilir."}


def build_safety(logs, denied_last_hour, limiter, scope):
    recent_probes = [e for e in reversed(logs) if isinstance(e, dict) and e.get("scenario_key") == "safe-probe"]
    consecutive_failed = 0
    for event in recent_probes:
        stats = event.get("probe_stats")
        if not isinstance(stats, dict):
            break
        if safe_int(stats.get("requests")) and safe_int(stats.get("successes")) == 0:
            consecutive_failed += 1
        else:
            break
    alerts = []
    if not scope["valid"]:
        alerts.append("scope.json geçersiz veya okunamıyor; izin listesini kontrol et.")
    if denied_last_hour:
        alerts.append(f"Son 60 dakikada {denied_last_hour} kapsam/limit denemesi engellendi.")
    if limiter["remaining"] == 0:
        alerts.append("Dakikalık istek limiti doldu; yeni kontrol geçici olarak engellenir.")
    if consecutive_failed >= 2:
        alerts.append("Arka arkaya en az iki izinli HTTP kontrolü başarısız oldu.")
    return {"status": "UYARI" if alerts else "KORUNUYOR", "alerts": alerts,
            "scope_valid": scope["valid"], "approved_urls": scope["approved_count"],
            "blocked_last_hour": denied_last_hour,
            "consecutive_failed_probes": consecutive_failed,
            "rate_limit": limiter,
            "note": "İzin ve kapsam kontrolü saldırı yetkisi vermez; yalnızca onaylanan zararsız kontrolleri sınırlar."}

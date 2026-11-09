#!/usr/bin/env python3
"""SQL Crack v1.0.5 (Beta) cinematic launcher (visual simulation only)."""
from __future__ import annotations

import argparse
import ctypes
import os
from pathlib import Path
import random
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parent
BANNER = [
    r"  ____   ___  _        ____ ____      _    ____ _  __",
    r" / ___| / _ \| |      / ___|  _ \    / \  / ___| |/ /",
    r" \___ \| | | | |     | |   | |_) |  / _ \| |   | ' / ",
    r"  ___) | |_| | |___  | |___|  _ <  / ___ \ |___| . \ ",
    ' |____/ \\__\\_\\_____|  \\____|_| \\_\\/_/   \\_\\____|_|\\_\\',
]

# Visual-only cinematic text, not real SQL operations.
STEPS = [
    "boot --module=sql-crack --profile=simulation",
    "verify --operator=tarikpro43391 --signature=local-demo",
    "mount --target=training-lab --mode=offline",
    "scan --scenario=sql-input-demo --network=disabled",
    "compile --visual-payload=simulation-only",
    "initialize --event-logs --example-dumps",
]


def supports_ansi() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.name != 'nt':
        return True
    try:
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError):
        return False


def paint(text: str, color: str, ansi: bool) -> str:
    return f"\x1b[{color}m{text}\x1b[0m" if ansi else text


def type_line(text: str, delay: float, *, color='96', ansi=False):
    if ansi:
        sys.stdout.write(f'\x1b[{color}m')
    for letter in text:
        sys.stdout.write(letter)
        sys.stdout.flush()
        if delay:
            time.sleep(delay * (1.65 if letter in ':.=' else 1.0))
    sys.stdout.write('\x1b[0m\n' if ansi else '\n')
    sys.stdout.flush()


def matrix_rain(ansi: bool, fast: bool):
    """Small matrix animation inside the existing CMD window; no external packages."""
    columns, rows = shutil.get_terminal_size((90, 28))
    width = max(30, min(columns - 1, 110))
    height = max(8, min(rows - 4, 20))
    frames = 3 if fast else 38
    fps = 0 if fast else 0.060
    alphabet = '0123456789ABCDEF#$+<>{}[]'
    rng = random.Random(43391)
    if not ansi:
        # Readable fallback for older terminals and redirected output.
        type_line('>>> MATRIX VISUAL SEQUENCE // SIMULATION ONLY', 0 if fast else .008)
        for _ in range(2 if fast else 5):
            text = ''.join(rng.choice(alphabet) for _ in range(44))
            type_line('    '+text, 0 if fast else .002)
        return
    heads = [rng.randrange(-height, 1) for _ in range(width)]
    speed = [rng.choice((1,1,2,2,3)) for _ in range(width)]
    sys.stdout.write('\x1b[2J\x1b[H\x1b[?25l')
    try:
        for frame in range(frames):
            buf = ['\x1b[H']
            for y in range(height):
                row=[]
                for x in range(width):
                    distance = heads[x] - y
                    if 0 <= distance <= 7:
                        code = '97' if distance == 0 else '92' if distance < 3 else '32' if distance < 6 else '2;32'
                        row.append(f'\x1b[{code}m{rng.choice(alphabet)}')
                    else:
                        row.append(' ')
                buf.append(''.join(row) + '\x1b[0m\n')
            footer='SQL CRACK  //  MATRIX BOOT  //  v1.0.5 (Beta)  //  SIMULATION ONLY'
            buf.append('\x1b[96m'+footer.center(width)[:width]+'\x1b[0m')
            sys.stdout.write(''.join(buf))
            sys.stdout.flush()
            if fps: time.sleep(fps)
            for x in range(width):
                if frame % speed[x] == 0:
                    heads[x] += 1
                if heads[x] - 7 > height:
                    heads[x] = rng.randrange(-height // 2, 0)
    finally:
        sys.stdout.write('\x1b[0m\x1b[?25h\x1b[2J\x1b[H')
        sys.stdout.flush()


def intro(*, fast=False, no_animation=False):
    ansi = supports_ansi() and not no_animation
    if os.name == 'nt':
        os.system('title SQL CRACK v1.0.5 (Beta)')
    if not no_animation:
        matrix_rain(ansi, fast)
    print()
    for line in BANNER:
        type_line('  '+line, 0 if fast else .0025, color='96', ansi=ansi)
    type_line('SQL CRACK', 0 if fast else .035, color='92', ansi=ansi)
    print(paint('=' * 73, '36', ansi))
    type_line('[+] DEVELOPER / CREATOR : tarikpro43391', 0 if fast else .012, ansi=ansi)
    type_line('[+] ENGINE VERSION      : v1.0.5 (Beta) [BETA-BUILD]', 0 if fast else .012, ansi=ansi)
    type_line('[+] TARGET DATABASE     : [SIMULATION / NO CONNECTION]', 0 if fast else .009, ansi=ansi)
    type_line('[+] ACCESS CLEARANCE    : DEMO_MODE // LOCAL_ONLY', 0 if fast else .009, ansi=ansi)
    print(paint('=' * 73, '36', ansi))
    print()
    for command in STEPS:
        type_line('C:\\SQL_CRACK> '+command, 0 if fast else .017, color='92', ansi=ansi)
        type_line('     [OK] Simulated sequence completed.', 0 if fast else .004, color='90', ansi=ansi)
        if not fast: time.sleep(.19)
    print()
    print(paint('-'*73, '36', ansi))
    type_line('   "CODE WRITTEN IN THE DARK. POWER UNLOCKED BY tarikpro43391."', 0 if fast else .007, ansi=ansi)
    print(paint('-'*73, '36', ansi))
    type_line('[>>>] ACCESS GRANTED (DEMO). STARTING LOCAL WEB PANEL...', 0 if fast else .015, color='92', ansi=ansi)
    print(paint('[INFO] Visual effects only. No SQL attack, WAF bypass or data extraction.', '90', ansi))
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(description='SQL Crack v1.0.5 (Beta) launcher')
    parser.add_argument('--fast', action='store_true', help='Skip intro delays (for testing)')
    parser.add_argument('--no-animation', action='store_true', help='No matrix or animation')
    parser.add_argument('--intro-only', action='store_true', help='Show introduction and exit')
    args = parser.parse_args(argv)
    os.chdir(ROOT)
    required = ('server.py','safe_probes.py','scope.json','index.html','app.js','style.css','assets/sql-crack-logo.png')
    missing = [x for x in required if not (ROOT/x).is_file()]
    if missing:
        print('[HATA] Eksik proje dosyalari: '+', '.join(missing))
        print('ZIP dosyasini tamamen cikarin ve Start.py dosyasini proje klasorunden calistirin.')
        return 1
    if sys.version_info < (3, 9):
        print('[HATA] Python 3.9 veya daha yeni bir surum gerekiyor.')
        return 1
    try:
        # --no-animation is a genuinely immediate, accessible text-only launch.
        intro(fast=args.fast or args.no_animation, no_animation=args.no_animation)
        if args.intro_only:
            return 0
        from server import main as start_server
        return start_server()
    except KeyboardInterrupt:
        print('\n[INFO] Baslatma iptal edildi.')
        return 0
    except Exception as exc:
        print(f'\n[HATA] Baslatilamadi: {exc}')
        return 1

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Использование: python get-keys.py qbittorrent.json")
    sys.exit(1)

file = Path(__file__).parent / "keys" / sys.argv[1]

if not file.exists():
    print(f"Файл {sys.argv[1]} не найден")
    sys.exit(1)

data = json.loads(file.read_text())
print("Доступные поля:", ", ".join(data.keys()))

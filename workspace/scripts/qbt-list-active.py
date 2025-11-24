#!/usr/bin/env python3
"""
Скрипт для получения списка активных (скачивающихся) торрентов в qBittorrent
Использование: python qbt-list-active.py
"""

import json
import requests
from pathlib import Path

def load_credentials():
    """Загрузка credentials из keys/qbittorrent.json"""
    keys_file = Path(__file__).parent.parent / "keys" / "qbittorrent.json"
    with open(keys_file, 'r') as f:
        return json.load(f)

def format_size(bytes_size):
    """Форматирование размера в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def format_speed(bytes_per_sec):
    """Форматирование скорости"""
    return format_size(bytes_per_sec) + "/s"

def list_active_torrents():
    """Получение списка активных торрентов"""
    creds = load_credentials()

    # Формируем базовый URL
    base_url = f"http://{creds['host']}:{creds['port']}"

    # Создаём сессию для сохранения cookies
    session = requests.Session()

    # Авторизация
    login_url = f"{base_url}/api/v2/auth/login"
    login_data = {
        'username': creds['username'],
        'password': creds['password']
    }

    login_response = session.post(login_url, data=login_data)
    if login_response.text != "Ok.":
        print(f"❌ Ошибка авторизации: {login_response.text}")
        return

    # Получаем список торрентов с фильтром "downloading"
    info_url = f"{base_url}/api/v2/torrents/info"
    params = {
        'filter': 'downloading'  # Только скачивающиеся
    }

    response = session.get(info_url, params=params)
    torrents = response.json()

    if not torrents:
        print("📭 Нет активных загрузок")
        return

    print(f"📥 Активные загрузки ({len(torrents)}):\n")

    for i, torrent in enumerate(torrents, 1):
        name = torrent.get('name', 'Без названия')
        hash_id = torrent.get('hash', 'unknown')
        progress = torrent.get('progress', 0) * 100
        size = format_size(torrent.get('size', 0))
        downloaded = format_size(torrent.get('downloaded', 0))
        dlspeed = format_speed(torrent.get('dlspeed', 0))
        eta = torrent.get('eta', 0)
        category = torrent.get('category', 'Без категории')
        state = torrent.get('state', 'unknown')

        # Форматируем ETA
        if eta == 8640000:  # Infinity
            eta_str = "∞"
        elif eta > 0:
            hours = eta // 3600
            minutes = (eta % 3600) // 60
            if hours > 0:
                eta_str = f"{hours}ч {minutes}м"
            else:
                eta_str = f"{minutes}м"
        else:
            eta_str = "—"

        print(f"{i}. 📁 {name}")
        print(f"   🆔 ID: {hash_id}")
        print(f"   📊 Прогресс: {progress:.1f}% ({downloaded} / {size})")
        print(f"   ⬇️  Скорость: {dlspeed}")
        print(f"   ⏱️  Осталось: {eta_str}")
        print(f"   🏷️  Категория: {category}")
        print(f"   📍 Статус: {state}")
        print()

if __name__ == "__main__":
    list_active_torrents()

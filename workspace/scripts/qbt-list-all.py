#!/usr/bin/env python3
"""
Скрипт для получения списка ВСЕХ торрентов в qBittorrent с возможностью поиска
Использование:
  python qbt-list-all.py                    - показать все торренты
  python qbt-list-all.py "название"         - поиск по названию
"""

import sys
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

def get_state_emoji(state):
    """Получить эмодзи для статуса"""
    state_map = {
        'downloading': '⬇️',
        'uploading': '⬆️',
        'pausedDL': '⏸️',
        'pausedUP': '⏸️',
        'queuedDL': '⏳',
        'queuedUP': '⏳',
        'stalledDL': '🔄',
        'stalledUP': '🔄',
        'checkingDL': '🔍',
        'checkingUP': '🔍',
        'checkingResumeData': '🔍',
        'error': '❌',
        'missingFiles': '⚠️',
        'allocating': '💾',
    }
    return state_map.get(state, '❓')

def get_state_name(state):
    """Получить название статуса на русском"""
    state_names = {
        'downloading': 'Скачивается',
        'uploading': 'Раздаётся',
        'pausedDL': 'Приостановлено',
        'pausedUP': 'Приостановлено',
        'queuedDL': 'В очереди',
        'queuedUP': 'В очереди',
        'stalledDL': 'Ожидание',
        'stalledUP': 'Ожидание',
        'checkingDL': 'Проверка',
        'checkingUP': 'Проверка',
        'checkingResumeData': 'Проверка данных',
        'error': 'Ошибка',
        'missingFiles': 'Файлы не найдены',
        'allocating': 'Выделение места',
    }
    return state_names.get(state, state)

def list_all_torrents(search_query=None):
    """Получение списка всех торрентов с возможностью поиска"""
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

    # Получаем список всех торрентов
    info_url = f"{base_url}/api/v2/torrents/info"

    response = session.get(info_url)
    torrents = response.json()

    # Фильтруем по поисковому запросу если указан
    if search_query:
        search_lower = search_query.lower()
        torrents = [t for t in torrents if search_lower in t.get('name', '').lower()]

    if not torrents:
        if search_query:
            print(f"🔍 Торренты с названием '{search_query}' не найдены")
        else:
            print("📭 Нет торрентов")
        return

    # Заголовок
    if search_query:
        print(f"🔍 Найдено торрентов: {len(torrents)} (поиск: '{search_query}')\n")
    else:
        print(f"📚 Всего торрентов: {len(torrents)}\n")

    # Группируем по категориям
    by_category = {}
    for torrent in torrents:
        category = torrent.get('category', 'Без категории') or 'Без категории'
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(torrent)

    # Выводим по категориям
    for category, cat_torrents in sorted(by_category.items()):
        print(f"📁 {category} ({len(cat_torrents)}):")
        print("─" * 60)

        for torrent in cat_torrents:
            name = torrent.get('name', 'Без названия')
            hash_id = torrent.get('hash', 'unknown')
            progress = torrent.get('progress', 0) * 100
            size = format_size(torrent.get('size', 0))
            state = torrent.get('state', 'unknown')
            state_emoji = get_state_emoji(state)
            state_name = get_state_name(state)
            added_on = torrent.get('added_on', 0)
            completed_on = torrent.get('completion_on', 0)

            # Дата добавления
            from datetime import datetime
            if added_on > 0:
                added_date = datetime.fromtimestamp(added_on).strftime('%d.%m.%Y')
            else:
                added_date = "—"

            print(f"  {state_emoji} {name}")
            print(f"     🆔 ID: {hash_id}")
            print(f"     Прогресс: {progress:.1f}% | Размер: {size}")
            print(f"     Статус: {state_name} | Добавлен: {added_date}")
            print()

        print()

if __name__ == "__main__":
    search_query = sys.argv[1] if len(sys.argv) > 1 else None
    list_all_torrents(search_query)

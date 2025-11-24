#!/usr/bin/env python3
"""
Скрипт для добавления торрента в qBittorrent
Использование: python qbt-add-torrent.py "Название" "magnet:..." "Movies|TV Shows"
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

def add_torrent(name, magnet_link, category):
    """Добавление торрента в qBittorrent"""
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
        return False

    # Добавляем торрент
    add_url = f"{base_url}/api/v2/torrents/add"
    add_data = {
        'urls': magnet_link,
        'category': category,
        'rename': name,
        'paused': 'false'  # Автоматически начать скачивание
    }

    add_response = session.post(add_url, data=add_data)

    if add_response.text == "Ok.":
        print(f"✅ Торрент '{name}' успешно добавлен в категорию '{category}'")
        print(f"🔗 Magnet: {magnet_link[:60]}...")
        return True
    else:
        print(f"❌ Ошибка добавления торрента: {add_response.text}")
        return False

def main():
    if len(sys.argv) != 4:
        print("Использование: python qbt-add-torrent.py \"Название\" \"magnet:...\" \"Movies|TV Shows\"")
        print("\nКатегории:")
        print("  Movies    - фильмы")
        print("  TV Shows  - сериалы")
        sys.exit(1)

    name = sys.argv[1]
    magnet_link = sys.argv[2]
    category = sys.argv[3]

    # Проверка категории
    valid_categories = ["Movies", "TV Shows"]
    if category not in valid_categories:
        print(f"❌ Неверная категория: {category}")
        print(f"Доступные категории: {', '.join(valid_categories)}")
        sys.exit(1)

    # Проверка magnet ссылки
    if not magnet_link.startswith("magnet:"):
        print("❌ Ошибка: это не magnet ссылка")
        sys.exit(1)

    add_torrent(name, magnet_link, category)

if __name__ == "__main__":
    main()

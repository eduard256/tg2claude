#!/usr/bin/env python3
"""
Скрипт для запуска видео на Apple TV через Jellyfin Sessions API
"""
import sys
import json
import requests

# Загружаем конфигурацию
with open('keys/jellyfin.json', 'r') as f:
    config = json.load(f)

JELLYFIN_URL = config['url']
API_KEY = config['api_key']

def get_appletv_session():
    """Получает ID сессии Apple TV"""
    url = f"{JELLYFIN_URL}/Sessions?api_key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    sessions = response.json()

    for session in sessions:
        if session.get('DeviceName') == 'AppleTV' and session.get('Client') == 'Jellyfin tvOS':
            return session['Id']

    return None

def play_video(session_id, item_id):
    """Отправляет команду воспроизведения видео"""
    url = f"{JELLYFIN_URL}/Sessions/{session_id}/Playing"
    params = {
        'itemIds': item_id,
        'playCommand': 'PlayNow'
    }
    headers = {
        'X-Emby-Token': API_KEY
    }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 204:
        print(f"✅ Команда воспроизведения отправлена успешно")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)
        return False

def main():
    if len(sys.argv) < 2:
        print("Использование: python3 jellyfin-play-video.py <название_фильма>")
        print("Пример: python3 jellyfin-play-video.py Бремя")
        sys.exit(1)

    search_query = sys.argv[1]

    # Получаем сессию
    print("🔍 Поиск сессии Apple TV...")
    session_id = get_appletv_session()

    if not session_id:
        print("❌ Активная сессия Apple TV не найдена. Запустите Jellyfin на Apple TV.")
        sys.exit(1)

    print(f"✅ Найдена сессия: {session_id}")

    # Ищем фильм
    print(f"🔍 Поиск фильма '{search_query}'...")
    search_url = f"{JELLYFIN_URL}/Items?searchTerm={search_query}&Recursive=true&IncludeItemTypes=Movie&api_key={API_KEY}"
    response = requests.get(search_url)
    response.raise_for_status()
    results = response.json()

    if results['TotalRecordCount'] == 0:
        print(f"❌ Фильм '{search_query}' не найден")
        sys.exit(1)

    item = results['Items'][0]
    item_id = item['Id']
    item_name = item['Name']
    item_year = item.get('ProductionYear', '')

    print(f"✅ Найден: {item_name} ({item_year})")
    print(f"📺 Запуск на Apple TV...")

    # Запускаем видео
    play_video(session_id, item_id)

if __name__ == "__main__":
    main()

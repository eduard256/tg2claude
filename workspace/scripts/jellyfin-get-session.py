#!/usr/bin/env python3
"""
Скрипт для получения активной сессии Jellyfin на Apple TV
"""
import sys
import json
import requests

# Загружаем конфигурацию
with open('keys/jellyfin.json', 'r') as f:
    config = json.load(f)

JELLYFIN_URL = config['url']
API_KEY = config['api_key']

def get_sessions():
    """Получает все активные сессии"""
    url = f"{JELLYFIN_URL}/Sessions?api_key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_appletv_session():
    """Находит активную сессию Apple TV"""
    sessions = get_sessions()

    for session in sessions:
        if session.get('DeviceName') == 'AppleTV' and session.get('Client') == 'Jellyfin tvOS':
            return session

    return None

def main():
    session = get_appletv_session()

    if session:
        print(f"✅ Найдена активная сессия Apple TV")
        print(f"ID сессии: {session['Id']}")
        print(f"Пользователь: {session.get('UserName', 'N/A')}")
        print(f"Клиент: {session['Client']}")
        print(f"Версия: {session.get('ApplicationVersion', 'N/A')}")
        print(f"Активна: {session['IsActive']}")
        print(f"Поддержка управления медиа: {session.get('SupportsMediaControl', False)}")

        # Сохраняем ID сессии для использования в других скриптах
        with open('/tmp/jellyfin_session_id.txt', 'w') as f:
            f.write(session['Id'])

        return session['Id']
    else:
        print("❌ Активная сессия Apple TV не найдена")
        print("\nВсе доступные сессии:")
        sessions = get_sessions()
        for s in sessions:
            print(f"  - {s.get('DeviceName', 'Unknown')} ({s.get('Client', 'Unknown')})")
        return None

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Универсальный скрипт для управления торрентами в qBittorrent
Использование:
  python qbt-control.py pause <hash>      - поставить на паузу
  python qbt-control.py resume <hash>     - продолжить загрузку
  python qbt-control.py delete <hash>     - удалить торрент (без файлов)
  python qbt-control.py delete-full <hash> - удалить торрент с файлами
  python qbt-control.py recheck <hash>    - перепроверить торрент
  python qbt-control.py reannounce <hash> - переподключиться к трекерам

Где <hash> - это ID торрента (hash), который можно получить из qbt-list-active.py или qbt-list-all.py
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

def get_session():
    """Создание авторизованной сессии"""
    creds = load_credentials()
    base_url = f"http://{creds['host']}:{creds['port']}"

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
        return None, None

    return session, base_url

def get_torrent_name(session, base_url, hash_id):
    """Получить название торрента по hash"""
    info_url = f"{base_url}/api/v2/torrents/info"
    params = {'hashes': hash_id}
    response = session.get(info_url, params=params)
    torrents = response.json()

    if torrents and len(torrents) > 0:
        return torrents[0].get('name', 'Неизвестный торрент')
    return None

def pause_torrent(hash_id):
    """Поставить торрент на паузу"""
    session, base_url = get_session()
    if not session:
        return False

    name = get_torrent_name(session, base_url, hash_id)
    if not name:
        print(f"❌ Торрент с ID {hash_id} не найден")
        return False

    url = f"{base_url}/api/v2/torrents/pause"
    data = {'hashes': hash_id}
    response = session.post(url, data=data)

    if response.text == "Ok." or response.status_code == 200:
        print(f"⏸️  Торрент '{name}' поставлен на паузу")
        return True
    else:
        print(f"❌ Ошибка при постановке на паузу: {response.text}")
        return False

def resume_torrent(hash_id):
    """Продолжить загрузку торрента"""
    session, base_url = get_session()
    if not session:
        return False

    name = get_torrent_name(session, base_url, hash_id)
    if not name:
        print(f"❌ Торрент с ID {hash_id} не найден")
        return False

    url = f"{base_url}/api/v2/torrents/resume"
    data = {'hashes': hash_id}
    response = session.post(url, data=data)

    if response.text == "Ok." or response.status_code == 200:
        print(f"▶️  Торрент '{name}' продолжает загрузку")
        return True
    else:
        print(f"❌ Ошибка при возобновлении: {response.text}")
        return False

def delete_torrent(hash_id, delete_files=False):
    """Удалить торрент"""
    session, base_url = get_session()
    if not session:
        return False

    name = get_torrent_name(session, base_url, hash_id)
    if not name:
        print(f"❌ Торрент с ID {hash_id} не найден")
        return False

    url = f"{base_url}/api/v2/torrents/delete"
    data = {
        'hashes': hash_id,
        'deleteFiles': 'true' if delete_files else 'false'
    }
    response = session.post(url, data=data)

    if response.text == "Ok." or response.status_code == 200:
        if delete_files:
            print(f"🗑️  Торрент '{name}' удалён вместе с файлами")
        else:
            print(f"🗑️  Торрент '{name}' удалён (файлы сохранены)")
        return True
    else:
        print(f"❌ Ошибка при удалении: {response.text}")
        return False

def recheck_torrent(hash_id):
    """Перепроверить торрент"""
    session, base_url = get_session()
    if not session:
        return False

    name = get_torrent_name(session, base_url, hash_id)
    if not name:
        print(f"❌ Торрент с ID {hash_id} не найден")
        return False

    url = f"{base_url}/api/v2/torrents/recheck"
    data = {'hashes': hash_id}
    response = session.post(url, data=data)

    if response.text == "Ok." or response.status_code == 200:
        print(f"🔍 Торрент '{name}' начал перепроверку")
        return True
    else:
        print(f"❌ Ошибка при перепроверке: {response.text}")
        return False

def reannounce_torrent(hash_id):
    """Переподключиться к трекерам"""
    session, base_url = get_session()
    if not session:
        return False

    name = get_torrent_name(session, base_url, hash_id)
    if not name:
        print(f"❌ Торрент с ID {hash_id} не найден")
        return False

    url = f"{base_url}/api/v2/torrents/reannounce"
    data = {'hashes': hash_id}
    response = session.post(url, data=data)

    if response.text == "Ok." or response.status_code == 200:
        print(f"📡 Торрент '{name}' переподключается к трекерам")
        return True
    else:
        print(f"❌ Ошибка при переподключении: {response.text}")
        return False

def print_usage():
    """Вывести справку по использованию"""
    print("Использование: python qbt-control.py <действие> <hash>")
    print("\nДоступные действия:")
    print("  pause        - поставить на паузу")
    print("  resume       - продолжить загрузку")
    print("  delete       - удалить торрент (файлы остаются)")
    print("  delete-full  - удалить торрент с файлами")
    print("  recheck      - перепроверить файлы торрента")
    print("  reannounce   - переподключиться к трекерам")
    print("\nПример:")
    print("  python qbt-control.py pause 28a2695396c7cc02193c0927336f8877c3a5b4fa")
    print("  python qbt-control.py delete-full 28a2695396c7cc02193c0927336f8877c3a5b4fa")

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    action = sys.argv[1].lower()
    hash_id = sys.argv[2].lower()

    actions = {
        'pause': pause_torrent,
        'resume': resume_torrent,
        'delete': lambda h: delete_torrent(h, delete_files=False),
        'delete-full': lambda h: delete_torrent(h, delete_files=True),
        'recheck': recheck_torrent,
        'reannounce': reannounce_torrent,
    }

    if action not in actions:
        print(f"❌ Неизвестное действие: {action}")
        print_usage()
        sys.exit(1)

    # Выполняем действие
    success = actions[action](hash_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

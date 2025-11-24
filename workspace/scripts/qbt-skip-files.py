#!/usr/bin/env python3
"""
Скрипт для исключения файлов из загрузки (установка priority=0)
Использование: python qbt-skip-files.py <hash> <ID файлов>

Примеры:
  python qbt-skip-files.py <hash> 0,1,2       - исключить файлы 0, 1, 2
  python qbt-skip-files.py <hash> 5-10        - исключить файлы с 5 по 10
  python qbt-skip-files.py <hash> 0,3,5-8,12  - комбинированный вариант
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

def parse_file_ids(ids_string):
    """Парсинг строки с ID файлов
    Примеры:
      "0,1,2" -> [0, 1, 2]
      "5-10" -> [5, 6, 7, 8, 9, 10]
      "0,3,5-8,12" -> [0, 3, 5, 6, 7, 8, 12]
    """
    result = []
    parts = ids_string.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # Диапазон
            start, end = part.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            # Одиночный ID
            result.append(int(part))

    return sorted(list(set(result)))  # Убираем дубликаты и сортируем

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

def get_torrent_files(session, base_url, hash_id):
    """Получить список файлов торрента"""
    files_url = f"{base_url}/api/v2/torrents/files"
    params = {'hash': hash_id}
    response = session.get(files_url, params=params)

    if response.status_code != 200:
        return None

    return response.json()

def set_file_priority(session, base_url, hash_id, file_ids, priority):
    """Установить приоритет для файлов
    priority: 0 = не качать, 1 = нормальный, 6 = высокий, 7 = максимальный
    """
    url = f"{base_url}/api/v2/torrents/filePrio"
    data = {
        'hash': hash_id,
        'id': '|'.join(map(str, file_ids)),
        'priority': priority
    }

    response = session.post(url, data=data)
    return response.status_code == 200 or response.text == "Ok."

def skip_files(hash_id, ids_string):
    """Исключить файлы из загрузки"""
    session, base_url = get_session()
    if not session:
        return False

    # Парсим ID
    try:
        file_ids = parse_file_ids(ids_string)
    except Exception as e:
        print(f"❌ Ошибка при парсинге ID: {e}")
        print("Используйте формат: 0,1,2 или 5-10 или 0,3,5-8,12")
        return False

    # Получаем список файлов
    files = get_torrent_files(session, base_url, hash_id)
    if files is None:
        print(f"❌ Не удалось получить список файлов для торрента {hash_id}")
        return False

    # Проверяем что все ID существуют
    max_index = len(files) - 1
    invalid_ids = [fid for fid in file_ids if fid > max_index or fid < 0]
    if invalid_ids:
        print(f"❌ Неверные ID файлов: {invalid_ids}")
        print(f"   Доступные ID: 0-{max_index}")
        return False

    # Устанавливаем priority=0 для файлов
    success = set_file_priority(session, base_url, hash_id, file_ids, priority=0)

    if success:
        print(f"✅ Файлы исключены из загрузки")
        print(f"\n📝 Исключённые файлы:")
        for fid in file_ids:
            file_info = files[fid]
            name = file_info['name']
            size_bytes = file_info['size']
            size = format_size(size_bytes)
            print(f"   [{fid}] ❌ {name} ({size})")

        # Считаем сколько места сэкономили
        total_skipped = sum(files[fid]['size'] for fid in file_ids)
        print(f"\n💾 Сэкономлено места: {format_size(total_skipped)}")
        return True
    else:
        print(f"❌ Ошибка при установке приоритета файлов")
        return False

def format_size(bytes_size):
    """Форматирование размера в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def main():
    if len(sys.argv) != 3:
        print("Использование: python qbt-skip-files.py <hash> <ID файлов>")
        print("\nПримеры:")
        print("  python qbt-skip-files.py <hash> 0,1,2       - исключить файлы 0, 1, 2")
        print("  python qbt-skip-files.py <hash> 5-10        - исключить файлы с 5 по 10")
        print("  python qbt-skip-files.py <hash> 0,3,5-8,12  - комбинированный вариант")
        sys.exit(1)

    hash_id = sys.argv[1].lower()
    ids_string = sys.argv[2]

    success = skip_files(hash_id, ids_string)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Обновление библиотеки Jellyfin по названию
Использование: python3 jellyfin-refresh.py <название>
Примеры:
  python3 jellyfin-refresh.py Фильмы
  python3 jellyfin-refresh.py Сериалы
"""

import sys
import json
import requests
import os

def load_credentials():
    """Загрузка учетных данных из keys/jellyfin.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keys_file = os.path.join(os.path.dirname(script_dir), 'keys', 'jellyfin.json')

    with open(keys_file, 'r') as f:
        return json.load(f)

def get_libraries(url, api_key):
    """Получить список всех библиотек"""
    headers = {
        'Authorization': f'MediaBrowser Token={api_key}'
    }

    response = requests.get(f'{url}/Library/VirtualFolders', headers=headers)
    response.raise_for_status()
    return response.json()

def refresh_library(url, api_key, library_id):
    """Обновить библиотеку по ID"""
    headers = {
        'Authorization': f'MediaBrowser Token={api_key}'
    }

    response = requests.post(f'{url}/Library/Refresh', headers=headers, params={'id': library_id})
    response.raise_for_status()
    return response.status_code == 204

def main():
    if len(sys.argv) < 2:
        print("❌ Ошибка: не указано название библиотеки")
        print("\nИспользование: python3 jellyfin-refresh.py <название>")
        print("\nПримеры:")
        print("  python3 jellyfin-refresh.py Фильмы")
        print("  python3 jellyfin-refresh.py Сериалы")
        sys.exit(1)

    library_name = ' '.join(sys.argv[1:])

    try:
        # Загрузить учетные данные
        creds = load_credentials()
        url = creds['url']
        api_key = creds['api_key']

        # Получить список библиотек
        libraries = get_libraries(url, api_key)

        # Найти библиотеку по названию
        library = None
        for lib in libraries:
            if lib['Name'].lower() == library_name.lower():
                library = lib
                break

        if not library:
            print(f"❌ Библиотека '{library_name}' не найдена")
            print("\n📚 Доступные библиотеки:")
            for lib in libraries:
                print(f"  • {lib['Name']}")
            sys.exit(1)

        # Обновить библиотеку
        print(f"🔄 Обновление библиотеки '{library['Name']}'...")
        refresh_library(url, api_key, library['ItemId'])
        print(f"✅ Библиотека '{library['Name']}' успешно обновлена!")

    except FileNotFoundError:
        print("❌ Файл keys/jellyfin.json не найден")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к Jellyfin: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

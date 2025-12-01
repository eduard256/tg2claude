#!/usr/bin/env python3
"""
Поиск контента в Jellyfin
Использование: python3 jellyfin-search.py <название>
Примеры:
  python3 jellyfin-search.py Интерстеллар
  python3 jellyfin-search.py "Breaking Bad"
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

def search_items(url, api_key, query):
    """Поиск контента по названию"""
    headers = {
        'Authorization': f'MediaBrowser Token={api_key}'
    }

    params = {
        'searchTerm': query,
        'IncludeItemTypes': 'Movie,Series',
        'Recursive': 'true',
        'Fields': 'Path,MediaSources,ProviderIds'
    }

    response = requests.get(f'{url}/Items', headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def format_size(bytes_size):
    """Форматирование размера в человекочитаемый вид"""
    if not bytes_size:
        return "N/A"

    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} ПБ"

def main():
    if len(sys.argv) < 2:
        print("❌ Ошибка: не указан поисковый запрос")
        print("\nИспользование: python3 jellyfin-search.py <название>")
        print("\nПримеры:")
        print("  python3 jellyfin-search.py Интерстеллар")
        print('  python3 jellyfin-search.py "Breaking Bad"')
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    try:
        # Загрузить учетные данные
        creds = load_credentials()
        url = creds['url']
        api_key = creds['api_key']

        # Поиск
        print(f"🔍 Поиск '{query}'...\n")
        result = search_items(url, api_key, query)

        if result['TotalRecordCount'] == 0:
            print(f"❌ Ничего не найдено по запросу '{query}'")
            sys.exit(0)

        print(f"✅ Найдено: {result['TotalRecordCount']}\n")

        for item in result['Items']:
            item_type = "🎬" if item['Type'] == 'Movie' else "📺"
            name = item['Name']
            year = item.get('ProductionYear', 'N/A')
            item_id = item['Id']

            # Размер файла
            size = "N/A"
            if 'MediaSources' in item and len(item['MediaSources']) > 0:
                total_size = sum(ms.get('Size', 0) for ms in item['MediaSources'])
                size = format_size(total_size)

            # Путь к файлу
            path = item.get('Path', 'N/A')

            print(f"{item_type} {name} ({year})")
            print(f"   ID: {item_id}")
            print(f"   Размер: {size}")
            print(f"   Путь: {path}")
            print()

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

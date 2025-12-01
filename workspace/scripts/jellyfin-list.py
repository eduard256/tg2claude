#!/usr/bin/env python3
"""
Список всего контента в Jellyfin
Использование: python3 jellyfin-list.py [фильмы|сериалы]
Примеры:
  python3 jellyfin-list.py          # весь контент
  python3 jellyfin-list.py фильмы   # только фильмы
  python3 jellyfin-list.py сериалы  # только сериалы
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

def get_items(url, api_key, item_type=None):
    """Получить список контента"""
    headers = {
        'Authorization': f'MediaBrowser Token={api_key}'
    }

    params = {
        'Recursive': 'true',
        'Fields': 'Path,MediaSources,ProviderIds',
        'SortBy': 'SortName',
        'SortOrder': 'Ascending'
    }

    if item_type:
        params['IncludeItemTypes'] = item_type

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
    item_type = None
    type_filter = ""

    if len(sys.argv) > 1:
        filter_arg = sys.argv[1].lower()
        if filter_arg in ['фильмы', 'фильм', 'movie', 'movies']:
            item_type = 'Movie'
            type_filter = "Фильмы"
        elif filter_arg in ['сериалы', 'сериал', 'series', 'tv']:
            item_type = 'Series'
            type_filter = "Сериалы"
        else:
            print(f"❌ Неверный фильтр: {sys.argv[1]}")
            print("\nИспользование: python3 jellyfin-list.py [фильмы|сериалы]")
            sys.exit(1)

    try:
        # Загрузить учетные данные
        creds = load_credentials()
        url = creds['url']
        api_key = creds['api_key']

        # Получить список
        title = f"📚 {type_filter}" if type_filter else "📚 Весь контент"
        print(f"{title}\n")

        result = get_items(url, api_key, item_type)

        if result['TotalRecordCount'] == 0:
            print("❌ Контент не найден")
            sys.exit(0)

        print(f"Всего: {result['TotalRecordCount']}\n")

        for item in result['Items']:
            item_type_icon = "🎬" if item['Type'] == 'Movie' else "📺"
            name = item['Name']
            year = item.get('ProductionYear', 'N/A')

            # Размер файла
            size = "N/A"
            if 'MediaSources' in item and len(item['MediaSources']) > 0:
                total_size = sum(ms.get('Size', 0) for ms in item['MediaSources'])
                size = format_size(total_size)

            print(f"{item_type_icon} {name} ({year}) - {size}")

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

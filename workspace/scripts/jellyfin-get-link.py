#!/usr/bin/env python3
"""
Получение прямой ссылки на контент в Jellyfin
Использование: python3 jellyfin-get-link.py <название>
Примеры:
  python3 jellyfin-get-link.py Интерстеллар
  python3 jellyfin-get-link.py "Breaking Bad"
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

def get_server_id(url, api_key):
    """Получить ID сервера"""
    headers = {
        'Authorization': f'MediaBrowser Token={api_key}'
    }
    response = requests.get(f'{url}/System/Info', headers=headers)
    response.raise_for_status()
    return response.json()['Id']

def search_items(url, api_key, query):
    """Поиск контента по названию"""
    headers = {
        'Authorization': f'MediaBrowser Token={api_key}'
    }

    params = {
        'searchTerm': query,
        'IncludeItemTypes': 'Movie,Series',
        'Recursive': 'true',
        'Fields': 'Path,MediaSources'
    }

    response = requests.get(f'{url}/Items', headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) < 2:
        print("❌ Ошибка: не указано название")
        print("\nИспользование: python3 jellyfin-get-link.py <название>")
        print("\nПримеры:")
        print("  python3 jellyfin-get-link.py Интерстеллар")
        print('  python3 jellyfin-get-link.py "Breaking Bad"')
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    try:
        # Загрузить учетные данные
        creds = load_credentials()
        url = creds['url']
        api_key = creds['api_key']

        # Получить Server ID
        server_id = get_server_id(url, api_key)

        # Поиск
        print(f"🔍 Поиск '{query}'...\n")
        result = search_items(url, api_key, query)

        if result['TotalRecordCount'] == 0:
            print(f"❌ Ничего не найдено по запросу '{query}'")
            sys.exit(0)

        for item in result['Items']:
            item_type = "🎬" if item['Type'] == 'Movie' else "📺"
            name = item['Name']
            year = item.get('ProductionYear', 'N/A')
            item_id = item['Id']

            print(f"{item_type} {name} ({year})")
            print(f"ID: {item_id}")

            # Ссылка для просмотра (детали)
            details_link = f"{url}/web/index.html#!/details?id={item_id}"
            print(f"\n📄 Страница с деталями:\n{details_link}")

            # Ссылка для прямого воспроизведения в плеере
            if item['Type'] == 'Movie':
                player_link = f"{url}/web/index.html#!/video?id={item_id}&serverId={server_id}"
                print(f"\n▶️  Открыть в плеере (сразу включит фильм):\n{player_link}")

                stream_link = f"{url}/Items/{item_id}/Download?api_key={api_key}"
                print(f"\n⬇️  Прямая ссылка для скачивания:\n{stream_link}")
            else:
                print(f"\n📺 Для сериалов используйте веб-интерфейс для выбора эпизода")

            # Путь к файлу на сервере
            path = item.get('Path', 'N/A')
            print(f"\n📁 Путь на сервере:\n{path}")
            print("\n" + "=" * 60 + "\n")

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

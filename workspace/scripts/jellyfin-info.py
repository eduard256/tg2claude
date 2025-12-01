#!/usr/bin/env python3
"""
Детальная информация о контенте в Jellyfin
Использование: python3 jellyfin-info.py <название>
Примеры:
  python3 jellyfin-info.py Интерстеллар
  python3 jellyfin-info.py "Breaking Bad"
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
        'Fields': 'Path,MediaSources,MediaStreams,ProviderIds,Overview'
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

def format_duration(ticks):
    """Форматирование длительности из тиков"""
    if not ticks:
        return "N/A"

    seconds = ticks / 10000000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)

    if hours > 0:
        return f"{hours}ч {minutes}м"
    return f"{minutes}м"

def main():
    if len(sys.argv) < 2:
        print("❌ Ошибка: не указано название")
        print("\nИспользование: python3 jellyfin-info.py <название>")
        print("\nПримеры:")
        print("  python3 jellyfin-info.py Интерстеллар")
        print('  python3 jellyfin-info.py "Breaking Bad"')
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

        for item in result['Items']:
            item_type = "🎬 Фильм" if item['Type'] == 'Movie' else "📺 Сериал"
            name = item['Name']
            year = item.get('ProductionYear', 'N/A')

            print("=" * 60)
            print(f"{item_type}: {name} ({year})")
            print("=" * 60)
            print(f"ID: {item['Id']}")

            # Описание
            if 'Overview' in item and item['Overview']:
                overview = item['Overview'][:200] + "..." if len(item['Overview']) > 200 else item['Overview']
                print(f"\n📝 Описание:\n{overview}")

            # Медиа информация
            if 'MediaSources' in item and len(item['MediaSources']) > 0:
                print("\n💿 Медиа информация:")
                for idx, ms in enumerate(item['MediaSources'], 1):
                    if len(item['MediaSources']) > 1:
                        print(f"\n  Файл {idx}:")

                    # Размер
                    size = format_size(ms.get('Size', 0))
                    print(f"  • Размер: {size}")

                    # Длительность
                    duration = format_duration(ms.get('RunTimeTicks'))
                    print(f"  • Длительность: {duration}")

                    # Контейнер
                    container = ms.get('Container', 'N/A')
                    print(f"  • Контейнер: {container}")

                    # Битрейт
                    bitrate = ms.get('Bitrate')
                    if bitrate:
                        bitrate_mbps = bitrate / 1000000
                        print(f"  • Битрейт: {bitrate_mbps:.2f} Mbps")

            # Видео потоки
            if 'MediaSources' in item and len(item['MediaSources']) > 0:
                for ms in item['MediaSources']:
                    video_streams = [s for s in ms.get('MediaStreams', []) if s['Type'] == 'Video']
                    if video_streams:
                        print("\n🎥 Видео:")
                        for vs in video_streams:
                            codec = vs.get('Codec', 'N/A')
                            width = vs.get('Width', 'N/A')
                            height = vs.get('Height', 'N/A')
                            fps = vs.get('RealFrameRate', vs.get('AverageFrameRate', 'N/A'))

                            quality = f"{height}p" if height != 'N/A' else 'N/A'
                            print(f"  • Качество: {quality} ({width}x{height})")
                            print(f"  • Кодек: {codec}")
                            if fps != 'N/A':
                                print(f"  • FPS: {fps:.2f}")

            # Аудио потоки
            if 'MediaSources' in item and len(item['MediaSources']) > 0:
                for ms in item['MediaSources']:
                    audio_streams = [s for s in ms.get('MediaStreams', []) if s['Type'] == 'Audio']
                    if audio_streams:
                        print("\n🔊 Аудио:")
                        for idx, aus in enumerate(audio_streams, 1):
                            codec = aus.get('Codec', 'N/A')
                            language = aus.get('Language', 'N/A')
                            channels = aus.get('Channels', 'N/A')
                            print(f"  Дорожка {idx}: {codec}, {language}, {channels} каналов")

            # Субтитры
            if 'MediaSources' in item and len(item['MediaSources']) > 0:
                for ms in item['MediaSources']:
                    subtitle_streams = [s for s in ms.get('MediaStreams', []) if s['Type'] == 'Subtitle']
                    if subtitle_streams:
                        print("\n💬 Субтитры:")
                        for idx, sub in enumerate(subtitle_streams, 1):
                            language = sub.get('Language', sub.get('DisplayTitle', 'N/A'))
                            codec = sub.get('Codec', 'N/A')
                            print(f"  {idx}. {language} ({codec})")

            # Путь к файлу
            path = item.get('Path', 'N/A')
            print(f"\n📁 Путь: {path}")
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

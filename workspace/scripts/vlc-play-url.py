#!/usr/bin/env python3
"""
Скрипт для отправки URL на воспроизведение в VLC через веб-интерфейс
"""
import sys
import requests

VLC_HOST = "http://10.0.0.31"

def play_url(url):
    """Отправляет URL на воспроизведение в VLC"""

    # Сначала получим страницу, чтобы понять endpoint
    try:
        session = requests.Session()

        # Пробуем разные возможные endpoints
        endpoints = [
            "/stream.json",
            "/download.json",
            "/remote/vlc/addToPlaylistAndPlay",
            "/api/play",
            "/play"
        ]

        for endpoint in endpoints:
            try:
                # POST запрос с URL
                response = session.post(
                    f"{VLC_HOST}{endpoint}",
                    data={"url": url},
                    timeout=5
                )
                print(f"Попытка {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ URL отправлен через {endpoint}")
                    return True
            except Exception as e:
                continue

        # Если ничего не сработало, попробуем через GET параметры
        for endpoint in endpoints:
            try:
                response = session.get(
                    f"{VLC_HOST}{endpoint}",
                    params={"url": url},
                    timeout=5
                )
                print(f"Попытка GET {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ URL отправлен через GET {endpoint}")
                    return True
            except Exception as e:
                continue

        print("❌ Не удалось найти рабочий endpoint")
        return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 vlc-play-url.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"📺 Отправка URL в VLC: {url}")
    play_url(url)

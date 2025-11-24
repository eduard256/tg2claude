#!/usr/bin/env python3
"""
Скрипт для отображения структуры файлов торрента
Использование: python qbt-show-files.py <hash>
"""

import sys
import json
import requests
from pathlib import Path
from collections import defaultdict

def load_credentials():
    """Загрузка credentials из keys/qbittorrent.json"""
    keys_file = Path(__file__).parent.parent / "keys" / "qbittorrent.json"
    with open(keys_file, 'r') as f:
        return json.load(f)

def format_size(bytes_size):
    """Форматирование размера в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def get_priority_status(priority):
    """Получить статус приоритета"""
    if priority == 0:
        return "❌ не качается"
    elif priority == 1:
        return "✅ качается"
    elif priority == 6:
        return "⚡ высокий"
    elif priority == 7:
        return "🔥 максимальный"
    else:
        return "❓ неизвестно"

def build_tree(files):
    """Построить дерево папок и файлов"""
    tree = defaultdict(list)

    for file_info in files:
        path = file_info['name']
        parts = path.split('/')

        if len(parts) == 1:
            # Файл в корне
            tree['__root__'].append(file_info)
        else:
            # Файл в папке
            folder = '/'.join(parts[:-1])
            tree[folder].append(file_info)

    return tree

def print_tree(tree, files_list, total_size):
    """Вывести дерево файлов"""
    # Собираем все уникальные папки
    folders = set()
    for path in tree.keys():
        if path != '__root__':
            parts = path.split('/')
            for i in range(len(parts)):
                folders.add('/'.join(parts[:i+1]))

    folders = sorted(folders)

    # Если есть файлы в корне
    if '__root__' in tree and tree['__root__']:
        print("\n📂 Файлы в корне:")
        for file_info in sorted(tree['__root__'], key=lambda x: x['name']):
            idx = file_info['index']
            name = file_info['name']
            size = format_size(file_info['size'])
            priority = file_info['priority']
            status = get_priority_status(priority)
            progress = file_info.get('progress', 0) * 100

            print(f"├─ [{idx}] 📄 {name} ({size}) {status} [{progress:.1f}%]")

    # Выводим папки и их содержимое
    if folders:
        print("\n📂 Структура папок:")

        # Группируем по корневой папке
        root_folders = set()
        for folder in folders:
            root = folder.split('/')[0]
            root_folders.add(root)

        for root_folder in sorted(root_folders):
            # Находим все файлы в этой корневой папке
            folder_files = []
            for folder_path, files in tree.items():
                if folder_path.startswith(root_folder):
                    folder_files.extend(files)

            # Считаем общий размер папки
            folder_size = sum(f['size'] for f in folder_files)

            print(f"\n├─ 📁 {root_folder}/ ({format_size(folder_size)})")

            # Выводим файлы в этой папке и подпапках
            for folder_path in sorted([f for f in folders if f.startswith(root_folder)]):
                if folder_path in tree:
                    # Определяем уровень вложенности
                    depth = folder_path.count('/')
                    indent = "│  " * (depth + 1)

                    # Если это подпапка, показываем её
                    if depth > 0:
                        subfolder_name = folder_path.split('/')[-1]
                        subfolder_files = tree[folder_path]
                        subfolder_size = sum(f['size'] for f in subfolder_files)
                        print(f"{indent}├─ 📁 {subfolder_name}/ ({format_size(subfolder_size)})")
                        indent += "│  "

                    # Выводим файлы
                    for file_info in sorted(tree[folder_path], key=lambda x: x['name']):
                        idx = file_info['index']
                        name = file_info['name'].split('/')[-1]  # Только имя файла
                        size = format_size(file_info['size'])
                        priority = file_info['priority']
                        status = get_priority_status(priority)
                        progress = file_info.get('progress', 0) * 100

                        print(f"{indent}├─ [{idx}] 📄 {name} ({size}) {status} [{progress:.1f}%]")

def show_files(hash_id):
    """Показать файлы торрента"""
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
        return False

    # Получаем информацию о торренте
    info_url = f"{base_url}/api/v2/torrents/info"
    params = {'hashes': hash_id}
    response = session.get(info_url, params=params)
    torrents = response.json()

    if not torrents or len(torrents) == 0:
        print(f"❌ Торрент с hash {hash_id} не найден")
        return False

    torrent = torrents[0]
    name = torrent.get('name', 'Без названия')
    total_size = torrent.get('size', 0)
    progress = torrent.get('progress', 0) * 100

    # Получаем список файлов
    files_url = f"{base_url}/api/v2/torrents/files"
    params = {'hash': hash_id}
    response = session.get(files_url, params=params)
    files = response.json()

    if not files:
        print(f"❌ Не удалось получить список файлов")
        print(f"⏳ Возможно торрент ещё загружает метаданные, попробуйте через несколько секунд")
        return False

    # Заголовок
    print(f"\n{'='*70}")
    print(f"📦 Торрент: {name}")
    print(f"🆔 Hash: {hash_id}")
    print(f"📊 Размер: {format_size(total_size)} | Прогресс: {progress:.1f}%")
    print(f"📝 Всего файлов: {len(files)}")
    print(f"{'='*70}")

    # Строим и выводим дерево
    tree = build_tree(files)
    print_tree(tree, files, total_size)

    print(f"\n{'='*70}")
    print("💡 Для управления файлами используйте:")
    print(f"   python3 scripts/qbt-skip-files.py {hash_id} <ID файлов>")
    print(f"   python3 scripts/qbt-download-files.py {hash_id} <ID файлов>")
    print("\n   Примеры ID: 0,1,2 или 5-10 или 0,3,5-8,12")
    print(f"{'='*70}\n")

    return True

def main():
    if len(sys.argv) != 2:
        print("Использование: python qbt-show-files.py <hash>")
        print("\nПример:")
        print("  python qbt-show-files.py a08982d48ba7ce28e8bb42922d8fe37243903405")
        sys.exit(1)

    hash_id = sys.argv[1].lower()
    show_files(hash_id)

if __name__ == "__main__":
    main()

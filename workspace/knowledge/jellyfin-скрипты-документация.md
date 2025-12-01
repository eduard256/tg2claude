# Jellyfin - Работа со скриптами

## Требования
- Файл `keys/jellyfin.json` должен содержать поля: `url`, `api_key`
- Получить поля: `python3 get-keys.py jellyfin.json`
- Получить значение: `jq -r .поле keys/jellyfin.json`

---

## Скрипты

### `jellyfin-refresh.py <библиотека>` - Обновить библиотеку
```bash
python3 scripts/jellyfin-refresh.py Фильмы
python3 scripts/jellyfin-refresh.py Сериалы
```
Использовать после добавления новых файлов в qBittorrent.

---

### `jellyfin-search.py <название>` - Найти контент
```bash
python3 scripts/jellyfin-search.py Интерстеллар
python3 scripts/jellyfin-search.py "Breaking Bad"
```
Выдаёт: название, год, ID, размер, путь.

---

### `jellyfin-list.py [фильтр]` - Список контента
```bash
python3 scripts/jellyfin-list.py           # всё
python3 scripts/jellyfin-list.py фильмы    # только фильмы
python3 scripts/jellyfin-list.py сериалы   # только сериалы
```

---

### `jellyfin-info.py <название>` - Детали о контенте
```bash
python3 scripts/jellyfin-info.py Deadpool
```
Выдаёт: качество (4K/1080p), размер, длительность, кодеки, аудиодорожки, субтитры, битрейт, путь.

---

### `jellyfin-get-link.py <название>` - Получить ссылки
```bash
python3 scripts/jellyfin-get-link.py Batman
```
Выдаёт 3 типа ссылок:
1. **Страница с деталями** - `http://IP:8096/web/index.html#!/details?id=ITEM_ID`
2. **Для VLC/плеера** - `http://IP:8096/Videos/ITEM_ID/stream?static=true&api_key=KEY` (работает только в VLC/MPV, НЕ в браузере)
3. **Для скачивания** - `http://IP:8096/Items/ITEM_ID/Download?api_key=KEY`

---

## Типичный сценарий: скачать фильм
1. Найти торрент: `bash scripts/freedomist-search.sh "название"`
2. Добавить в qBittorrent: `python3 scripts/qbt-add-torrent.py "magnet:..."`
3. Дождаться завершения: `python3 scripts/qbt-list-active.py`
4. Обновить Jellyfin: `python3 scripts/jellyfin-refresh.py Фильмы`
5. Получить ссылку: `python3 scripts/jellyfin-get-link.py "название"`

---

## Проверка перед скачкой (избежать дублей)
```bash
python3 scripts/jellyfin-search.py "название фильма"
```
Если нашёл - фильм уже есть, качать не нужно.

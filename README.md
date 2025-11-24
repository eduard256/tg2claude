# tg2claude v0.0.1

Простой Telegram-бот для взаимодействия с Claude Code CLI.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте `.env` файл:
```env
TG_BOT_TOKEN=your_bot_token_here
ALLOWED_USERS=123456789,987654321
```

3. Убедитесь, что Claude Code CLI установлен и доступен в PATH.

## Запуск

Из папки workspace:
```bash
python ../system/bot.py
```

Или из корня проекта:
```bash
cd workspace && python ../system/bot.py
```

## Команды

- `/start` - Сброс сессии Claude
- Любое текстовое сообщение - отправка в Claude Code

## Структура

```
tg2claude/
├── workspace/          # Рабочая директория Claude
│   ├── keys/          # Хранение credentials
│   ├── knowledge/     # База знаний
│   ├── scripts/       # Вспомогательные скрипты
│   └── get-keys.py    # Утилита для чтения полей credentials
├── system/            # Файлы бота
│   ├── PROMPT.md     # Системный промпт
│   ├── bot.py        # Главный файл
│   ├── config.py     # Конфигурация
│   ├── claude.py     # Работа с Claude Code
│   ├── parser.py     # Парсинг JSON
│   └── sessions.py   # Управление сессиями
├── sessions/          # Хранение сессий пользователей
├── .env              # Переменные окружения
└── requirements.txt   # Зависимости Python
```

## Особенности

- Поддержка нескольких пользователей
- Сохранение контекста между сообщениями
- Потоковая передача ответов в реальном времени
- Простая и надёжная архитектура без излишних проверок
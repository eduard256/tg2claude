#!/bin/bash
# Скрипт остановки tg2claude бота

echo "🛑 Остановка tg2claude бота..."

# Поиск процесса bot.py
PID=$(pgrep -f "python.*bot.py" || true)

if [ -z "$PID" ]; then
    echo "⚠️  Бот не запущен"
    exit 0
fi

# Остановка процесса
kill $PID 2>/dev/null || true

echo "✅ Бот остановлен (PID: $PID)"

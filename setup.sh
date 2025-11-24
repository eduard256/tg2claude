#!/bin/bash
# Скрипт установки виртуального окружения для tg2claude

set -e

echo "🚀 Установка tg2claude..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.10 или выше."
    exit 1
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация и установка зависимостей
echo "📥 Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Для запуска бота:"
echo "  ./start.sh"
echo ""
echo "Или вручную:"
echo "  source venv/bin/activate"
echo "  cd workspace && python ../system/bot.py"

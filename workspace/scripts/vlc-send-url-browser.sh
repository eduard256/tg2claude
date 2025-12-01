#!/bin/bash
# Скрипт для отправки URL в VLC через эмуляцию браузера

URL="$1"
if [ -z "$URL" ]; then
    echo "Использование: $0 <URL>"
    exit 1
fi

# Попробуем через JavaScript injection с curl
echo "📺 Отправка URL в VLC: $URL"

# Создаем временный HTML файл который выполнит отправку
cat > /tmp/vlc_submit.html <<EOF
<html>
<body>
<script>
var xhr = new XMLHttpRequest();
xhr.open('POST', 'http://10.0.0.31/stream.json', true);
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.send(JSON.stringify({url: '$URL'}));
</script>
</body>
</html>
EOF

# Попробуем разные варианты API
echo "Пробую разные endpoints..."

# Вариант 1: POST с JSON
curl -X POST "http://10.0.0.31/stream.json" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$URL\"}" 2>&1

echo ""

# Вариант 2: GET с параметрами
curl "http://10.0.0.31/stream.json?url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$URL'))")" 2>&1

echo ""
echo "✅ Запросы отправлены"

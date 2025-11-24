#!/bin/bash
# Получение magnet-ссылки по ключу из результатов поиска
# Использование: ./freedomist-magnet.sh "key"

KEY="$1"

if [ -z "$KEY" ]; then
    echo '{"error": "Usage: ./freedomist-magnet.sh \"key\""}'
    exit 1
fi

TOKEN=$(jq -r .token keys/freedomist.json)

curl -sk "https://api.exfreedomist.com/magnet/${KEY}?token=${TOKEN}" | jq '{
  status: .status_code,
  magnet: .data.magnet_link,
  tracker: .data.tracker
}'

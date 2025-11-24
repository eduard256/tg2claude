#!/bin/bash
# Поиск торрентов через Freedomist API (только для ИИ)
# Использование: ./freedomist-search.sh "название" [лимит]

QUERY="$1"
LIMIT="${2:-20}"

if [ -z "$QUERY" ]; then
    echo '{"error": "Usage: ./freedomist-search.sh \"query\" [limit]"}'
    exit 1
fi

TOKEN=$(jq -r .token keys/freedomist.json)

curl -sk -X POST "https://api.exfreedomist.com/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"token\": \"$TOKEN\", \"limit\": $LIMIT}" | jq '{
  status: .status_code,
  total: (.data | length),
  results: .data | map({
    title,
    tracker,
    s: .seeders,
    l: .leechers,
    size,
    key: .magnet_key,
    dl: .downloads
  })
}'

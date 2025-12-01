# Troubleshooting: MCP серверы не работают в боте

## Проблема

Когда вы добавляете MCP сервер через `claude mcp add`, он отлично работает при ручном запуске Claude Code в терминале, но **не работает** когда Claude запускается через бота (Python subprocess).

### Симптомы

- При ручном запуске `claude` в терминале MCP сервер показывает статус `✓ Connected`
- В Telegram боте Claude отвечает: "У меня нет доступа к MCP серверам"
- При проверке в логах видно: `"mcp_servers":[{"name":"mqtt","status":"failed"}]`

## Причина

Проблема возникает из-за того, что MCP модули установлены только в **системном Python**, а бот работает в **виртуальном окружении (venv)**.

Когда Claude Code запускается через subprocess в Python и пытается подключить MCP сервер командой типа:
```bash
python3 -m mqtt_mcp.server
```

Он использует Python из активного venv, где модуля `mqtt_mcp` нет, поэтому подключение не удается.

## Решение

### 1. Установите MCP модули в виртуальное окружение

```bash
# Активируйте venv бота
cd /path/to/tg2claude
source venv/bin/activate

# Установите нужный MCP сервер
pip install mqtt-mcp-server  # для MQTT
# или
pip install <your-mcp-package>  # для другого MCP сервера
```

### 2. Убедитесь, что окружение передается в subprocess

В файле `system/claude.py` должна быть строка:

```python
import os

# ...

process = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    cwd=WORKSPACE_DIR,
    env=os.environ.copy(),  # ← Важно! Передаем окружение
    limit=10 * 1024 * 1024
)
```

Параметр `env=os.environ.copy()` гарантирует, что subprocess получит все переменные окружения, включая `HOME`, которая нужна Claude Code для поиска конфигурации MCP.

## Проверка решения

### Тест 1: Проверьте что модуль установлен в venv

```bash
cd /path/to/tg2claude
source venv/bin/activate
python3 -c "import mqtt_mcp; print(mqtt_mcp.__file__)"
```

Должен показать путь к модулю **внутри venv**, например:
```
/home/user/tg2claude/venv/lib/python3.10/site-packages/mqtt_mcp/__init__.py
```

Если показывает путь вне venv или ошибку `ModuleNotFoundError` - значит модуль не установлен.

### Тест 2: Запустите тестовый скрипт

Создайте файл `test_mcp.py`:

```python
#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "system"))
from config import WORKSPACE_DIR, CLAUDE_BASE_CMD

async def test():
    cmd = CLAUDE_BASE_CMD.copy()
    cmd.extend(["-p", "у тебя есть mcp?"])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=WORKSPACE_DIR,
        env=os.environ.copy(),
        limit=10 * 1024 * 1024
    )

    line = await process.stdout.readline()
    print(line.decode("utf-8"))
    await process.wait()

asyncio.run(test())
```

Запустите:
```bash
source venv/bin/activate
python test_mcp.py | grep mcp_servers
```

Должно быть:
```json
"mcp_servers":[{"name":"mqtt","status":"connected"}]
```

Если `"status":"failed"` - модуль не установлен в venv.

### Тест 3: Проверьте через бота

Отправьте боту в Telegram:
```
у тебя есть mcp?
```

Правильный ответ должен содержать список MCP инструментов, например:
```
Да, у меня есть доступ к MCP серверу для работы с MQTT!

Доступные функции:
- mcp__mqtt__topics
- mcp__mqtt__value
- mcp__mqtt__publish
- mcp__mqtt__record
```

## Частые ошибки

### Ошибка: Конфликт версий pydantic

При установке `mqtt-mcp-server` может появиться:
```
ERROR: aiogram 3.15.0 requires pydantic<2.10,>=2.4.1, but you have pydantic 2.12.4
```

**Решение:** Обычно это не критично и бот продолжит работать. Если возникают проблемы:

```bash
pip install 'pydantic>=2.4.1,<2.10'
pip install mqtt-mcp-server --no-deps
pip install aiomqtt mcp
```

### Ошибка: ModuleNotFoundError при запуске MCP сервера

Означает, что модуль не установлен в текущем Python окружении. Убедитесь что:
1. venv активирован: `source venv/bin/activate`
2. Модуль установлен: `pip install mqtt-mcp-server`
3. Проверьте: `python3 -m mqtt_mcp.server --help`

### Ошибка: MCP сервер работает вручную, но не в боте

Скорее всего venv не активирован при запуске бота. Проверьте `start.sh`:

```bash
#!/bin/bash
source venv/bin/activate  # ← Должно быть!
cd workspace
python ../system/bot.py
```

## Для других MCP серверов

Эта проблема актуальна для **любых** MCP серверов, которые требуют Python модули:

- `mqtt-mcp-server` → `pip install mqtt-mcp-server`
- `playwright-mcp-server` → `pip install playwright-mcp-server`
- Любой кастомный MCP сервер → установите его зависимости в venv

Общее правило: **все Python зависимости MCP серверов должны быть установлены в том же venv, где работает бот**.

## Альтернативное решение: Использовать абсолютный путь к Python

Вместо того чтобы устанавливать модули в venv, можно настроить MCP сервер на использование системного Python:

```bash
claude mcp remove mqtt
claude mcp add --transport stdio mqtt \
  --env MQTT_HOST=your_host \
  --env MQTT_PORT=1883 \
  --env MQTT_USERNAME=your_user \
  --env MQTT_PASSWORD=your_pass \
  -- /usr/bin/python3 -m mqtt_mcp.server  # ← Абсолютный путь
```

Но это может привести к другим проблемам с окружением, поэтому рекомендуется установка в venv.

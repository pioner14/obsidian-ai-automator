#!/bin/bash
set -x # Включаем режим отладки Bash

# --- КОНФИГУРАЦИЯ ---
WATCH_DIR="/home/nick/Public/ai-automator/" # Укажите путь к папке для мониторинга
LOG_FILE="$(dirname "$0")/.watch_and_transcribe.log"


# --- ФУНКЦИИ ---
log_message() {
    local MESSAGE="$1"
    local LEVEL="${2:-INFO}" # По умолчанию INFO
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $LEVEL - $MESSAGE" | tee -a "$LOG_FILE"
    if [[ "$LEVEL" == "ERROR" ]]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR - $MESSAGE" >&2
    fi
}

# --- ОСНОВНАЯ ЛОГИКА ---
log_message "Запуск мониторинга папки: $WATCH_DIR с inotify..."

# Проверка существования папки для мониторинга
if [ ! -d "$WATCH_DIR" ]; then
    log_message "Ошибка: Папка для мониторинга \"$WATCH_DIR\" не существует. Создайте ее или укажите правильный путь." ERROR
    exit 1
fi

# Запускаем Python-скрипт мониторинга
source venv/bin/activate && python "$(dirname "$0")"/scripts/inotify_monitor.py
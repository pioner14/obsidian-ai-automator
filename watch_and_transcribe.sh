#!/bin/bash
set -x # Включаем режим отладки Bash

# --- КОНФИГУРАЦИЯ ---
WATCH_DIR="/home/nick/Public/ai-automator/" # Укажите путь к папке для мониторинга
LOG_FILE="$(dirname "$0")/.watch_and_transcribe.log"
SLEEP_INTERVAL=10 # Интервал опроса в секундах

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
log_message "Запуск скрипта мониторинга папки: $WATCH_DIR (метод опроса)"

# Проверка существования папки для мониторинга
if [ ! -d "$WATCH_DIR" ]; then
    log_message "Ошибка: Папка для мониторинга \"$WATCH_DIR\" не существует. Создайте ее или укажите правильный путь." ERROR
    exit 1
fi

log_message "Начало мониторинга папки \"$WATCH_DIR\" на предмет новых видео/аудио файлов..."

while true; do
    log_message "Выполнение команды find: find \"$WATCH_DIR\" -maxdepth 1 -type f -print0"
    
    # Собираем все файлы в массив, чтобы избежать проблем с подшеллами
    mapfile -d '' FILES_TO_PROCESS < <(find "$WATCH_DIR" -maxdepth 1 -type f -print0)
    
    for FULL_PATH in "${FILES_TO_PROCESS[@]}"; do
        if [ -z "$FULL_PATH" ]; then
            continue
        fi

        log_message "Обработка FULL_PATH: $FULL_PATH" # Отладочное сообщение
        FILENAME=$(basename "$FULL_PATH")
        log_message "Обнаружен файл: $FULL_PATH"

        # Проверка, является ли файл видео или аудио
        log_message "Попытка определить MIME-тип файла: $FULL_PATH"
        
        # Проверяем существование и исполняемость команды 'file'
        if ! command -v file &> /dev/null; then
            log_message "Ошибка: Команда 'file' не найдена. Убедитесь, что она установлена и доступна в PATH." ERROR
            continue
        fi

        # Выводим команду file перед ее выполнением
        echo "$(date '+%Y-%m-%d %H:%M:%S') - DEBUG: Executing file command: 'file --mime-type -b \"$FULL_PATH\"'" >> "$LOG_FILE"

        # Используем временный файл для захвата вывода команды file
        TEMP_FILE_OUTPUT=$(mktemp)
        file --mime-type -b "$FULL_PATH" > "$TEMP_FILE_OUTPUT" 2>&1
        _FILE_EXIT_CODE=$?
        _FILE_OUTPUT=$(cat "$TEMP_FILE_OUTPUT")
        rm "$TEMP_FILE_OUTPUT" # Удаляем временный файл

        # Выводим отладочную информацию напрямую
        echo "$(date '+%Y-%m-%d %H:%M:%S') - DEBUG: file command output (from temp file): '$_FILE_OUTPUT'" >> "$LOG_FILE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - DEBUG: file command exit code (from temp file): '$_FILE_EXIT_CODE'" >> "$LOG_FILE"

        MIME_TYPE_OUTPUT="$_FILE_OUTPUT"
        MIME_TYPE_EXIT_CODE="$_FILE_EXIT_CODE"

        if [ "$MIME_TYPE_EXIT_CODE" -ne 0 ]; then
            log_message "Ошибка: Команда 'file' завершилась с ошибкой ($MIME_TYPE_EXIT_CODE) для файла \"$FILENAME\". Вывод: $MIME_TYPE_OUTPUT. Пропускаю." ERROR
            continue
        fi
        MIME_TYPE="$MIME_TYPE_OUTPUT"
        log_message "MIME-тип файла \"$FILENAME\": $MIME_TYPE"
        if [[ "$MIME_TYPE" == audio/* || "$MIME_TYPE" == video/* ]]; then
            log_message "Файл \"$FILENAME\" является аудио/видео. Начинаю обработку."
            log_message "Вызов obsidian-ai-transcribe.sh для файла: $FULL_PATH"
            
            # Вызов основного скрипта обработки
            # Предполагается, что obsidian-ai-transcribe.sh находится в той же директории
            ./obsidian-ai-transcribe.sh "$FULL_PATH"
            EXIT_CODE=$?

            if [ $EXIT_CODE -eq 0 ]; then
                log_message "Успешная обработка файла \"$FILENAME\". Удаляю исходный файл."
                rm "$FULL_PATH"
            else
                log_message "Ошибка при обработке файла \"$FILENAME\". Код выхода: $EXIT_CODE. Файл не будет удален." ERROR
            fi
        else
            log_message "Файл \"$FILENAME\" не является аудио/видео ($MIME_TYPE). Пропускаю."
        fi
    done
    sleep $SLEEP_INTERVAL
done
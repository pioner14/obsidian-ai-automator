#!/bin/bash

# --- КОНФИГУРАЦИЯ ---
WATCH_DIR="/media/windows/ai-automator/" # Укажите путь к папке для мониторинга
LOG_FILE="$(dirname "$0")/.watch_and_transcribe.log"

# --- ФУНКЦИИ ---
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# --- ОСНОВНАЯ ЛОГИКА ---
log_message "Запуск скрипта мониторинга папки: $WATCH_DIR"

# Проверка наличия inotifywait
if ! command -v inotifywait &> /dev/null
then
    log_message "Ошибка: inotifywait не найден. Пожалуйста, установите пакет inotify-tools."
    exit 1
fi

# Проверка существования папки для мониторинга
if [ ! -d "$WATCH_DIR" ]; then
    log_message "Ошибка: Папка для мониторинга \"$WATCH_DIR\" не существует. Создайте ее или укажите правильный путь."
    exit 1
fi

log_message "Начало мониторинга папки \"$WATCH_DIR\" на предмет новых видео/аудио файлов..."

inotifywait -m -e create -e moved_to --format "%f" "$WATCH_DIR" | while read -r FILENAME
do
    FULL_PATH="$WATCH_DIR/$FILENAME"
    log_message "Обнаружен новый файл: $FULL_PATH"

    # Проверка, является ли файл видео или аудио
    MIME_TYPE=$(file --mime-type -b "$FULL_PATH")
    if [[ "$MIME_TYPE" == audio/* || "$MIME_TYPE" == video/* ]]; then
        log_message "Файл \"$FILENAME\" является аудио/видео. Начинаю обработку."
        
        # Вызов основного скрипта обработки
        # Предполагается, что obsidian-ai-transcribe.sh находится в той же директории
        ./obsidian-ai-transcribe.sh "$FULL_PATH"
        EXIT_CODE=$?

        if [ $EXIT_CODE -eq 0 ]; then
            log_message "Успешная обработка файла \"$FILENAME\". Удаляю исходный файл."
            rm "$FULL_PATH"
        else
            log_message "Ошибка при обработке файла \"$FILENAME\". Код выхода: $EXIT_CODE. Файл не будет удален."
        fi
    else
        log_message "Файл \"$FILENAME\" не является аудио/видео ($MIME_TYPE). Пропускаю."
    fi
done

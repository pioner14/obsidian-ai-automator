#!/bin/bash
# Скрипт-обертка для автоматизации:

INPUT_VIDEO=$1

if [ -z "$INPUT_VIDEO" ]; then
    echo "Usage: $0 /path/to/video.mp4"
    exit 1
fi



# 1. Транскрипция с Deepgram API и анализ LLM (Ollama) и запись в Obsidian
echo "-> 1/2: Транскрипция (Deepgram API) и анализ LLM (NVIDIA API) и запись в Obsidian..."
PYTHON_SCRIPT_PATH="$(pwd)/scripts/ai_analyzer.py" 
CREATED_MARKDOWN_PATH=$(source venv/bin/activate && python "$PYTHON_SCRIPT_PATH" "$INPUT_VIDEO")
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ] && [ -n "$CREATED_MARKDOWN_PATH" ]; then
    echo "Markdown файл успешно создан: $CREATED_MARKDOWN_PATH"
    if [ -f "$CREATED_MARKDOWN_PATH" ]; then
        echo "-> 2/2: Удаление исходного видеофайла: $INPUT_VIDEO"
        rm "$INPUT_VIDEO"
        echo "Исходный видеофайл удален."
    else
        echo "Ошибка: Созданный Markdown файл не найден по пути: $CREATED_MARKDOWN_PATH. Исходный видеофайл не будет удален."
    fi
else
    echo "Ошибка при создании Markdown файла. Исходный видеофайл не будет удален."
    exit $EXIT_CODE
fi

echo "Готово. Заметка синхронизирована через Syncthing."
#!/bin/bash
# Скрипт-обертка для автоматизации:

INPUT_VIDEO=$1

if [ -z "$INPUT_VIDEO" ]; then
    echo "Usage: $0 /path/to/video.mp4"
    exit 1
fi

# Проверка, что Ollama запущен
if ! curl -s http://localhost:11434 > /dev/null; then
    echo "ERROR: Ollama server is not running. Please run 'ollama serve' in a separate terminal."
    exit 1
fi

# 1. Извлечение Аудио в /tmp
AUDIO_FILE="/tmp/$(basename "$INPUT_VIDEO" | sed 's/\.[^.]*$//' | sed 's/[^a-zA-Z0-9_]/-/g').wav"
echo "-> 1/3: Извлечение аудио из $INPUT_VIDEO..."
# Извлекаем моно-аудио, 16kHz для лучшей работы Whisper
ffmpeg -i "$INPUT_VIDEO" -vn -acodec pcm_s16le -ar 16000 -ac 1 -y "$AUDIO_FILE"

# 2. Вызов Python-анализатора для транскрипции и записи в Obsidian
echo "-> 2/3: Транскрипция (Faster-Whisper) и анализ LLM (Ollama) и запись в Obsidian..."
PYTHON_SCRIPT_PATH="$(pwd)/scripts/ai_analyzer.py" 
source venv/bin/activate && python "$PYTHON_SCRIPT_PATH" "$AUDIO_FILE"

# Очистка временных файлов
rm "$AUDIO_FILE"
echo "Готово. Заметка синхронизирована через Syncthing."
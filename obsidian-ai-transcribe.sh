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
ffmpeg -i "$INPUT_VIDEO" -vn -acodec pcm_s16le -ar 16000 -ac 1 -y "$AUDIO_FILE" 2>/dev/null

# 2. Транскрипция с Whisper.cpp (Large-v3, Русский, GPU)
TRANSCRIPT_JSON="/tmp/$(basename "$INPUT_VIDEO" | sed 's/\.[^.]*$//' | sed 's/[^a-zA-Z0-9_]/-/g').json"
WHISPER_CMD="/usr/bin/whisper.cpp-cuda" # Исполняемый файл CUDA-версии
# ! ОБНОВИТЕ ПУТЬ К МОДЕЛИ! Проверьте реальный путь на вашей системе
WHISPER_MODEL_PATH="/usr/share/whisper-cpp/models/ggml-large-v3.bin" 

echo "-> 2/3: Транскрипция с Large-v3 (GPU)..."
# -oj: вывод в JSON, -t: потоки (для i5 4-ядерного процессора, -t 8 - это 8 потоков)
# -p 1 -c 1: для ускорения на CUDA-ядрах
"$WHISPER_CMD" -m "$WHISPER_MODEL_PATH" -l ru -f "$AUDIO_FILE" -oj -t 8 -p 1 -c 1 2>/dev/null 

# 3. Вызов Python-анализатора и запись в Obsidian
echo "-> 3/3: Анализ LLM (Ollama) и запись в Obsidian..."
PYTHON_SCRIPT_PATH="$(pwd)/scripts/ai_analyzer.py" 
python "$PYTHON_SCRIPT_PATH" "$TRANSCRIPT_JSON"

# Очистка временных файлов
rm "$AUDIO_FILE"
rm "$TRANSCRIPT_JSON"
echo "Готово. Заметка синхронизирована через Syncthing."

#!/bin/bash
# Скрипт-обертка для автоматизации:

INPUT_VIDEO=$1

if [ -z "$INPUT_VIDEO" ]; then
    echo "Usage: $0 /path/to/video.mp4"
    exit 1
fi

# Проверка, что Ollama запущен (пока оставляем, но скоро заменим на облачный LLM)
if ! curl -s http://localhost:11434 > /dev/null; then
    echo "ERROR: Ollama server is not running. Please run 'ollama serve' in a separate terminal."
    exit 1
fi

# 1. Транскрипция с Deepgram API и анализ LLM (Ollama) и запись в Obsidian
echo "-> 1/2: Транскрипция (Deepgram API) и анализ LLM (Ollama) и запись в Obsidian..."
PYTHON_SCRIPT_PATH="$(pwd)/scripts/ai_analyzer.py" 
# Явно передаем DEEPGRAM_API_KEY в окружение Python-скрипта
source venv/bin/activate && DEEPGRAM_API_KEY="$DEEPGRAM_API_KEY" python "$PYTHON_SCRIPT_PATH" "$INPUT_VIDEO"

# Очистка временных файлов (если ai_analyzer.py создает их)
# В данном случае, Deepgram обрабатывает видео напрямую, поэтому временный аудиофайл не создается здесь.
echo "Готово. Заметка синхронизирована через Syncthing."
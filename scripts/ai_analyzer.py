import sys
import json
import requests
import os
import re
import logging
from faster_whisper import WhisperModel

# --- КОНФИГУРАЦИЯ ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:mini" 
OBSIDIAN_VAULT_PATH = os.path.expanduser("/home/nick/Obsidian Vault/Auto_Notes") 
WHISPER_MODEL_SIZE = "tiny" # Используем tiny, faster-whisper будет управлять устройством
# ---------------------

def transcribe_audio_with_faster_whisper(audio_path):
    """Транскрибирует аудиофайл с помощью faster-whisper, используя GPU или CPU."""
    # Принудительное использование CPU для Faster-Whisper, чтобы избежать проблем с VRAM
    model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    logging.info(f"Faster-Whisper: Принудительно используется CPU ({WHISPER_MODEL_SIZE}, int8).")

    segments, info = model.transcribe(audio_path, beam_size=5, language="ru")
    
    full_text = []
    for segment in segments:
        start_time = str(int(segment.start // 3600)).zfill(2) + ':' + \
                     str(int((segment.start % 3600) // 60)).zfill(2) + ':' + \
                     str(int(segment.start % 60)).zfill(2)
        full_text.append(f"[{start_time}] {segment.text.strip()}")
    
    return "\n".join(full_text)

def analyze_with_ollama(transcript):
    """Отправляет транскрипт в Ollama и получает структурированный Markdown."""
    
    prompt = f"""Ты — ИИ-аналитик, помогающий исследователю из Общества Сторожевой Башни. 
    Твоя задача — проанализировать стенограмму лекции на русском языке, чтобы найти ключевые "наглядные пособия" или "примеры" для дальнейшего исследования.

    Выполни 3 шага:
    1. **Заголовок:** Сгенерируй краткий и точный заголовок (не более 10 слов) из транскрипта.
    2. **Примеры:** Выдели **3-5** наиболее ярких наглядных примеров (иллюстраций), которые использовал спикер. Укажи **тайм-код** (в формате HH:MM:SS) начала каждого примера из транскрипта.
    3. **Формат:** Отформатируй ВСЕ в формат Obsidian Markdown, используя YAML Frontmatter и Callouts. **Не включай ничего, кроме запрошенного Markdown**.

    ---
    ### ТРЕБУЕМЫЙ ФОРМАТ OBSIDIAN ###
    ```markdown
    ---
    title: [Твой сгенерированный заголовок]
    tags: [jw, research, transcript, {OLLAMA_MODEL}]
    ---

    ## Анализ: Ключевые Примеры (Наглядные Пособия)

    > [!example|collapse open] [Название Примера, HH:MM:SS]
    > [Твой краткий пересказ Примера, должен быть коротким]

    > [!example|collapse open] [Название Второго Примера, HH:MM:SS]
    > [Твой краткий пересказ Второго Примера, должен быть коротким]
    
    ## Полный Транскрипт
    ```
    ---
    
    ### ТРАНСКРИПТ ДЛЯ АНАЛИЗА:
    {transcript}
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('response', '')
    except Exception as e:
        return f"Error communicating with Ollama: {e}"

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("ai_analyzer.log"),
                            logging.StreamHandler()
                        ])
    logging.info("Запуск скрипта ai_analyzer.py")
    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <path_to_audio.wav>")
        sys.exit(1)

    audio_path = sys.argv[1]
    
    logging.info(f"Начало транскрипции аудио: {audio_path}...")
    transcript_with_timecodes = transcribe_audio_with_faster_whisper(audio_path)
    logging.info("Транскрипция завершена.")
    
    if not transcript_with_timecodes:
        logging.error("Ошибка: Транскрипция не удалась или вернула пустой результат.")
        sys.exit(1)

    logging.info("Начало анализа LLM (Ollama)...")
    markdown_output = analyze_with_ollama(transcript_with_timecodes)
    logging.info("Анализ LLM завершен.")
    
    if markdown_output.startswith("Error"):
        logging.error(f"Ошибка LLM-анализа: {markdown_output}")
        sys.exit(1)

    title_line = next((line for line in markdown_output.split('\n') if line.startswith('title:')), None)
    if title_line:
        file_title = title_line.split('title:')[1].strip().strip('[]')
        safe_filename = re.sub(r'[^\w\s-]', '', file_title).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        filename = f"{safe_filename}.md"
    else:
        filename = f"LLM_Analysis_Error_{os.path.basename(audio_path).replace('.wav', '.md')}"

    output_path = os.path.join(OBSIDIAN_VAULT_PATH, filename)
    os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    logging.info(f"Успех. Obsidian заметка создана: {output_path}")

if __name__ == "__main__":
    main()
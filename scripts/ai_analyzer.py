import sys
import json
import requests
import os
import re
import logging

# --- КОНФИГУРАЦИЯ ---
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "nvidia/nemotron-4-340b-instruct" # Или другая подходящая модель NVIDIA
OBSIDIAN_VAULT_PATH = os.path.expanduser("/home/nick/Obsidian Vault/Auto_Notes")
TRANSCRIPT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".deepgram_cache")
# ---------------------


def transcribe_with_deepgram(video_path):
    """Транскрибирует видеофайл с помощью Deepgram API, используя кэширование."""
    if not DEEPGRAM_API_KEY:
        logging.error("Ошибка: DEEPGRAM_API_KEY не установлен. Пожалуйста, создайте файл .deepgram_api_key и поместите в него ваш ключ.")
        sys.exit(1)

    # Создаем директорию для кэша, если ее нет
    os.makedirs(TRANSCRIPT_CACHE_DIR, exist_ok=True)

    # Генерируем имя кэш-файла на основе имени видеофайла
    video_filename = os.path.basename(video_path)
    cache_filename = os.path.join(TRANSCRIPT_CACHE_DIR, f"{video_filename}.json")

    # Проверяем, существует ли кэшированный транскрипт
    if os.path.exists(cache_filename):
        logging.info(f"Используем кэшированный транскрипт для {video_filename}")
        try:
            with open(cache_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Извлечение транскрипта с тайм-кодами из кэшированных данных
            full_text = []
            if 'results' in data and 'channels' in data['results'] and data['results']['channels']:
                for channel in data['results']['channels']:
                    for alternative in channel['alternatives']:
                        for word_info in alternative['words']:
                            start_time = str(int(word_info['start'] // 3600)).zfill(2) + ':' + \
                                         str(int((word_info['start'] % 3600) // 60)).zfill(2) + ':' + \
                                         str(int(word_info['start'] % 60)).zfill(2)
                            full_text.append(f"[{start_time}] {word_info['word'].strip()}")
            return " ".join(full_text)
        except Exception as e:
            logging.error(f"Ошибка при чтении кэш-файла {cache_filename}: {e}. Повторяем транскрипцию.")
            # Если кэш-файл поврежден, удаляем его и продолжаем без него
            os.remove(cache_filename)

    logging.info(f"Кэшированный транскрипт для {video_filename} не найден или поврежден. Выполняем транскрипцию с Deepgram API...")

    # URL для Deepgram API
    DEEPGRAM_URL = "https://api.deepgram.com/v1/listen?punctuate=true&diarize=true&language=ru&model=nova-2"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "video/mp4" # Или другой соответствующий MIME-тип видео
    }

    try:
        with open(video_path, 'rb') as video_file:
            response = requests.post(DEEPGRAM_URL, headers=headers, data=video_file)
            response.raise_for_status() # Вызывает исключение для ошибок HTTP

        data = response.json()
        
        # Сохраняем полный ответ Deepgram в кэш-файл
        with open(cache_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Транскрипт Deepgram сохранен в кэш: {cache_filename}")

        # Извлечение транскрипта с тайм-кодами
        full_text = []
        if 'results' in data and 'channels' in data['results'] and data['results']['channels']:
            for channel in data['results']['channels']:
                for alternative in channel['alternatives']:
                    for word_info in alternative['words']:
                        start_time = str(int(word_info['start'] // 3600)).zfill(2) + ':' + \
                                     str(int((word_info['start'] % 3600) // 60)).zfill(2) + ':' + \
                                     str(int(word_info['start'] % 60)).zfill(2)
                        full_text.append(f"[{start_time}] {word_info['word'].strip()}")
        
        return " ".join(full_text) # Deepgram возвращает слова, объединяем их
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при обращении к Deepgram API: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Неизвестная ошибка при транскрипции с Deepgram: {e}")
        sys.exit(1)

def analyze_with_nvidia_llm(transcript):
    """Отправляет транскрипт в NVIDIA API и получает структурированный Markdown."""
    if not NVIDIA_API_KEY:
        logging.error("Ошибка: NVIDIA_API_KEY не установлен. Пожалуйста, установите переменную окружения NVIDIA_API_KEY.")
        sys.exit(1)
    prompt = f"""Ты — ИИ-аналитик, помогающий исследователю из Общества Сторожевой Башни. 
    Твоя задача — проанализировать предоставленную стенограмму лекции на русском языке, чтобы найти ключевые "наглядные пособия" или "примеры" и объяснения библейских стихов для дальнейшего исследования.
    **Крайне важно:**
    1. Отвечай **ТОЛЬКО НА РУССКОМ ЯЗЫКЕ**.
    2. Используй только информацию из предоставленного транскрипта. Не генерируй информацию извне и не галлюцинируй.

    Выполни 3 шага:
    1. **Заголовок:** Сгенерируй краткий и точный заголовок (не более 10 слов) из транскрипта. Заголовок должен быть без квадратных скобок.
    2. **Примеры:** Выдели **3-5** наиболее ярких наглядных примеров (иллюстраций) и объяснений библейских стихов, которые использовал спикер. Укажи **тайм-код** (в формате HH:MM:SS) начала каждого примера из транскрипта.
    3. **Формат:** Отформатируй ВСЕ в формат Obsidian Markdown, используя YAML Frontmatter и Callouts. Добавь к каждому примеру **понятные теги**, которые помогут легко найти его в Obsidian (например, #БиблейскийПример, #НаглядноеПособие, #ОбъяснениеСтиха). **Не включай ничего, кроме запрошенного Markdown**.

    ---
    ### ТРЕБУЕМЫЙ ФОРМАТ OBSIDIAN ###
    ```markdown
    ---
    title: Твой сгенерированный заголовок
    tags: [jw, research, transcript, {NVIDIA_MODEL}]
    ---

    ## Анализ: Ключевые Примеры (Наглядные Пособия)

    > [!example|collapse open] [Название Примера, HH:MM:SS] #Тег1 #Тег2
    > [Твой краткий пересказ Примера, должен быть коротким]

    > [!example|collapse open] [Название Второго Примера, HH:MM:SS] #Тег3
    > [Твой краткий пересказ Второго Примера, должен быть коротким]
    
    ## Полный Транскрипт
    ```
    ---
    
    ### ТРАНСКРИПТ ДЛЯ АНАЛИЗА:
    {transcript}
    """
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": False
    }

    try:
        response = requests.post(NVIDIA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('choices')[0].get('message').get('content', '')
    except Exception as e:
        return f"Error communicating with NVIDIA API: {e}"

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("ai_analyzer.log"),
                            logging.StreamHandler()
                        ])
    logging.info("Запуск скрипта ai_analyzer.py")
    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <path_to_video.mp4>")
        sys.exit(1)

    video_path = sys.argv[1]
    
    logging.info(f"Начало транскрипции видео с Deepgram API: {video_path}...")
    transcript_with_timecodes = transcribe_with_deepgram(video_path)
    logging.info("Транскрипция завершена.")
    
    if not transcript_with_timecodes:
        logging.error("Ошибка: Транскрипция не удалась или вернула пустой результат.")
        sys.exit(1)

    logging.info("Начало анализа LLM (NVIDIA API)...")
    markdown_output = analyze_with_nvidia_llm(transcript_with_timecodes)
    logging.info("Анализ LLM (NVIDIA API) завершен.")
    
    if markdown_output.startswith("Error"):
        logging.error(f"Ошибка LLM-анализа: {markdown_output}")
        sys.exit(1)

    title_line = next((line for line in markdown_output.split('\n') if line.startswith('title:')), None)
    if title_line:
        file_title = title_line.split('title:')[1].strip()
        safe_filename = re.sub(r'[^\w\s-]', '', file_title).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        filename = f"{safe_filename}.md"
    else:
        filename = f"LLM_Analysis_Error_{os.path.basename(video_path).replace('.mp4', '.md')}"

    output_path = os.path.join(OBSIDIAN_VAULT_PATH, filename)
    os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    logging.info(f"Успех. Obsidian заметка создана: {output_path}")

if __name__ == "__main__":
    main()

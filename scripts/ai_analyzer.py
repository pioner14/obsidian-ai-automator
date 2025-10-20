import sys
import json
import requests
import os
import re

# --- КОНФИГУРАЦИЯ ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
# Используем рекомендованную модель, лучше следующую инструкциям
OLLAMA_MODEL = "phi3:mini" 
# ! ОБНОВИТЕ ПУТЬ !
OBSIDIAN_VAULT_PATH = os.path.expanduser("/home/nick/Obsidian_Vault/Auto_Notes") 
# ---------------------

def read_transcript(json_path):
    """Читает JSON-файл Whisper.cpp и возвращает полный текст с тайм-кодами."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        full_text = []
        for segment in data.get('segments', []):
            start = segment.get('start')
            text = segment.get('text').strip()
            # Формат для удобства LLM-анализа (HH:MM:SS)
            start_time = str(int(start // 3600)).zfill(2) + ':' + \
                         str(int((start % 3600) // 60)).zfill(2) + ':' + \
                         str(int(start % 60)).zfill(2)
            full_text.append(f"[{start_time}] {text}")
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading transcript: {e}")
        return None

def analyze_with_ollama(transcript):
    """Отправляет транскрипт в Ollama и получает структурированный Markdown."""
    
    # Ключевой промпт для LLM! Направляет Phi-3 на нужный формат.
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
        "options": {"temperature": 0.3} # Уменьшаем креативность, увеличиваем точность
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('response', '')
    except Exception as e:
        return f"Error communicating with Ollama: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <path_to_transcript.json>")
        sys.exit(1)

    transcript_json_path = sys.argv[1]
    transcript_with_timecodes = read_transcript(transcript_json_path)
    
    if not transcript_with_timecodes:
        sys.exit(1)

    # 1. Запуск Ollama для анализа
    markdown_output = analyze_with_ollama(transcript_with_timecodes)
    
    if markdown_output.startswith("Error"):
        print(f"Ошибка LLM-анализа: {markdown_output}")
        sys.exit(1)

    # 2. Извлечение заголовка для имени файла
    title_line = next((line for line in markdown_output.split('\n') if line.startswith('title:')), None)
    if title_line:
        file_title = title_line.split('title:')[1].strip().strip('[]')
        # Очистка заголовка от символов для безопасного имени файла
        safe_filename = re.sub(r'[^\w\s-]', '', file_title).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        filename = f"{safe_filename}.md"
    else:
        filename = f"LLM_Analysis_Error_{os.path.basename(transcript_json_path).replace('.json', '.md')}"

    # 3. Запись в Obsidian Vault (Syncthing подхватит)
    output_path = os.path.join(OBSIDIAN_VAULT_PATH, filename)
    os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f"Успех. Obsidian заметка создана: {output_path}")

if __name__ == "__main__":
    main()

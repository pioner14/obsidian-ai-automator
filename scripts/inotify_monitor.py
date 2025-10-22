import sys
import time
import logging
import os
import configparser
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- КОНФИГУРАЦИЯ ---
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

WATCH_DIR = os.path.expanduser(config.get('Paths', 'watch_directory'))
OBSIDIAN_TRANSCRIBE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "obsidian-ai-transcribe.sh")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".inotify_monitor.log")
# --------------------

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler(LOG_FILE),
                        logging.StreamHandler()
                    ])

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            logging.info(f"Обнаружен новый файл: {file_path}")
            self.process_file(file_path)

    def process_file(self, file_path):
        allowed_extensions_str = config.get('File_Filtering', 'allowed_extensions', fallback='')
        allowed_extensions = [ext.strip() for ext in allowed_extensions_str.split(',') if ext.strip()]

        file_extension = os.path.splitext(file_path)[1].lower()

        if allowed_extensions and file_extension not in allowed_extensions:
            logging.info(f"Файл {file_path} имеет неподдерживаемое расширение ({file_extension}). Пропускаю.")
            return
        
        logging.info(f"Начинаю обработку файла: {file_path}")
        # Вызываем основной скрипт обработки
        # Убедитесь, что obsidian-ai-transcribe.sh имеет права на выполнение
        command = [OBSIDIAN_TRANSCRIBE_SCRIPT, file_path]
        logging.info(f"Запуск обработки файла {file_path} в фоновом режиме: {' '.join(command)}")
        try:
            subprocess.Popen(command) 
            logging.info(f"Файл {file_path} передан для фоновой обработки.")
        except Exception as e:
            logging.error(f"Ошибка при запуске обработки файла {file_path}: {e}")

def main():
    logging.info(f"Запуск мониторинга папки: {WATCH_DIR} с inotify...")
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Мониторинг остановлен.")

if __name__ == "__main__":
    main()
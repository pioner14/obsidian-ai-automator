import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- КОНФИГУРАЦИЯ ---
WATCH_DIR = os.path.expanduser("/home/nick/Public/ai-automator/")
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
        # Проверяем, является ли файл видео или аудио (можно улучшить)
        # Для простоты пока полагаемся на расширение или MIME-тип, если это возможно
        # В будущем можно использовать команду 'file' или более продвинутые методы
        
        # Простой пример: если файл не является временным или скрытым
        if not os.path.basename(file_path).startswith('.') and not file_path.endswith('~'):
            logging.info(f"Начинаю обработку файла: {file_path}")
            # Вызываем основной скрипт обработки
            # Убедитесь, что obsidian-ai-transcribe.sh имеет права на выполнение
            command = f"{OBSIDIAN_TRANSCRIBE_SCRIPT} "{file_path}""
            logging.info(f"Выполнение команды: {command}")
            try:
                # Запускаем скрипт в отдельном процессе, чтобы не блокировать монитор
                os.system(command) 
                logging.info(f"Обработка файла {file_path} завершена.")
            except Exception as e:
                logging.error(f"Ошибка при обработке файла {file_path}: {e}")

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

import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_EXTENSIONS = ('.py',)
WATCHED_DIR = "."

class ReloadOnChange(FileSystemEventHandler):
    def __init__(self):
        self.proc = self.start_proc()

    def start_proc(self):
        print("Starting simulator...")
        return subprocess.Popen(['python', 'main.py'])

    def restart_proc(self):
        print("Restarting simulator...")
        self.proc.terminate()
        self.proc.wait()
        self.proc = self.start_proc()

    def on_modified(self, event):
        if event.src_path.endswith(WATCHED_EXTENSIONS):
            self.restart_proc()

if __name__ == "__main__":
    event_handler = ReloadOnChange()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.proc.terminate()
    observer.join()
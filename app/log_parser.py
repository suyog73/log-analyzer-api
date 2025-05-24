import os
import uuid
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIRECTORY = os.path.join(BASE_DIR, "logs")
LOG_FORMAT = "%Y-%m-%d %H:%M:%S"

class LogEntry:
    def __init__(self, timestamp, level, component, message):
        raw_string = f"{timestamp}{level}{component}{message}"
        self.id = hashlib.md5(raw_string.encode()).hexdigest()
        self.timestamp = timestamp
        self.level = level
        self.component = component
        self.message = message

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime(LOG_FORMAT),
            "level": self.level,
            "component": self.component,
            "message": self.message
        }

def load_logs():
    logs = []
    for filename in os.listdir(LOG_DIRECTORY):
        filepath = os.path.join(LOG_DIRECTORY, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) != 4:
                        continue  # Skip malformed lines
                    try:
                        timestamp = datetime.strptime(parts[0], LOG_FORMAT)
                        level = parts[1]
                        component = parts[2]
                        message = parts[3]
                        logs.append(LogEntry(timestamp, level, component, message))
                    except Exception:
                        continue
    return logs

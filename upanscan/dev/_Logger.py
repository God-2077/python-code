import sys
import os
import datetime
from rich.console import Console

# logger
class Logger:
    def __init__(self, log_file_path: str =None, encode: str = "utf-8"):
        self.console = Console()
        self.log_file_path = log_file_path
        if self.log_file_path != None:
            self.f = open(self.log_file_path, "a", encoding=encode)
        else:
            self.f = None

    def _print(self, msg, level="INFO"):
        level = "WARN" if level == "WARNING" else level
        supported_levels = ["INFO", "DEBUG", "WARN", "ERROR"]
        if level not in supported_levels:
            level = "INFO"
            self._print(f"Invalid level: {level}", level="WARN")

        time = datetime.datetime.now()
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        colors = {"INFO": "green", "DEBUG": "#808080", "WARN": "yellow", "ERROR": "red"}

        str = f"{formatted_time} {level.ljust(5)} {msg}"
        console_str = f"[#808080]{formatted_time}[/#808080] [{colors[level]}]{level.ljust(5)}[/{colors[level]}] {msg}"

        self.console.print(console_str)
        self._write_file(str)

    def _write_file(self, msg):
        if self.log_file_path != None and self.f != None:
            self.f.write(msg + "\n")
            self.f.flush()

    def info(self, msg):
        self._print(msg, level="INFO")

    def debug(self, msg):
        self._print(msg, level="DEBUG")
    
    def error(self, msg):
        self._print(msg, level="ERROR")

    def warning(self, msg):
        self._print(msg, level="WARN")
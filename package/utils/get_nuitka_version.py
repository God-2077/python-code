# -*- coding: utf-8 -*-
# language: English
import subprocess
import sys
import logging
import datetime
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent

log_dir = base_dir / 'log'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'get_nuitka_version.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=str(log_file),
    filemode='a',
    encoding='utf-8'
)

logging.info(f"Start get Nuitka version at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def get_nuitka_version():
    python_executable = sys.executable
    logging.info(f"Python executable: {python_executable}")
    logging.info(f"begin get Nuitka version")
    logging.info(f"runing command: {python_executable} -m nuitka --version")
    try:
        result = subprocess.run(
            [python_executable, '-m', 'nuitka', '--version'],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Get Nuitka version command exit code: {result.returncode}")
        logging.info(f"Nuitka version output:")
        logging.info(f"\n{result.stdout}")
        return parse_nuitka_version(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Get Nuitka version failed: {e}")
        return "unknown"

def parse_nuitka_version(version_str):
    # 版本号在第一行
    lines = version_str.splitlines()
    if lines:
        ver = lines[0].strip()
        logging.info(f"Nuitka version: {ver}")
        return ver
    return "unknown"

if __name__ == "__main__":
    try:
        version = get_nuitka_version()
    except Exception as e:
        logging.error(f"Error: {e}")
        version = "unknown"
    print(version)
    logging.info(f"End get Nuitka version at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

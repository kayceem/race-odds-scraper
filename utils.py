import os
import pytz
import random
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
load_dotenv()

aest = pytz.timezone("Australia/Sydney")

def convert_to_aest(utc_timestamp):
    if not utc_timestamp:
        return ""
    utc_dt = datetime.fromtimestamp(int(utc_timestamp), tz=pytz.utc)
    return utc_dt.astimezone(aest).strftime("%H:%M:%S")

def get_today_str():
    return datetime.now(pytz.utc).astimezone(aest).strftime("%Y-%m-%d")


def setup_logger(name: str, log_file: str = "log.log"):
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", log_file)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) Gecko/20100101 Firefox/125.0",

        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",

        "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    ]

    return random.choice(USER_AGENTS)

def get_headers(type: str = "race"):
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }
        race_headers = {
            **headers,
            "Host": "www.punters.com.au",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://www.odds.com.au/",
            "Origin": "https://www.odds.com.au",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
        }
        event_headers = {
            **headers,
            "priority": "u=1, i",
            "referer": "https://www.odds.com.au/horse-racing/",
        }
        return race_headers if type == "race" else event_headers
from logging import config
import json

with open("telegram.json") as file:
    TELEGRAM_CONFIG = json.load(file)

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "telegram": {
            "class": "python_telegram_logger.Handler",
            "token": TELEGRAM_CONFIG["token"],
            "chat_ids": TELEGRAM_CONFIG["log_chat_ids"],
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["telegram",]
    }
}

def set_config():
    config.dictConfig(config=log_config)

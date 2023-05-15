import os
import logging
import pathlib
from logging import config
from logging.handlers import QueueHandler
import json
from uuid import uuid4
from googletrans import Translator
from python_telegram_logger.handlers import (
    Handler,
    LogMessageDispatcher,
    Queue,
    FORMATTERS,
    HTML,
)

try:
    with open(
        os.path.join(pathlib.Path(__file__).parent.resolve(), "telegram.json")
    ) as file:
        TELEGRAM_CONFIG = json.load(file)
except FileNotFoundError:
    TELEGRAM_CONFIG = {}


class HindiTelegramDispatcher(LogMessageDispatcher):
    """Translates the messages to hindi first"""

    src = "en"
    dest = "hi"
    translator = Translator()

    def handle(self, record):
        record.msg = self.translator.translate(
            record.msg, src=self.src, dest=self.dest
        ).text
        return super().handle(record)


class HindiTelegramHandler(Handler):
    """Uses HindiTelegramDispatcher"""

    def __init__(
        self,
        token: str,
        chat_ids: list,
        format: str = HTML,
        disable_notifications: bool = False,
        disable_preview: bool = False,
    ):
        queue = Queue()
        QueueHandler.__init__(self, queue)

        try:
            formatter = FORMATTERS[format.lower()]
        except Exception:
            raise Exception("TelegramLogging. Unknown format '%s'" % format)

        self.handler = HindiTelegramDispatcher(
            token, chat_ids, disable_notifications, disable_preview
        )
        self.handler.setFormatter(formatter())
        listener = logging.handlers.QueueListener(queue, self.handler)
        listener.start()


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "telegram": {
            "class": "python_telegram_logger.Handler",
            "token": TELEGRAM_CONFIG.get("token"),
            "chat_ids": TELEGRAM_CONFIG.get("log_chat_ids"),
        },
        "telegram_hindi": {
            "class": "wautomark.telegram.HindiTelegramHandler",
            "token": TELEGRAM_CONFIG.get("token"),
            "chat_ids": TELEGRAM_CONFIG.get("log_chat_ids_hindi"),
        },
    },
    "loggers": {
        "tg": {
            "level": "INFO",
            "handlers": [
                "telegram",
                "telegram_hindi",
            ],
        }
    },
}


def set_config():
    if TELEGRAM_CONFIG:
        config.dictConfig(config=log_config)

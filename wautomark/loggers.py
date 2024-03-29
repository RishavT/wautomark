"""Contains logging config"""

from datetime import datetime, timedelta
import logging
import sys
from proglog import ProgressBarLogger, TqdmProgressBarLogger

from .telegram import set_config

set_config()

logger = logging.getLogger("wautomark")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
tg_logger = logging.getLogger("tg")
tg_logger.addHandler(logging.StreamHandler(sys.stdout))


class CustomProgressLogger(TqdmProgressBarLogger):
    additional_loggers = [logger, tg_logger]

    def __init__(
        self,
        *args,
        additional_loggers_prefix="",
        **kwargs,
    ):
        self.additional_loggers_prefix = additional_loggers_prefix
        self.mybars = {}
        super().__init__(*args, **kwargs)

    def log(self, message):
        pass

    def log_bar_progress(self, barname):
        """Logs the progress of a bar"""
        # We will log in chunks of 10%
        bar = self.mybars.get(barname)
        if not bar:
            return
        prog_in_percent = bar["index"] * 100.0 / bar["total"]
        last_log_time = bar.get("last_log_time")
        current_log_time = datetime.now()
        if last_log_time is None or (last_log_time - current_log_time) > timedelta(
            minutes=2
        ):
            bar["last_log_time"] = current_log_time
            for adlogger in self.additional_loggers:
                adlogger.info(
                    "%s Progress of our video conversion is: %s %%",
                    self.additional_loggers_prefix,
                    str(prog_in_percent),
                )

    def bars_callback(self, bar, attr, value, old_value=None):
        if bar != "t":
            return  # We just want the total progress
        if attr == "total":
            # This is the start of a new bar
            self.mybars[bar] = {
                "total": value,
                "index": -1,
            }
        elif attr == "index":
            self.mybars[bar]["index"] = value
        self.log_bar_progress(bar)

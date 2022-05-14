"""Contains logging config"""

import logging
import sys
from proglog import ProgressBarLogger, TqdmProgressBarLogger

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

    def log_additional_loggers(self, message):
        for adlogger in self.additional_loggers:
            adlogger.info(f"{self.additional_loggers_prefix}%s", message)

    def log(self, message):
        pass

    def log_bar_progress(self, barname):
        """Logs the progress of a bar"""
        # We will log in chunks of 10%
        bar = self.mybars.get(barname)
        if not bar:
            return
        prog_in_percent = bar["index"] * 100.0 / bar["total"]
        prog_in_quarters = int(prog_in_percent / 25)
        old_prog_in_quarters = bar.get("prog_in_quarters", 0)
        if prog_in_quarters > old_prog_in_quarters:
            bar["prog_in_quarters"] = prog_in_quarters
            self.log_additional_loggers(
                f"Progress of our video conversion is: {prog_in_quarters * 25}%"
            )

    def bars_callback(self, bar, attr, value, old_value=None):
        if bar != "t":
            return  # We just want the total progress
        if attr == "total":
            # This is the start of a new bar
            self.mybars[bar] = {
                "total": value,
                "index": 0,
            }
            self.log_additional_loggers("Progress of our video conversion is: 0%")
        elif attr == "index":
            self.mybars[bar]["index"] = value
            self.log_bar_progress(bar)

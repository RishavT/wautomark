"""Contains logging config"""

import logging
import sys

logger = logging.getLogger("wautomark")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
tg_logger = logging.getLogger("tg")
tg_logger.addHandler(logging.StreamHandler(sys.stdout))

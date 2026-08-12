"""Logging with per-level colors. Requires: pip install colorama"""

import logging

from colorama import Back, Fore, Style, init

# wrap the stdout/stdout streams: translates ANSI codes on old Windows consoles,
# and strips them automatically when the output is redirected to a file or a pipe.
# must run before StreamHandler() is built — the handler grabs sys.stderr at construction time.
init()

LEVEL_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.WHITE + Back.RED,
}


class ColorFormatter(logging.Formatter):
    """Same layout as the plain formatter, but the level name is colored."""

    def format(self, record):
        color = LEVEL_COLORS.get(record.levelno, "")
        # copy: mutating the record would leak the escape codes into the file handler,
        # since both handlers format the same record object
        colored = logging.makeLogRecord(record.__dict__)
        # pad before coloring: %(levelname)-8s would count the invisible escape codes
        colored.levelname = f"{color}{record.levelname:<8}{Style.RESET_ALL}"
        return super().format(colored)


class FileHandler(logging.FileHandler):
    def __init__(self, path):
        super().__init__(path, encoding="utf-8")
        self.setLevel(logging.INFO)


FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
COLOR_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"  # padding is applied by the formatter

file_handler = FileHandler("app.log")
file_handler.setFormatter(logging.Formatter(FORMAT))

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(ColorFormatter(COLOR_FORMAT))

# root logger must be at DEBUG so records reach handlers;
# each handler then applies its own level filter
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])

logger = logging.getLogger(__name__)

logger.debug("debug message")
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("unhandled error while dividing")

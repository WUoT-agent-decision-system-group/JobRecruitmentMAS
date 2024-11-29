import logging
import logging.config
import sys
from pathlib import Path


class LogConfig:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Loads logger config"""

        log_file = Path("/app/logs") / f"{name}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(name)

        file_handler = LogConfig.__get_file_handler(log_file)
        console_handler = LogConfig.__get_console_handler()
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)

        return logger

    @staticmethod
    def __get_file_handler(log_file: Path) -> logging.FileHandler:
        file_handler = logging.FileHandler(log_file)
        # file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LogConfig.__get_formatter())
        return file_handler

    @staticmethod
    def __get_console_handler() -> logging.FileHandler:
        file_handler = logging.StreamHandler(sys.stdout)
        # file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LogConfig.__get_formatter())
        return file_handler

    @staticmethod
    def __get_formatter() -> logging.Formatter:
        return logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(name)s] %(levelname)s: %(message)s")

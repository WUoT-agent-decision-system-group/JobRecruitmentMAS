import json
import logging
import logging.config
from pathlib import Path

CONFIG_FILE = "app/logging-config.json"


class LogConfig:
    @staticmethod
    def load_config(name: str):
        """Loads logger config"""

        with open(CONFIG_FILE, 'r', encoding='utf-8') as cfg:
            config = json.load(cfg)

        log_file = Path("/app/logs") / f"{name}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        config["handlers"]["file"]["filename"] = str(log_file)

        logging.config.dictConfig(config)

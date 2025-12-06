import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir="./logs"):
    """Setup logger"""
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = pathlib.Path(log_dir) / "editor.log"
        logger = logging.getLogger('Phoenix Editor')
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler = RotatingFileHandler(str(log_file), maxBytes=1024 * 1024, backupCount=5)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger
    except Exception as e:
        print(f"Failed to setup logger: {e}")
        return None
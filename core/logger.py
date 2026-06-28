import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def get_logger(name="AldyConverter"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        if sys.platform == 'win32':
            app_data = os.getenv('APPDATA')
        else:
            app_data = os.path.expanduser('~')
            
        log_dir = os.path.join(app_data, 'AldyConverter')
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'app.log')
            
            handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception as e:
            print(f"Failed to setup file logger: {e}")
            
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console)
        
    return logger

logger = get_logger()
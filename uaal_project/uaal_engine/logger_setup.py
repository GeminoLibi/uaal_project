# ua_al_engine/logger_setup.py

import logging
import sys

def setup_logger():
    """
    Sets up a global logger to write to 'uaal_session.log' and the console.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Capture messages of level INFO and above

    # Avoid adding handlers if they already exist (important for re-runs)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a formatter to define the log message structure
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create a handler to write logs to a file (mode='w' overwrites the file each run)
    file_handler = logging.FileHandler('uaal_session.log', mode='w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create a handler to also print logs to the console
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

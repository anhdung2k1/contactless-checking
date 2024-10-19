# logger.py
import logging

def setup_logger(level=logging.INFO):
    """Setup a standalone logger that logs only to the console."""
    logger = logging.getLogger(str(level))  # Use level as a unique name for the logger
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Add console handler if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger

# Define loggers for different levels
loggers = {
    "info": setup_logger(logging.INFO),
    "debug": setup_logger(logging.DEBUG),
    "error": setup_logger(logging.ERROR)
}

def info(message):
    """Log an info-level message."""
    loggers["info"].info(message)

def debug(message):
    """Log a debug-level message."""
    loggers["debug"].debug(message)

def error(message):
    """Log an error-level message."""
    loggers["error"].error(message)

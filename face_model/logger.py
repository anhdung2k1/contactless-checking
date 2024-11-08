import logging

def setup_logger(name="my_logger", level=logging.INFO):
    """Setup a standalone logger that logs only to the console."""
    logger = logging.getLogger(name)
    
    # Check if the logger has been set up to avoid duplication
    if not logger.hasHandlers():
        logger.setLevel(level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    return logger

# Create a logger instance
logger = setup_logger(level=logging.DEBUG)

# Define helper functions for logging at different levels
def info(message):
    """Log an info-level message."""
    logger.info(message)

def debug(message):
    """Log a debug-level message."""
    logger.debug(message)

def error(message):
    """Log an error-level message."""
    logger.error(message)
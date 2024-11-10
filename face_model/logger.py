import logging

def setup_logger(name="my_logger", level=logging.INFO, propagate=False):
    """Setup a standalone logger that logs only to the console."""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate
    
    # Check if the logger has been set up to avoid duplication
    if not logger.hasHandlers():
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    return logger

# Create a logger instance
logger = setup_logger(level=logging.DEBUG)

# Define helper functions for logging at different levels
def info(message, *args, **kwargs):
    """Log an info-level message."""
    logger.info(message, *args, **kwargs)

def debug(message, *args, **kwargs):
    """Log a debug-level message."""
    logger.debug(message, *args, **kwargs)

def error(message, exc_info=None, *args, **kwargs):
    """Log an error-level message."""
    logger.error(message, exc_info=exc_info, *args, **kwargs)
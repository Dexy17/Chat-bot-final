import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Auto-run setup when the logger is imported
def _setup_logger():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RotatingFileHandler(
                "log.log",
                maxBytes=1_000_000,  # 1MB per file
                backupCount=5,       # Keep 5 backups
            )
        ]
    )

# Run setup once
_setup_logger()

# Define functions to expose
def log_error(message: str, exc_info: bool = False):
    """Log an error with optional traceback."""
    logging.error(message, exc_info=exc_info)

# Optional: Add other log levels (e.g., warn, info)
def log_warning(message: str):
    logging.warning(message)

def log_info(message: str):
    logging.info(message)

def create_custom_logger(
    name: str,
    filename: str,
    level=logging.INFO,
    max_bytes=1_000_000,
    backup_count=5,
):
    """
    Creates a new logger with its own file and settings.
    
    Args:
        name: Unique name for the logger (e.g., 'debug_logger').
        filename: Log file path (e.g., 'debug.log').
        level: Logging level (e.g., logging.DEBUG).
        max_bytes: Max log file size before rotation.
        backup_count: Number of rotated backups to keep.
    
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    handler = RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger


symptom_logger = create_custom_logger(
    name="symptom_logger",
    filename="symptom.log",
    level=logging.DEBUG,  # Log ALL levels (DEBUG and above)
)
"""
Structured logging configuration with context and performance tracking.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add context if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data['user_id'] = user_id
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['data'] = record.extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET
        
        # Format: [TIME] LEVEL: message
        time_str = datetime.now().strftime('%H:%M:%S')
        levelname = f"{color}{record.levelname:8}{reset}"
        
        msg = f"[{time_str}] {levelname} {record.getMessage()}"
        
        # Add extra data if present
        if hasattr(record, 'extra_data'):
            msg += f" | {record.extra_data}"
        
        return msg


def setup_logging(
    log_level: str = "INFO",
    log_file: Path = None,
    json_logs: bool = False
):
    """
    Configure application logging
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logs
        json_logs: Use JSON format (True) or colored console (False)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_logs:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(ColoredConsoleFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with structured logging support"""
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter that adds extra data to log records"""
    
    def process(self, msg, kwargs):
        # Add extra data from kwargs
        if 'extra_data' in kwargs:
            extra = kwargs.pop('extra_data')
            kwargs.setdefault('extra', {})['extra_data'] = extra
        return msg, kwargs


def create_logger(name: str, **default_extra) -> LoggerAdapter:
    """
    Create a logger with default extra fields
    
    Example:
        logger = create_logger(__name__, component='generator')
        logger.info("Starting generation", extra_data={'project_id': 'P-123'})
    """
    base_logger = logging.getLogger(name)
    return LoggerAdapter(base_logger, default_extra)


# Example usage context manager
class LogContext:
    """Context manager for setting request/user context"""
    
    def __init__(self, request_id: str = None, user_id: str = None):
        self.request_id = request_id
        self.user_id = user_id
        self.tokens = []
    
    def __enter__(self):
        if self.request_id:
            self.tokens.append(request_id_var.set(self.request_id))
        if self.user_id:
            self.tokens.append(user_id_var.set(self.user_id))
        return self
    
    def __exit__(self, *args):
        for token in self.tokens:
            if self.request_id:
                request_id_var.reset(token)
            if self.user_id:
                user_id_var.reset(token)


# Performance logging decorator
import functools
import time

def log_performance(logger: logging.Logger):
    """Decorator to log function execution time"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                logger.info(
                    f"{func.__name__} completed",
                    extra={'extra_data': {'duration_sec': round(duration, 3)}}
                )
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(
                    f"{func.__name__} failed",
                    extra={'extra_data': {'duration_sec': round(duration, 3)}},
                    exc_info=True
                )
                raise
        return wrapper
    return decorator

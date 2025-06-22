"""
Centralized logging service for the application.
Provides structured JSON logging with configurable output destinations and log levels.
"""
import os
import sys
import logging
import datetime
from enum import Enum
from typing import Optional, Union, List, Dict, Any, Callable
from pathlib import Path

from loguru import logger as loguru_logger
from pydantic import BaseModel

from app.core.config_service import config_service


class LogLevel(str, Enum):
    """Log levels supported by the logging service."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig(BaseModel):
    """Configuration for the logging service."""
    level: LogLevel = LogLevel.INFO
    json_format: bool = True
    console_output: bool = True
    file_output: bool = False
    log_file_path: Optional[str] = None
    rotation: str = "20 MB"  # Size at which to rotate log files
    retention: str = "1 week"  # How long to keep log files
    compression: str = "zip"  # Compression format for rotated logs


class LoggingService:
    """
    Centralized logging service for the application.
    Provides structured JSON logging with configurable output destinations and log levels.
    """

    def __init__(self, config: Optional[LogConfig] = None):
        """
        Initialize the logging service with the given configuration.
        If no configuration is provided, it will be loaded from the config service.
        """
        self.config = config or self._load_config_from_service()
        self._configure_loguru()

    def _load_config_from_service(self) -> LogConfig:
        """Load logging configuration from the config service."""
        return LogConfig(
            level=LogLevel(config_service.get("log_level", "INFO").upper()),
            json_format=config_service.get("log_json_format", True),
            console_output=config_service.get("log_console_output", True),
            file_output=config_service.get("log_file_output", False),
            log_file_path=config_service.get("log_file_path"),
            rotation=config_service.get("log_rotation", "20 MB"),
            retention=config_service.get("log_retention", "1 week"),
            compression=config_service.get("log_compression", "zip"),
        )

    def _configure_loguru(self) -> None:
        """Configure loguru with the current settings."""
        # Remove default handlers
        loguru_logger.remove()

        # Define the log format based on configuration
        if self.config.json_format:
            # For JSON format, we'll use serialize=True and a custom function to format the JSON
            log_format = "{message}"
        else:
            log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

        # Add console handler if enabled
        if self.config.console_output:
            loguru_logger.add(
                sys.stdout,
                format=log_format,
                level=self.config.level.value,
                serialize=self.config.json_format,
                backtrace=True,
                diagnose=True,
            )

        # Add file handler if enabled
        if self.config.file_output and self.config.log_file_path:
            log_path = Path(self.config.log_file_path)

            # Create directory if it doesn't exist
            log_path.parent.mkdir(parents=True, exist_ok=True)

            loguru_logger.add(
                str(log_path),
                format=log_format,
                level=self.config.level.value,
                serialize=self.config.json_format,
                rotation=self.config.rotation,
                retention=self.config.retention,
                compression=self.config.compression,
                backtrace=True,
                diagnose=True,
            )

    def _serialize_record(self, record):
        """Serialize a log record for JSON output.

        This is used by loguru's serialize parameter to convert the record to a dict
        that can be serialized to JSON.
        """
        # Basic log data
        serialized = {
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "process_id": record["process"].id,
            "thread_id": record["thread"].id,
        }

        # Add exception info if available
        if record["exception"] is not None:
            serialized["exception"] = {
                "type": record["exception"].type,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback,
            }

        # Add all extra fields at the top level
        if record["extra"]:
            for key, value in record["extra"].items():
                # Don't overwrite standard fields
                if key not in serialized:
                    serialized[key] = value

        return serialized

    def get_logger(self, name: str) -> "Logger":
        """
        Get a logger for the given name.

        Args:
            name: The name of the logger, typically the module name.

        Returns:
            A Logger instance configured with the current settings.
        """
        return Logger(name, self.config)

    def update_config(self, config: LogConfig) -> None:
        """
        Update the logging configuration.

        Args:
            config: The new configuration to apply.
        """
        self.config = config
        self._configure_loguru()


class Logger:
    """
    Logger class that wraps loguru logger with additional functionality.
    """

    def __init__(self, name: str, config: LogConfig):
        """
        Initialize a logger with the given name and configuration.

        Args:
            name: The name of the logger, typically the module name.
            config: The logging configuration to use.
        """
        self.name = name
        self.config = config
        self.logger = loguru_logger.bind(name=name)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log an exception message with traceback."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).exception(message, **kwargs)

    def log(self, level: Union[str, int], message: str, **kwargs) -> None:
        """Log a message with the specified level."""
        # Use depth=1 to capture the caller's frame instead of this method
        self.logger.opt(depth=1).log(level, message, **kwargs)

    def bind(self, **kwargs) -> "Logger":
        """
        Bind contextual information to the logger.

        Args:
            **kwargs: Key-value pairs to bind to the logger.

        Returns:
            A new Logger instance with the bound context.
        """
        new_logger = Logger(self.name, self.config)
        # Bind the kwargs to the logger
        new_logger.logger = self.logger.bind(**kwargs)
        return new_logger


# Create a singleton instance of the logging service
logging_service = LoggingService()


def get_logger(name: str) -> Logger:
    """
    Get a logger for the given name.

    Args:
        name: The name of the logger, typically the module name.

    Returns:
        A Logger instance configured with the current settings.
    """
    return logging_service.get_logger(name)

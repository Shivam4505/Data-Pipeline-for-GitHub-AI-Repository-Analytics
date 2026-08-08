# GitHub AI Repository Analytics - Logging Configuration
import sys
import structlog
from structlog.types import EventDict, WrappedLogger
from typing import Any


def add_timestamp(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add timestamp to log entries."""
    from datetime import datetime, timezone
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def add_service_name(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add service name to log entries."""
    event_dict["service"] = "github-analytics-collector"
    return event_dict


def filter_secrets(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Filter out sensitive information from logs."""
    sensitive_keys = {"token", "password", "secret", "key", "authorization", "api_key"}
    for key in list(event_dict.keys()):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            event_dict[key] = "***REDACTED***"
    return event_dict


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structured logging."""
    
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_timestamp,
        add_service_name,
        filter_secrets,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("minio").setLevel(logging.WARNING)


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
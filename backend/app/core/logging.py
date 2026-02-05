"""
Logging configuration using structlog.

This module sets up structured logging for the application using structlog.
It provides:
- Pretty console output for development
- JSON output for production (machine-parseable)
- Request context binding for tracing
"""
import logging
import sys
from typing import Any, Dict, Optional

import structlog


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = False
) -> None:
    """
    Configure structured logging for the application.
    
    This function should be called once during application startup.
    It configures both standard library logging and structlog.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        json_logs: If True, output JSON formatted logs (for production)
                   If False, output pretty console logs (for development)
    """
    # Configure standard library logging
    # This ensures that logs from third-party libraries are also captured
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Shared processors that run for all log output formats
    shared_processors = [
        # Merge context variables from contextvars
        structlog.contextvars.merge_contextvars,
        # Add log level (info, warning, error, etc.)
        structlog.processors.add_log_level,
        # Add ISO format timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Render stack info if present
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        # Production: JSON output for log aggregators
        # (e.g., Datadog, Splunk, ELK stack)
        processors = shared_processors + [
            # Format exception info as string
            structlog.processors.format_exc_info,
            # Render final output as JSON
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Pretty console output with colors
        # Much easier to read during development
        processors = shared_processors + [
            # Pretty colored console output
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        # Filter logs below the specified level
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        # Use dict for context storage
        context_class=dict,
        # Use print logger factory (outputs to stdout)
        logger_factory=structlog.PrintLoggerFactory(),
        # Cache logger on first use for performance
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name.
    
    Use this function to create loggers in your modules.
    The name is typically set to __name__ to identify the module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog bound logger
        
    Example:
        logger = get_logger(__name__)
        logger.info("Starting process", job_id="123")
    """
    return structlog.get_logger(name)


def log_request_context(
    request_id: str,
    user_id: Optional[str] = None,
    **extra: Dict[str, Any]
) -> None:
    """
    Bind request context to all subsequent log calls.
    
    Call this at the start of each request to add context
    that will be included in all logs for that request.
    
    Args:
        request_id: Unique request identifier (for tracing)
        user_id: Optional authenticated user ID
        **extra: Additional context to bind
        
    Example:
        log_request_context(
            request_id="req-123",
            user_id="user-456",
            endpoint="/api/discovery"
        )
        logger.info("Processing request")  # Will include all context
    """
    # Clear any existing context from previous requests
    structlog.contextvars.clear_contextvars()
    # Bind new context for this request
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        user_id=user_id,
        **extra
    )


def clear_request_context() -> None:
    """
    Clear all bound context variables.
    
    Call this at the end of request processing to ensure
    context doesn't leak between requests.
    """
    structlog.contextvars.clear_contextvars()

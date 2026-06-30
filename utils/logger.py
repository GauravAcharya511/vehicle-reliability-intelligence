"""
Structured logging configuration.

Why this exists:
- Every pipeline run is traceable with timestamps and severity levels
- Production observability tools (Datadog, Splunk, CloudWatch) parse this format
- Replaces print() statements which lose context and ordering in concurrent runs
"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with consistent formatting."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

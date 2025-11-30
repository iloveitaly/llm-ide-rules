"""Centralized logging configuration using structlog-config.

This module configures structlog with opinionated defaults and exports a global logger.
Import the `log` object from this module to use structured logging throughout the application.
"""

from structlog_config import configure_logger

log = configure_logger()

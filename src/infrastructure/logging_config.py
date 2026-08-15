"""Configuracao de logging com structlog (formato amigavel em terminal)."""

import logging

import structlog


def configure_logging(nivel: int = logging.INFO) -> None:
    """Configura o logging do aplicativo.

    Args:
        nivel: nivel minimo de log (padrao INFO).
    """
    logging.basicConfig(format="%(message)s", level=nivel)

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(nivel),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

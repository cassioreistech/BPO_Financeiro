"""Configuracao de logging com structlog (formato amigavel em terminal)."""

import logging
import os
import sys
from pathlib import Path

import structlog


def _aplicacao_empacotada() -> bool:
    """True quando executado de um binario compilado (PyInstaller)."""
    return bool(getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"))


def _diretorio_logs() -> Path:
    """Diretorio estavel de logs, independente da localizacao do exe."""
    if _aplicacao_empacotada():
        base = Path(os.environ.get("APPDATA") or Path.home())
        return base / "Sistema BPO Financeiro" / "logs"
    return Path(__file__).resolve().parents[3] / "logs"


def configure_logging(nivel: int = logging.INFO) -> None:
    """Configura o logging do aplicativo.

    Args:
        nivel: nivel minimo de log (padrao INFO).

    Em executavel compilado, alem do terminal, registra eventos em um arquivo
    de log em %APPDATA% para permitir diagnostico remoto de problemas.
    """
    if _aplicacao_empacotada():
        _configurar_arquivo_log(nivel)
        return

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


def _configurar_arquivo_log(nivel: int) -> None:
    """Configura eventos structlog/stdlib em arquivo JSON em %APPDATA%."""
    log_dir = _diretorio_logs()
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    )

    logging.basicConfig(level=nivel, handlers=[file_handler])
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(nivel),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

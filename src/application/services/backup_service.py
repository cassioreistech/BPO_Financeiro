"""Servico de backup e restauracao do banco de dados SQLite."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from infrastructure.database import DATA_DIR, DATABASE_PATH

BACKUP_DIR = DATA_DIR / "backups"


def _garantir_diretorio_backup() -> None:
    """Garante que o diretorio de backups existe."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def criar_backup(destino: Path | None = None) -> Path:
    """Cria um backup do banco de dados.

    Args:
        destino: caminho completo do arquivo de destino.
                 Se None, salva no diretorio padrao com timestamp.

    Returns:
        Path do arquivo de backup criado.

    Raises:
        FileNotFoundError: se o banco de dados nao existir.
    """
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Banco de dados não encontrado para backup.")

    if destino is None:
        _garantir_diretorio_backup()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = BACKUP_DIR / f"bpo_backup_{timestamp}.db"

    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATABASE_PATH, destino)
    return destino


def listar_backups() -> list[Path]:
    """Lista os backups disponiveis, ordenados por data (mais recente primeiro).

    Returns:
        Lista de paths dos arquivos de backup.
    """
    _garantir_diretorio_backup()
    backups = sorted(BACKUP_DIR.glob("bpo_backup_*.db"), reverse=True)
    return backups


def restaurar_backup(backup_path: Path) -> None:
    """Restaura o banco de dados a partir de um backup.

    Args:
        backup_path: path do arquivo de backup.

    Raises:
        FileNotFoundError: se o backup nao existir.
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup não encontrado: {backup_path}")

    _garantir_diretorio_backup()
    shutil.copy2(backup_path, DATABASE_PATH)


def formatar_nome_backup(backup_path: Path) -> str:
    """Formata o nome do backup para exibicao amigavel.

    Args:
        backup_path: path do arquivo de backup.

    Returns:
        Nome formatado para exibicao.
    """
    nome = backup_path.stem
    try:
        partes = nome.replace("bpo_backup_", "")
        dt = datetime.strptime(partes, "%Y%m%d_%H%M%S")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return nome

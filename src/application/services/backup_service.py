"""Servico de backup e restauracao do banco de dados SQLite."""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path

from infrastructure.database import DATA_DIR, DATABASE_PATH, engine

log = logging.getLogger(__name__)

BACKUP_DIR = DATA_DIR / "backups"

MAX_BACKUPS_AUTOMATICOS = 15
MAX_BACKUPS_MANUAIS = 30

NOME_STAMP = ".ultimo_backup.json"


def _wal_checkpoint(caminho: Path) -> None:
    """Forca WAL checkpoint para garantir que todos os dados estao no .db."""
    try:
        conn = sqlite3.connect(str(caminho), timeout=10)
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        log.warning("Falha ao executar WAL checkpoint em %s", caminho)


def _fechar_sessoes_ativas() -> None:
    """Fecha todas as sessoes SQLAlchemy ativas antes de operacoes no banco."""
    try:
        engine.dispose()
    except Exception:
        log.warning("Falha ao dispor engine SQLAlchemy", exc_info=True)


def _copiar_banco_consistente(origem: Path, destino: Path) -> None:
    """Copia um snapshot consistente do banco usando a backup API do sqlite3.

    Diferente de shutil.copy2, esta copia produz um snapshot atomico do ponto
    de vista do SQLite, evitando backups parciais quando ha escrita concorrente.
    Executa WAL checkpoint antes de copiar para garantir que todos os dados
    estao no arquivo principal.
    """
    if not origem.exists():
        raise FileNotFoundError(f"Banco de dados não encontrado: {origem}")

    _wal_checkpoint(origem)

    destino.parent.mkdir(parents=True, exist_ok=True)
    conn_origem = sqlite3.connect(str(origem), timeout=10)
    try:
        conn_destino = sqlite3.connect(str(destino), timeout=10)
        try:
            conn_origem.backup(conn_destino)
        finally:
            conn_destino.close()
    finally:
        conn_origem.close()


def _validar_banco(caminho: Path) -> bool:
    """Executa PRAGMA quick_check em um arquivo e informa se e um banco valido."""
    try:
        conn = sqlite3.connect(str(caminho), timeout=10)
        try:
            resultado = conn.execute("PRAGMA quick_check;").fetchone()
            return bool(resultado and resultado[0] == "ok")
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        return False


def _limpar_backups_automaticos(max_manter: int = MAX_BACKUPS_AUTOMATICOS) -> None:
    """Remove backups automaticos antigos, mantendo os max_manter recentes."""
    backups = sorted(BACKUP_DIR.glob("bpo_auto_*.db"), reverse=True)
    for antigo in backups[max_manter:]:
        antigo.unlink(missing_ok=True)


def _limpar_backups_manuais(max_manter: int = MAX_BACKUPS_MANUAIS) -> None:
    """Remove backups manuais antigos do diretorio padrao, mantendo os recentes."""
    backups = sorted(BACKUP_DIR.glob("bpo_backup_*.db"), reverse=True)
    for antigo in backups[max_manter:]:
        antigo.unlink(missing_ok=True)


def _registrar_backup_realizado() -> None:
    """Registra o mtime do banco coberto pelo ultimo backup.

    Guardar o mtime do proprio banco (e nao o relogio de parede) elimina
    divergencias de sub-segundo entre o relogio do processo e o mtime do
    arquivo, tornando a comparacao em 'banco_alterado_em' deterministica.
    """
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        (BACKUP_DIR / NOME_STAMP).write_text(
            json.dumps({"banco_mtime": DATABASE_PATH.stat().st_mtime}),
            encoding="utf-8",
        )
    except OSError:
        return


def _ultimo_backup_mtime() -> float | None:
    """mtime do banco no momento do ultimo backup registrado."""
    caminho = BACKUP_DIR / NOME_STAMP
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        valor = dados.get("banco_mtime")
        if not isinstance(valor, int | float):
            return None
        return float(valor)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def backup_automatico() -> Path:
    """Cria um backup automatico diario do banco atual.

    Um arquivo por dia (bpo_auto_YYYYMMDD.db). Se o arquivo do dia ja existe
    mas o banco foi alterado depois dele, o arquivo e atualizado com o estado
    mais recente — assim um backup diario nunca fica desatualizado apos um
    crash ou edicoes posteriores a abertura. Aplica rotacao.

    Returns:
        Path do arquivo de backup diario.

    Raises:
        FileNotFoundError: se o banco de dados nao existir.
    """
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Banco de dados não encontrado para backup.")

    _garantir_diretorio_backup()
    hoje = datetime.now().strftime("%Y%m%d")
    destino = BACKUP_DIR / f"bpo_auto_{hoje}.db"

    if destino.exists() and destino.stat().st_mtime >= DATABASE_PATH.stat().st_mtime:
        _registrar_backup_realizado()
        return destino

    _copiar_banco_consistente(DATABASE_PATH, destino)
    _registrar_backup_realizado()
    _limpar_backups_automaticos()
    return destino


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

    _copiar_banco_consistente(DATABASE_PATH, destino)
    _registrar_backup_realizado()

    if destino.parent == BACKUP_DIR:
        _limpar_backups_manuais()

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

    Antes de sobrescrever, cria um backup de segurança do estado atual
    para permitir rollback caso a restauração falhe.

    Args:
        backup_path: path do arquivo de backup.

    Raises:
        FileNotFoundError: se o backup nao existir.
        ValueError: se o arquivo nao for um banco SQLite valido.
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup não encontrado: {backup_path}")
    if not _validar_banco(backup_path):
        raise ValueError(f"Backup inválido ou corrompido: {backup_path}")

    _garantir_diretorio_backup()
    _fechar_sessoes_ativas()

    # Backup de segurança antes de sobrescrever
    backup_seguranca = BACKUP_DIR / ".restore_rollback.db"
    tem_backup_seguranca = False
    if DATABASE_PATH.exists():
        try:
            shutil.copy2(DATABASE_PATH, backup_seguranca)
            tem_backup_seguranca = True
        except OSError:
            log.warning("Não foi possível criar backup de segurança antes de restaurar")

    try:
        _copiar_banco_consistente(backup_path, DATABASE_PATH)
    except Exception:
        # Rollback: restaura o estado anterior
        if tem_backup_seguranca and backup_seguranca.exists():
            try:
                _fechar_sessoes_ativas()
                shutil.copy2(backup_seguranca, DATABASE_PATH)
                log.info("Rollback: banco anterior restaurado após falha na restauração")
            except OSError:
                log.critical("FALHA CRÍTICA: rollback falhou. Banco pode estar corrompido.")
        raise
    finally:
        # Limpa arquivo temporário
        if backup_seguranca.exists():
            try:
                backup_seguranca.unlink()
            except OSError:
                pass


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


def banco_alterado_em(data_referencia: date) -> bool:
    """Indica se ha alteracoes no banco na data informada sem backup posterior.

    Considera que houve alteracao quando o arquivo do banco foi modificado na
    data de referencia e essa modificacao ocorreu apos o ultimo backup
    registrado. Assim, fechar apos ja ter feito backup no dia nao volta a pedir
    outro backup sem motivo.

    Args:
        data_referencia: data (dia) a verificar.

    Returns:
        True se ha alteracoes nao protegidas por backup na data informada.
    """
    try:
        if not DATABASE_PATH.exists():
            return False
        mtime = DATABASE_PATH.stat().st_mtime
        if datetime.fromtimestamp(mtime).date() != data_referencia:
            return False
        ultimo = _ultimo_backup_mtime()
        if ultimo is None:
            return True
        return mtime > ultimo
    except OSError:
        return False

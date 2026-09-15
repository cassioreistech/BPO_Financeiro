"""Infraestrutura de banco de dados (SQLite via SQLAlchemy 2.x)."""

import logging
import os
import shutil
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from infrastructure.database.schema_upgrade import upgrade_database

NOME_APP = "Sistema BPO Financeiro"

log = logging.getLogger(__name__)


def _aplicacao_empacotada() -> bool:
    """True quando executado de um binario compilado (PyInstaller)."""
    return bool(getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"))


def _diretorio_dados() -> Path:
    """Diretorio canonico de dados, estavel independente da localizacao do exe.

    Em executavel compilado usa %APPDATA%; em desenvolvimento a pasta data
    na raiz do projeto.
    """
    if _aplicacao_empacotada():
        return _appdata() / NOME_APP / "data"
    return Path(__file__).resolve().parents[3] / "data"


def _appdata() -> Path:
    """Retorna o diretorio %APPDATA% do usuario."""
    return Path(os.environ.get("APPDATA") or Path.home())


def _locais_legados() -> list[Path]:
    """Locais onde versoes antigas podiam armazenar os dados."""
    if not _aplicacao_empacotada():
        return []
    inicio = Path.home()
    exe_dir = Path(sys.executable).resolve().parent
    return [
        exe_dir / "data",
        exe_dir / "_internal" / "data",
        inicio / "Desktop" / "data",
        inicio / "OneDrive" / "Desktop" / "data",
    ]


def _copiar_backups_legados(origem: Path) -> None:
    """Reaproveita backups antigos no diretorio canonico, sem sobrescrever."""
    origem_backups = origem / "backups"
    if not origem_backups.is_dir():
        return
    destino_backups = DATA_DIR / "backups"
    destino_backups.mkdir(parents=True, exist_ok=True)
    for backup in origem_backups.glob("*.db"):
        destino = destino_backups / backup.name
        if not destino.exists():
            shutil.copy2(backup, destino)


def _migrar_dados_legados() -> None:
    """Move dados de instalacoes/versoes antigas para o diretorio canonico."""
    if DATABASE_PATH.exists():
        for origem in _locais_legados():
            _copiar_backups_legados(origem)
        return

    for origem in _locais_legados():
        banco = origem / "bpo.db"
        if not banco.exists():
            continue
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for item in sorted(origem.iterdir()):
            destino = DATA_DIR / item.name
            if item.is_dir():
                if not destino.exists():
                    shutil.move(str(item), str(destino))
                else:
                    _copiar_backups_legados(item)
            elif not destino.exists():
                shutil.move(str(item), str(destino))
        break


DATA_DIR = _diretorio_dados()
DATABASE_PATH = DATA_DIR / "bpo.db"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa para as entidades do dominio."""


_integridade_falhou = False


def integridade_falhou() -> bool:
    """Indica se a ultima verificacao de integridade detectou problema."""
    return _integridade_falhou


def diretorio_dados_gravavel() -> bool:
    """Garante e testa a gravacao em DATA_DIR; True se tudo escrevivel.

    Protege contra bloqueios do Windows (Defender 'Acesso a pastas
    controladas'), antivirus e permissoes de usuario.
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "backups").mkdir(parents=True, exist_ok=True)
        probe = DATA_DIR / ".probe_escrita.tmp"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:
        log.critical(
            "Sem permissao de escrita em %s: verificar Windows Defender, "
            "antivirus ou permissoes da pasta",
            DATA_DIR,
            exc_info=True,
        )
        return False


def banco_vazio() -> bool:
    """True quando o banco existe mas nao possui registros em nenhuma tabela."""
    try:
        with engine.connect() as conn:
            tabelas = [
                str(linha[0])
                for linha in conn.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'"
                )
            ]
        for tabela in tabelas:
            with engine.connect() as conn:
                total = conn.exec_driver_sql(
                    f'SELECT COUNT(*) FROM "{tabela}"'
                ).scalar()
            if total:
                return False
        return True
    except Exception:
        log.exception("Falha ao verificar se o banco esta vazio")
        return False


def _verificar_integridade() -> bool:
    """Executa PRAGMA quick_check e informa se o banco esta integro."""
    global _integridade_falhou
    try:
        with engine.connect() as conn:
            resultado = conn.exec_driver_sql("PRAGMA quick_check;").scalar()
    except Exception:
        log.exception("Falha ao verificar integridade do banco")
        _integridade_falhou = True
        return False
    if resultado == "ok":
        log.info("Integridade do banco verificada: %s", resultado)
        return True
    log.critical("Banco possivelmente corrompido: %s", resultado)
    _integridade_falhou = True
    return False


def init_db() -> None:
    """Garante o diretorio de dados e cria/atualiza o schema do banco."""
    global _integridade_falhou
    _integridade_falhou = False
    try:
        _migrar_dados_legados()
    except Exception:
        log.exception("Falha na migracao de dados legados")

    if not diretorio_dados_gravavel():
        return

    if DATABASE_PATH.exists():
        if _verificar_integridade():
            try:
                from application.services.backup_service import backup_automatico

                backup_automatico()
            except Exception:
                log.exception("Falha no backup automatico do banco")
        else:
            log.error(
                "Integridade falha detectada: backup diario preservado (nao "
                "sobrescrito com banco suspeito)"
            )

    # Importacao registra os models no metadata do Base antes do create_all.
    from infrastructure.database.models import (  # noqa: F401
        CentroCustoModel,
        ContaBancariaModel,
        ContadorModel,
        EmpresaModel,
        EscritorioModel,
        PlanoContaModel,
        TituloModel,
    )

    try:
        Base.metadata.create_all(bind=engine)
        upgrade_database(engine)
        _verificar_integridade()
    except Exception:
        _integridade_falhou = True
        log.exception(
            "Falha ao carregar o schema do banco (provavelmente corrompido): "
            "a interface abrira para permitir a restauracao de um backup"
        )

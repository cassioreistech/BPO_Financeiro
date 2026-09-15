"""Testes do servico de backup automatico."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from application.services import backup_service


def _criar_banco_sqlite(caminho: Path) -> None:
    """Cria um banco SQLite real com uma tabela de exemplo."""
    conn = sqlite3.connect(str(caminho))
    try:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, valor TEXT)")
        conn.execute("INSERT INTO t (valor) VALUES ('teste')")
        conn.commit()
    finally:
        conn.close()


def _fazer_mtime(caminho: Path, momento: datetime) -> None:
    ts = momento.timestamp()
    os.utime(caminho, (ts, ts))


@pytest.fixture()
def ambiente_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isola DATA_DIR/DATABASE_PATH/BACKUP_DIR do servico em pasta temporaria."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db = data_dir / "bpo.db"
    _criar_banco_sqlite(db)

    monkeypatch.setattr(backup_service, "DATA_DIR", data_dir)
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", data_dir / "backups")
    return data_dir


def _primeiro_registro_tabela(caminho: Path) -> str:
    conn = sqlite3.connect(str(caminho))
    try:
        return conn.execute("SELECT valor FROM t LIMIT 1").fetchone()[0]
    finally:
        conn.close()


def test_backup_automatico_cria_arquivo_diario(ambiente_backup: Path) -> None:
    destino = backup_service.backup_automatico()

    assert destino.parent == ambiente_backup / "backups"
    assert destino.name.startswith("bpo_auto_")
    assert destino.exists()
    assert _primeiro_registro_tabela(destino) == "teste"


def test_backup_automatico_nao_duplica_no_mesmo_dia(ambiente_backup: Path) -> None:
    primeiro = backup_service.backup_automatico()
    segundo = backup_service.backup_automatico()

    assert primeiro == segundo
    backups = list((ambiente_backup / "backups").glob("bpo_auto_*.db"))
    assert len(backups) == 1


def test_backup_automatico_atualiza_backup_apos_alteracao(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    primeiro = backup_service.backup_automatico()

    conn = sqlite3.connect(str(db))
    try:
        conn.execute("INSERT INTO t (valor) VALUES ('apos-crash')")
        conn.commit()
    finally:
        conn.close()
    _fazer_mtime(db, datetime.now() + timedelta(minutes=5))

    segundo = backup_service.backup_automatico()

    assert primeiro == segundo
    valores = sorted(r[0] for r in _consultar_valores(segundo))
    assert valores == ["apos-crash", "teste"]


def _consultar_valores(caminho: Path) -> list[tuple[str]]:
    conn = sqlite3.connect(str(caminho))
    try:
        return conn.execute("SELECT valor FROM t ORDER BY valor").fetchall()
    finally:
        conn.close()


def test_backup_automatico_sem_banco_levanta_erro(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "sem-banco" / "bpo.db"
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    with pytest.raises(FileNotFoundError):
        backup_service.backup_automatico()


def test_rotacao_mantem_apenas_recentes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    for dia in range(1, 6):
        (backup_dir / f"bpo_auto_2026010{dia}.db").write_bytes(b"x")
    monkeypatch.setattr(backup_service, "BACKUP_DIR", backup_dir)

    backup_service._limpar_backups_automaticos(max_manter=2)

    restantes = sorted(p.name for p in backup_dir.glob("bpo_auto_*.db"))
    assert restantes == ["bpo_auto_20260104.db", "bpo_auto_20260105.db"]


def test_rotacao_manuais_mantem_apenas_recentes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    for seq in range(1, 6):
        (backup_dir / f"bpo_backup_2026091{seq}_100000.db").write_bytes(b"x")
    monkeypatch.setattr(backup_service, "BACKUP_DIR", backup_dir)

    backup_service._limpar_backups_manuais(max_manter=2)

    restantes = sorted(p.name for p in backup_dir.glob("bpo_backup_*.db"))
    assert restantes == [
        "bpo_backup_20260914_100000.db",
        "bpo_backup_20260915_100000.db",
    ]


def test_banco_alterado_em_detecta_hoje(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    _fazer_mtime(db, datetime.now())
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    assert backup_service.banco_alterado_em(datetime.now().date())


def test_banco_sem_alteracao_no_dia_retorna_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    _fazer_mtime(db, datetime.now() - timedelta(days=2))
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    assert not backup_service.banco_alterado_em(datetime.now().date())


def test_banco_inexistente_retorna_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        backup_service, "DATABASE_PATH", tmp_path / "sem-banco" / "bpo.db"
    )
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    assert not backup_service.banco_alterado_em(datetime.now().date())


def test_banco_alterado_apos_backup_sem_registro_nao_pede_denovo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    _fazer_mtime(db, datetime.now())
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    assert backup_service.banco_alterado_em(datetime.now().date())

    backup_service._registrar_backup_realizado()

    assert not backup_service.banco_alterado_em(datetime.now().date())


def test_banco_alterado_detecta_mudanca_apos_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    _fazer_mtime(db, datetime.now())
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    backup_service._registrar_backup_realizado()
    _fazer_mtime(db, datetime.now() + timedelta(minutes=1))

    assert backup_service.banco_alterado_em(datetime.now().date())


def test_criar_backup_manual_registra_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    _fazer_mtime(db, datetime.now())
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    assert backup_service.banco_alterado_em(datetime.now().date())

    destino = backup_service.criar_backup()

    assert destino.name.startswith("bpo_backup_")
    assert _primeiro_registro_tabela(destino) == "teste"
    assert backup_service._ultimo_backup_mtime() == db.stat().st_mtime
    assert not backup_service.banco_alterado_em(datetime.now().date())


def test_restaurar_backup_recusa_arquivo_invalido(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    invalido = tmp_path / "invalido.db"
    invalido.write_bytes(b"isso nao e sqlite")

    with pytest.raises(ValueError, match="inválido|invalido"):
        backup_service.restaurar_backup(invalido)


def test_restaurar_backup_restaura_banco_valido(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    backup = backup_service.criar_backup()

    backup_service.restaurar_backup(backup)

    assert _primeiro_registro_tabela(db) == "teste"


def test_backup_automatico_preserva_snapshot_consistente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    _criar_banco_sqlite(db)
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", tmp_path / "backups")

    destino = backup_service.backup_automatico()

    dado_copiado = _primeiro_registro_tabela(destino)
    assert dado_copiado == "teste"

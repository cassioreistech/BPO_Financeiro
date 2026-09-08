"""Testes do servico de backup automatico."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from application.services import backup_service


@pytest.fixture()
def ambiente_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isola DATA_DIR/DATABASE_PATH/BACKUP_DIR do servico em pasta temporaria."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db = data_dir / "bpo.db"
    db.write_bytes(b"banco-de-teste")

    monkeypatch.setattr(backup_service, "DATA_DIR", data_dir)
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)
    monkeypatch.setattr(backup_service, "BACKUP_DIR", data_dir / "backups")
    return data_dir


def test_backup_automatico_cria_arquivo_diario(ambiente_backup: Path) -> None:
    destino = backup_service.backup_automatico()

    assert destino.parent == ambiente_backup / "backups"
    assert destino.name.startswith("bpo_auto_")
    assert destino.exists()
    assert destino.read_bytes() == b"banco-de-teste"


def test_backup_automatico_nao_duplica_no_mesmo_dia(ambiente_backup: Path) -> None:
    primeiro = backup_service.backup_automatico()
    segundo = backup_service.backup_automatico()

    assert primeiro == segundo
    backups = list((ambiente_backup / "backups").glob("bpo_auto_*.db"))
    assert len(backups) == 1


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


def _fazer_mtime(caminho: Path, momento: datetime) -> None:
    ts = momento.timestamp()
    os.utime(caminho, (ts, ts))


def test_banco_alterado_em_detecta_hoje(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    db.write_bytes(b"banco")
    _fazer_mtime(db, datetime.now())
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)

    assert backup_service.banco_alterado_em(datetime.now().date())


def test_banco_sem_alteracao_no_dia_retorna_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "bpo.db"
    db.write_bytes(b"banco")
    _fazer_mtime(db, datetime.now() - timedelta(days=2))
    monkeypatch.setattr(backup_service, "DATABASE_PATH", db)

    assert not backup_service.banco_alterado_em(datetime.now().date())


def test_banco_inexistente_retorna_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        backup_service, "DATABASE_PATH", tmp_path / "sem-banco" / "bpo.db"
    )

    assert not backup_service.banco_alterado_em(datetime.now().date())

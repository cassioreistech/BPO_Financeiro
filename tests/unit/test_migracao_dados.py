"""Testes da migracao de dados de instalacoes/versoes antigas."""

from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.database import _migrar_dados_legados


def _montar_legado(base: Path, dados: bytes = b"banco-antigo") -> Path:
    """Cria um diretorio legado 'data' com banco e backups."""
    legado = base / "legado" / "data"
    (legado / "backups").mkdir(parents=True)
    (legado / "bpo.db").write_bytes(dados)
    (legado / "backups" / "bpo_backup_20260101_120000.db").write_bytes(b"backup-antigo")
    return legado


def _isolar_destino(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    canonico = tmp_path / "canonico"
    monkeypatch.setattr("infrastructure.database.DATA_DIR", canonico)
    monkeypatch.setattr("infrastructure.database.DATABASE_PATH", canonico / "bpo.db")
    return canonico, canonico / "bpo.db"


def test_migrar_dados_move_banco_legado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legado = _montar_legado(tmp_path)
    canonico, banco = _isolar_destino(tmp_path, monkeypatch)
    monkeypatch.setattr("infrastructure.database._locais_legados", lambda: [legado])

    _migrar_dados_legados()

    assert banco.read_bytes() == b"banco-antigo"
    assert (canonico / "backups" / "bpo_backup_20260101_120000.db").exists()
    assert not (legado / "bpo.db").exists()


def test_migrar_dados_nao_sobrescreve_banco_canonico(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legado = _montar_legado(tmp_path)
    canonico, banco = _isolar_destino(tmp_path, monkeypatch)
    canonico.mkdir()
    banco.write_bytes(b"banco-novo")
    monkeypatch.setattr("infrastructure.database._locais_legados", lambda: [legado])

    _migrar_dados_legados()

    assert banco.read_bytes() == b"banco-novo"
    assert (canonico / "backups" / "bpo_backup_20260101_120000.db").exists()
    assert (legado / "bpo.db").exists()


def test_migrar_sem_legado_nao_cria_nada(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonico, _ = _isolar_destino(tmp_path, monkeypatch)
    monkeypatch.setattr("infrastructure.database._locais_legados", lambda: [])

    _migrar_dados_legados()

    assert not canonico.exists()

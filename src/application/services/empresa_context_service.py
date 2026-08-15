"""Servico de contexto global de empresa ativa.

Mantem em memoria a empresa selecionada para operacao do sistema.
Telas operacionais consultam esse contexto para carregar dados da empresa
ativa por padrao, enquanto telas analiticas (Alertas, Dashboard) podem
ignora-lo e operar de forma consolidada.
"""

from __future__ import annotations

from collections.abc import Callable

from application.dto.contexto_empresa_dto import EmpresaAtivaDTO


class EmpresaContextService:
    """Gerencia a empresa ativa da aplicacao de forma agnostica de UI."""

    def __init__(self) -> None:
        self._empresa_id: int | None = None
        self._empresa: EmpresaAtivaDTO | None = None
        self._callbacks: list[Callable[[int | None], None]] = []

    def set_empresa_ativa(
        self, empresa_id: int | None, detalhes: EmpresaAtivaDTO | None = None
    ) -> None:
        """Define a empresa ativa e notifica os observadores."""
        self._empresa_id = empresa_id
        self._empresa = detalhes
        for callback in self._callbacks:
            callback(empresa_id)

    def get_empresa_ativa(self) -> int | None:
        """Retorna o ID da empresa ativa."""
        return self._empresa_id

    def get_empresa_ativa_detalhes(self) -> EmpresaAtivaDTO | None:
        """Retorna os detalhes da empresa ativa, se disponiveis."""
        return self._empresa

    def adicionar_callback(
        self, callback: Callable[[int | None], None]
    ) -> None:
        """Adiciona um callback chamado quando a empresa ativa muda."""
        self._callbacks.append(callback)

    def remover_callback(
        self, callback: Callable[[int | None], None]
    ) -> None:
        """Remove um callback previamente registrado."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

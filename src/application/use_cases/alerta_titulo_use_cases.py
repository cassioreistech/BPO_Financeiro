"""Use cases para alertas e dashboard de vencimentos de titulos."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

from application.dto.alerta_titulo_dto import (
    DashboardAlertasTitulosResponseDTO,
    FiltroAlertasTitulosDTO,
    GrupoAlertaTituloResponseDTO,
    ItemAlertaTituloResponseDTO,
)
from application.ports.titulo_repository import TituloRepository
from domain.entities.alerta_titulo import (
    AlertaTitulo,
    GrupoAlertasTitulos,
    NivelUrgencia,
    ResumoAlertasTitulos,
)


class ObterDashboardAlertasTitulosUseCase:
    """Use case que monta o dashboard de alertas de titulos."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int,
        filtro: FiltroAlertasTitulosDTO,
    ) -> DashboardAlertasTitulosResponseDTO:
        """Obtem o dashboard de alertas para o escritorio.

        Args:
            escritorio_id: ID do escritorio.
            filtro: Filtro opcional de empresa e data de referencia.

        Raises:
            ValueError: se escritorio_id invalido.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        data_referencia = filtro.data_referencia or date.today()
        alertas = self._repository.list_alertas(
            escritorio_id=escritorio_id,
            empresa_id=filtro.empresa_id,
            data_referencia=data_referencia,
            incluir_vencidos=filtro.incluir_vencidos,
        )

        resumo = self._classificar_e_resumir(alertas, data_referencia)
        return self._para_dto(resumo)

    def _classificar_e_resumir(
        self,
        alertas: list[AlertaTitulo],
        data_referencia: date,
    ) -> ResumoAlertasTitulos:
        vencidos: list[AlertaTitulo] = []
        vence_hoje: list[AlertaTitulo] = []
        vence_amanha: list[AlertaTitulo] = []
        semana: list[AlertaTitulo] = []

        amanha = data_referencia + timedelta(days=1)
        limite_semana = data_referencia + timedelta(days=7)

        for alerta in alertas:
            data = alerta.data_vencimento
            if data < data_referencia:
                urgencia = NivelUrgencia.CRITICO
                vencidos.append(replace(alerta, urgencia=urgencia))
            elif data == data_referencia:
                urgencia = NivelUrgencia.ALTO
                vence_hoje.append(replace(alerta, urgencia=urgencia))
            elif data == amanha:
                urgencia = NivelUrgencia.MEDIO
                vence_amanha.append(replace(alerta, urgencia=urgencia))
            elif data_referencia < data <= limite_semana:
                urgencia = NivelUrgencia.INFORMATIVO
                semana.append(replace(alerta, urgencia=urgencia))

        vencidos = self._ordenar_itens(vencidos)
        vence_hoje = self._ordenar_itens(vence_hoje)
        vence_amanha = self._ordenar_itens(vence_amanha)
        semana = self._ordenar_itens(semana)

        grupo_vencidos = self._criar_grupo(NivelUrgencia.CRITICO, vencidos)
        grupo_hoje = self._criar_grupo(NivelUrgencia.ALTO, vence_hoje)
        grupo_amanha = self._criar_grupo(NivelUrgencia.MEDIO, vence_amanha)
        grupo_semana = self._criar_grupo(NivelUrgencia.INFORMATIVO, semana)

        total_quantidade = (
            grupo_vencidos.quantidade
            + grupo_hoje.quantidade
            + grupo_amanha.quantidade
            + grupo_semana.quantidade
        )
        total_valor = (
            grupo_vencidos.valor_total
            + grupo_hoje.valor_total
            + grupo_amanha.valor_total
            + grupo_semana.valor_total
        )

        return ResumoAlertasTitulos(
            vencidos=grupo_vencidos,
            vence_hoje=grupo_hoje,
            vence_amanha=grupo_amanha,
            semana=grupo_semana,
            total_quantidade=total_quantidade,
            total_valor=total_valor,
        )

    @staticmethod
    def _ordenar_itens(itens: list[AlertaTitulo]) -> list[AlertaTitulo]:
        return sorted(
            itens,
            key=lambda a: (
                a.data_vencimento,
                a.empresa_nome.lower(),
                a.descricao.lower(),
            ),
        )

    @staticmethod
    def _criar_grupo(
        urgencia: NivelUrgencia, itens: list[AlertaTitulo]
    ) -> GrupoAlertasTitulos:
        valor_total = sum((item.valor for item in itens), Decimal("0"))
        return GrupoAlertasTitulos(
            urgencia=urgencia,
            quantidade=len(itens),
            valor_total=valor_total,
            itens=itens,
        )

    @staticmethod
    def _para_dto(
        resumo: ResumoAlertasTitulos,
    ) -> DashboardAlertasTitulosResponseDTO:
        return DashboardAlertasTitulosResponseDTO(
            vencidos=ObterDashboardAlertasTitulosUseCase._grupo_para_dto(
                resumo.vencidos
            ),
            vence_hoje=ObterDashboardAlertasTitulosUseCase._grupo_para_dto(
                resumo.vence_hoje
            ),
            vence_amanha=ObterDashboardAlertasTitulosUseCase._grupo_para_dto(
                resumo.vence_amanha
            ),
            semana=ObterDashboardAlertasTitulosUseCase._grupo_para_dto(
                resumo.semana
            ),
            total_quantidade=resumo.total_quantidade,
            total_valor=resumo.total_valor,
        )

    @staticmethod
    def _grupo_para_dto(
        grupo: GrupoAlertasTitulos,
    ) -> GrupoAlertaTituloResponseDTO:
        return GrupoAlertaTituloResponseDTO(
            urgencia=grupo.urgencia.value,
            quantidade=grupo.quantidade,
            valor_total=grupo.valor_total,
            itens=[
                ItemAlertaTituloResponseDTO(
                    titulo_id=item.titulo_id,
                    empresa_id=item.empresa_id,
                    empresa_nome=item.empresa_nome,
                    descricao=item.descricao,
                    categoria=item.categoria,
                    numero_documento=item.numero_documento,
                    valor=item.valor,
                    data_vencimento=item.data_vencimento,
                    status=item.status.value,
                    urgencia=item.urgencia.value,
                )
                for item in grupo.itens
            ],
        )

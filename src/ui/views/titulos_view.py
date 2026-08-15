"""Tela de listagem de Titulos financeiros."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from application.dto.escritorio_dto import EscritorioResponseDTO
from application.dto.titulo_dto import TituloResponseDTO
from application.use_cases.centro_custo_use_cases import ListarCentroCustoUseCase
from application.use_cases.empresa_use_cases import ListarEmpresasUseCase
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from application.use_cases.plano_conta_use_cases import ListarPlanoContaUseCase
from application.use_cases.titulo_use_cases import (
    CadastrarTituloUseCase,
    CancelarTituloUseCase,
    EditarTituloUseCase,
    ListarTitulosUseCase,
    ObterTituloUseCase,
    QuitarTituloUseCase,
    RemoverTituloUseCase,
)
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)
from ui.views.titulo_form_view import TituloFormView


class TitulosView(QWidget):
    """Tela de listagem e gerenciamento de titulos financeiros."""

    COLUNAS = [
        "ID",
        "Escritorio",
        "Empresa",
        "Plano Conta",
        "Descricao",
        "Tipo",
        "Status",
        "Valor",
        "Vencimento",
    ]

    def __init__(
        self,
        listar: ListarTitulosUseCase,
        obter: ObterTituloUseCase,
        criar: CadastrarTituloUseCase,
        editar: EditarTituloUseCase,
        quitar: QuitarTituloUseCase,
        cancelar: CancelarTituloUseCase,
        remover: RemoverTituloUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        listar_empresas: ListarEmpresasUseCase,
        listar_plano_contas: ListarPlanoContaUseCase,
        listar_centros_custo: ListarCentroCustoUseCase,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._quitar = quitar
        self._cancelar = cancelar
        self._remover = remover
        self._listar_escritorios = listar_escritorios
        self._listar_empresas = listar_empresas
        self._listar_plano_contas = listar_plano_contas
        self._listar_centros_custo = listar_centros_custo
        self._montar()
        self.atualizar_lista()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Titulos Financeiros")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        cabecalho.addWidget(QLabel("Escritorio:"))
        self._combo_filtro_escritorio = QComboBox()
        self._combo_filtro_escritorio.setMinimumWidth(160)
        self._combo_filtro_escritorio.currentIndexChanged.connect(
            self._escritorio_alterado
        )
        cabecalho.addWidget(self._combo_filtro_escritorio)

        cabecalho.addWidget(QLabel("Empresa:"))
        self._combo_filtro_empresa = QComboBox()
        self._combo_filtro_empresa.setMinimumWidth(140)
        self._combo_filtro_empresa.addItem("Todas", None)
        cabecalho.addWidget(self._combo_filtro_empresa)

        cabecalho.addWidget(QLabel("Tipo:"))
        self._combo_filtro_tipo = QComboBox()
        self._combo_filtro_tipo.addItem("Todos", None)
        for t in TipoTitulo:
            self._combo_filtro_tipo.addItem(t.value, t.value)
        cabecalho.addWidget(self._combo_filtro_tipo)

        cabecalho.addWidget(QLabel("Status:"))
        self._combo_filtro_status = QComboBox()
        self._combo_filtro_status.addItem("Todos", None)
        for s in StatusTitulo:
            self._combo_filtro_status.addItem(s.value, s.value)
        cabecalho.addWidget(self._combo_filtro_status)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.atualizar_lista)
        cabecalho.addWidget(btn_filtrar)

        btn_novo = QPushButton("Novo Titulo")
        btn_novo.setObjectName("btnPrimario")
        btn_novo.clicked.connect(self._novo)
        cabecalho.addWidget(btn_novo)

        layout.addLayout(cabecalho)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(len(self.COLUNAS))
        self._tabela.setHorizontalHeaderLabels(self.COLUNAS)
        configurar_tabela_padrao(self._tabela)
        self._tabela.doubleClicked.connect(self._editar_selecionado)
        layout.addWidget(self._tabela)

        botoes = QHBoxLayout()
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._editar_selecionado)
        botoes.addWidget(btn_editar)

        btn_quitar = QPushButton("Quitar")
        btn_quitar.clicked.connect(self._quitar_selecionado)
        botoes.addWidget(btn_quitar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self._cancelar_selecionado)
        botoes.addWidget(btn_cancelar)

        btn_remover = QPushButton("Remover")
        btn_remover.clicked.connect(self._remover_selecionado)
        botoes.addWidget(btn_remover)
        botoes.addStretch()
        layout.addLayout(botoes)

    def _escritorio_alterado(self) -> None:
        self._atualizar_filtro_empresa()
        self.atualizar_lista()

    def _atualizar_filtro_empresa(self) -> None:
        escritorio_id = self._combo_filtro_escritorio.currentData()
        self._combo_filtro_empresa.blockSignals(True)
        self._combo_filtro_empresa.clear()
        self._combo_filtro_empresa.addItem("Todas", None)
        if escritorio_id is not None:
            try:
                empresas = self._listar_empresas.execute(skip=0, limit=1000)
                for emp in empresas:
                    if emp.escritorio_id == escritorio_id and emp.id is not None:
                        self._combo_filtro_empresa.addItem(
                            emp.razao_social, emp.id
                        )
            except Exception:
                pass
        self._combo_filtro_empresa.blockSignals(False)

    def atualizar_lista(self) -> None:
        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1000)
            mapa_esc = {e.id: e.nome for e in escritorios if e.id is not None}
        except Exception:
            mapa_esc = {}
            escritorios = []

        self._atualizar_combo_filtro(escritorios)
        escritorio_id = self._combo_filtro_escritorio.currentData()
        if escritorio_id is None:
            self._tabela.setRowCount(0)
            return

        try:
            empresas = self._listar_empresas.execute(skip=0, limit=1000)
            mapa_emp = {e.id: e.razao_social for e in empresas if e.id is not None}
        except Exception:
            mapa_emp = {}

        try:
            planos = self._listar_plano_contas.execute(
                escritorio_id=escritorio_id, skip=0, limit=500
            )
            mapa_plano = {
                p.id: f"{p.codigo} - {p.nome}" for p in planos if p.id is not None
            }
        except Exception:
            mapa_plano = {}

        empresa_id = self._combo_filtro_empresa.currentData()
        tipo = self._combo_filtro_tipo.currentData()
        status = self._combo_filtro_status.currentData()

        try:
            titulos = self._listar.execute(
                escritorio_id=escritorio_id,
                empresa_id=empresa_id,
                tipo=tipo,
                status=status,
                skip=0,
                limit=500,
            )
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar titulos: {e}")
            return

        self._tabela.setRowCount(len(titulos))
        for i, t in enumerate(titulos):
            self._tabela.setItem(
                i, 0, criar_item_centralizado(str(t.id or ""))
            )
            self._tabela.setItem(
                i, 1, QTableWidgetItem(mapa_esc.get(t.escritorio_id, "—"))
            )
            self._tabela.setItem(
                i,
                2,
                QTableWidgetItem(
                    mapa_emp.get(t.empresa_id, "—") if t.empresa_id else "—"
                ),
            )
            self._tabela.setItem(
                i,
                3,
                QTableWidgetItem(
                    mapa_plano.get(t.plano_conta_id, "—")
                ),
            )
            self._tabela.setItem(i, 4, QTableWidgetItem(t.descricao))
            self._tabela.setItem(i, 5, QTableWidgetItem(t.tipo))
            self._tabela.setItem(i, 6, QTableWidgetItem(t.status))
            self._tabela.setItem(
                i, 7, criar_item_centralizado(self._formatar_valor(t.valor))
            )
            self._tabela.setItem(
                i,
                8,
                criar_item_centralizado(
                    t.data_vencimento.strftime("%d/%m/%Y")
                ),
            )

            if t.status == "PAGO":
                cor = "#2e7d32"
            elif t.status == "CANCELADO":
                cor = "#757575"
            elif t.data_vencimento < date.today():
                cor = "#c62828"
            else:
                cor = "#000000"
            for col in range(9):
                item = self._tabela.item(i, col)
                if item is not None:
                    item.setForeground(self._cor(cor))

    def _atualizar_combo_filtro(
        self, escritorios: list[EscritorioResponseDTO]
    ) -> None:
        atual = self._combo_filtro_escritorio.currentData()
        self._combo_filtro_escritorio.blockSignals(True)
        self._combo_filtro_escritorio.clear()
        self._combo_filtro_escritorio.addItem("Selecione...", None)
        for esc in escritorios:
            if esc.id is not None:
                self._combo_filtro_escritorio.addItem(esc.nome, esc.id)
        if atual is not None:
            idx = self._combo_filtro_escritorio.findData(atual)
            if idx >= 0:
                self._combo_filtro_escritorio.setCurrentIndex(idx)
        self._combo_filtro_escritorio.blockSignals(False)

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _cor(hex_code: str) -> QColor:
        return QColor(hex_code)

    def _obter_selecionado(self) -> TituloResponseDTO | None:
        linha = self._tabela.currentRow()
        if linha < 0:
            return None
        item_id = self._tabela.item(linha, 0)
        if item_id is None:
            return None
        try:
            id_int = int(item_id.text())
        except ValueError:
            return None
        return self._obter.execute(id_int)

    def _obter_opcoes(
        self, listar_use_case: Any, attr_id: str, attr_nome: str
    ) -> list[tuple[int, str]]:
        try:
            itens = listar_use_case.execute(skip=0, limit=1000)
            return [
                (getattr(item, attr_id), getattr(item, attr_nome))
                for item in itens
                if getattr(item, attr_id) is not None
            ]
        except Exception:
            return []

    def _obter_opcoes_plano_conta(self, escritorio_id: int | None) -> list[tuple[int, str]]:
        if escritorio_id is None:
            return []
        try:
            planos = self._listar_plano_contas.execute(
                escritorio_id=escritorio_id, skip=0, limit=500
            )
            return [
                (p.id, f"{p.codigo} - {p.nome}")
                for p in planos
                if p.id is not None
            ]
        except Exception:
            return []

    def _obter_opcoes_centro_custo(self, empresa_id: int | None) -> list[tuple[int, str]]:
        if empresa_id is None:
            return []
        try:
            centros = self._listar_centros_custo.execute(
                empresa_id=empresa_id, skip=0, limit=500
            )
            return [
                (c.id, f"{c.codigo} - {c.nome}")
                for c in centros
                if c.id is not None
            ]
        except Exception:
            return []

    def _novo(self) -> None:
        opcoes_escritorio = self._obter_opcoes(
            self._listar_escritorios, "id", "nome"
        )
        if not opcoes_escritorio:
            QMessageBox.information(
                self,
                "Aviso",
                "Cadastre um escritorio antes de cadastrar titulos.",
            )
            return

        escritorio_id = self._combo_filtro_escritorio.currentData()
        empresa_id = self._combo_filtro_empresa.currentData()
        opcoes_empresa = self._obter_opcoes(
            self._listar_empresas, "id", "razao_social"
        )
        opcoes_plano = self._obter_opcoes_plano_conta(escritorio_id)
        if not opcoes_plano:
            QMessageBox.information(
                self,
                "Aviso",
                "Cadastre pelo menos uma conta no Plano de Contas "
                "para este escritorio antes de cadastrar titulos.",
            )
            return
        opcoes_centro = self._obter_opcoes_centro_custo(empresa_id)

        form = TituloFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes_escritorio,
            opcoes_empresa=opcoes_empresa,
            opcoes_plano_conta=opcoes_plano,
            opcoes_centro_custo=opcoes_centro,
            escritorio_id=escritorio_id,
            parent=self,
        )
        if form.exec() == TituloFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para editar."
            )
            return

        opcoes_escritorio = self._obter_opcoes(
            self._listar_escritorios, "id", "nome"
        )
        opcoes_empresa = self._obter_opcoes(
            self._listar_empresas, "id", "razao_social"
        )
        opcoes_plano = self._obter_opcoes_plano_conta(titulo.escritorio_id)
        opcoes_centro = self._obter_opcoes_centro_custo(titulo.empresa_id)

        form = TituloFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes_escritorio,
            opcoes_empresa=opcoes_empresa,
            opcoes_plano_conta=opcoes_plano,
            opcoes_centro_custo=opcoes_centro,
            escritorio_id=titulo.escritorio_id,
            parent=self,
            titulo=titulo,
        )
        if form.exec() == TituloFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _quitar_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para quitar."
            )
            return
        if titulo.status == "PAGO":
            QMessageBox.information(self, "Aviso", "Titulo ja esta quitado.")
            return
        if titulo.status == "CANCELADO":
            QMessageBox.information(
                self, "Aviso", "Nao e possivel quitar um titulo cancelado."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar quitacao",
            f"Deseja quitar o titulo '{titulo.descricao}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._quitar.execute(titulo.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Titulo quitado com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def _cancelar_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para cancelar."
            )
            return
        if titulo.status == "CANCELADO":
            QMessageBox.information(
                self, "Aviso", "Titulo ja esta cancelado."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar cancelamento",
            f"Deseja cancelar o titulo '{titulo.descricao}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._cancelar.execute(titulo.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Titulo cancelado com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def _remover_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para remover."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar remocao",
            f"Deseja remover o titulo '{titulo.descricao}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._remover.execute(titulo.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Titulo removido com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

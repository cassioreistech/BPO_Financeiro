"""Janela principal do sistema com navegacao lateral."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from infrastructure.database import SessionLocal
from infrastructure.database.repositories.sqlite_conta_bancaria_repository import (
    SQLiteContaBancariaRepository,
)
from infrastructure.database.repositories.sqlite_contador_repository import (
    SQLiteContadorRepository,
)
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from ui.views.contadores_view import ContadoresView
from ui.views.contas_bancarias_view import ContasBancariasView
from ui.views.empresas_view import EmpresasView
from ui.views.escritorios_view import EscritoriosView


class MainWindow(QMainWindow):
    """Janela principal com navegacao lateral entre telas."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema BPO Financeiro")
        self.resize(1200, 720)
        self.showMaximized()

        self._configurar_repositories()
        self._montar_ui()
        self._navegar(0)

    def _configurar_repositories(self) -> None:
        self._esc_repo = SQLiteEscritorioRepository(SessionLocal)
        self._emp_repo = SQLiteEmpresaRepository(SessionLocal)
        self._cont_repo = SQLiteContadorRepository(SessionLocal)
        self._conta_repo = SQLiteContaBancariaRepository(SessionLocal)

        from application.use_cases.conta_bancaria_use_cases import (
            CadastrarContaBancariaUseCase,
            DesativarContaBancariaUseCase,
            EditarContaBancariaUseCase,
            ListarContasBancariasUseCase,
            ObterContaBancariaUseCase,
        )
        from application.use_cases.contador_use_cases import (
            CadastrarContadorUseCase,
            EditarContadorUseCase,
            ExcluirContadorUseCase,
            ListarContadoresUseCase,
            ObterContadorUseCase,
        )
        from application.use_cases.empresa_use_cases import (
            CadastrarEmpresaUseCase,
            EditarEmpresaUseCase,
            ListarEmpresasUseCase,
            ObterEmpresaUseCase,
        )
        from application.use_cases.escritorio_use_cases import (
            CriarEscritorioUseCase,
            EditarEscritorioUseCase,
            ListarEscritoriosUseCase,
            ObterEscritorioUseCase,
        )

        self._uc_listar_esc = ListarEscritoriosUseCase(self._esc_repo)
        self._uc_obter_esc = ObterEscritorioUseCase(self._esc_repo)
        self._uc_criar_esc = CriarEscritorioUseCase(self._esc_repo)
        self._uc_editar_esc = EditarEscritorioUseCase(self._esc_repo)

        self._uc_listar_emp = ListarEmpresasUseCase(self._emp_repo)
        self._uc_obter_emp = ObterEmpresaUseCase(self._emp_repo)
        self._uc_criar_emp = CadastrarEmpresaUseCase(self._emp_repo)
        self._uc_editar_emp = EditarEmpresaUseCase(self._emp_repo)

        self._uc_listar_cont = ListarContadoresUseCase(self._cont_repo)
        self._uc_obter_cont = ObterContadorUseCase(self._cont_repo)
        self._uc_criar_cont = CadastrarContadorUseCase(self._cont_repo)
        self._uc_editar_cont = EditarContadorUseCase(self._cont_repo)
        self._uc_excluir_cont = ExcluirContadorUseCase(self._cont_repo)

        self._uc_listar_conta = ListarContasBancariasUseCase(self._conta_repo)
        self._uc_obter_conta = ObterContaBancariaUseCase(self._conta_repo)
        self._uc_criar_conta = CadastrarContaBancariaUseCase(self._conta_repo)
        self._uc_editar_conta = EditarContaBancariaUseCase(self._conta_repo)
        self._uc_desativar_conta = DesativarContaBancariaUseCase(self._conta_repo)

    def _montar_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        principal = QHBoxLayout(central)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        sidebar = self._criar_sidebar()
        principal.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        self._criar_paginas()
        principal.addWidget(self._stack)

    def _criar_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QPushButton("BPO Financeiro")
        logo.setObjectName("logo")
        logo.setEnabled(False)
        layout.addWidget(logo)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setObjectName("separator")
        layout.addWidget(sep)

        self._botoes_nav: list[QPushButton] = []

        nav_items = [
            ("  Escritorios", 0),
            ("  Empresas", 1),
            ("  Contadores", 2),
            ("  Contas Bancarias", 3),
        ]

        for texto, indice in nav_items:
            btn = QPushButton(texto)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=indice: self._navegar(i))
            layout.addWidget(btn)
            self._botoes_nav.append(btn)

        layout.addStretch()

        return sidebar

    def _criar_paginas(self) -> None:
        self._view_escritorios = EscritoriosView(
            listar=self._uc_listar_esc,
            obter=self._uc_obter_esc,
            criar=self._uc_criar_esc,
            editar=self._uc_editar_esc,
        )
        self._stack.addWidget(self._view_escritorios)

        self._view_empresas = EmpresasView(
            listar=self._uc_listar_emp,
            obter=self._uc_obter_emp,
            criar=self._uc_criar_emp,
            editar=self._uc_editar_emp,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_empresas)

        self._view_contadores = ContadoresView(
            listar=self._uc_listar_cont,
            obter=self._uc_obter_cont,
            criar=self._uc_criar_cont,
            editar=self._uc_editar_cont,
            excluir=self._uc_excluir_cont,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_contadores)

        self._view_contas = ContasBancariasView(
            listar=self._uc_listar_conta,
            obter=self._uc_obter_conta,
            criar=self._uc_criar_conta,
            editar=self._uc_editar_conta,
            desativar=self._uc_desativar_conta,
            listar_empresas=self._uc_listar_emp,
        )
        self._stack.addWidget(self._view_contas)

    def _navegar(self, indice: int) -> None:
        self._stack.setCurrentIndex(indice)
        for i, btn in enumerate(self._botoes_nav):
            btn.setProperty("active", i == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

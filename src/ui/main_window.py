"""Janela principal do sistema com navegacao lateral."""

from __future__ import annotations

import contextlib
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.dto.contexto_empresa_dto import EmpresaAtivaDTO
from application.services.empresa_context_service import EmpresaContextService
from infrastructure.database import SessionLocal
from infrastructure.database.repositories.sqlite_centro_custo_repository import (
    SQLiteCentroCustoRepository,
)
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
from infrastructure.database.repositories.sqlite_plano_conta_repository import (
    SQLitePlanoContaRepository,
)
from infrastructure.database.repositories.sqlite_titulo_repository import (
    SQLiteTituloRepository,
)
from ui.views.alertas_titulos_view import AlertasTitulosView
from ui.views.contadores_view import ContadoresView
from ui.views.contas_bancarias_view import ContasBancariasView
from ui.views.dashboard_view import DashboardView
from ui.views.empresas_view import EmpresasView
from ui.views.escritorios_view import EscritoriosView
from ui.views.titulos_view import TitulosView


class MainWindow(QMainWindow):
    """Janela principal com navegacao lateral entre telas."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema BPO Financeiro")
        self.setMinimumSize(1024, 600)

        self._contexto_empresa = EmpresaContextService()
        self._configurar_repositories()
        self._carregar_empresas_iniciais()
        self._montar_ui()
        self._navegar(0)  # Abre na tela de Alertas
        QTimer.singleShot(100, self.showMaximized)

    def _carregar_empresas_iniciais(self) -> None:
        """Carrega empresas e define a primeira como ativa, se houver."""
        try:
            empresas = self._uc_listar_emp.execute(skip=0, limit=1000)
        except Exception:
            empresas = []

        self._empresas: dict[int, EmpresaAtivaDTO] = {}
        for emp in empresas:
            if emp.id is not None:
                self._empresas[emp.id] = EmpresaAtivaDTO(
                    id=emp.id,
                    nome_fantasia=emp.nome_fantasia,
                    razao_social=emp.razao_social,
                    cnpj=emp.cnpj,
                )

    def _recarregar_empresas(self) -> None:
        """Recarrega as empresas e o combo global apos alteracoes."""
        self._carregar_empresas_iniciais()
        if hasattr(self, "_combo_empresa_ativa"):
            self._combo_empresa_ativa.blockSignals(True)
            self._combo_empresa_ativa.clear()
            self._combo_empresa_ativa.addItem("Selecione...", None)
            for empresa in self._empresas.values():
                texto = (
                    f"{empresa.nome_fantasia} "
                    f"({self._formatar_cnpj(empresa.cnpj)})"
                )
                self._combo_empresa_ativa.addItem(texto, empresa.id)
            empresa_ativa = self._contexto_empresa.get_empresa_ativa()
            if empresa_ativa is not None:
                idx = self._combo_empresa_ativa.findData(empresa_ativa)
                if idx >= 0:
                    self._combo_empresa_ativa.setCurrentIndex(idx)
            self._combo_empresa_ativa.blockSignals(False)
            self._atualizar_label_empresa_ativa()
        self._recarregar_telas_operacionais()

    def _configurar_repositories(self) -> None:
        self._esc_repo = SQLiteEscritorioRepository(SessionLocal)
        self._emp_repo = SQLiteEmpresaRepository(SessionLocal)
        self._cont_repo = SQLiteContadorRepository(SessionLocal)
        self._conta_repo = SQLiteContaBancariaRepository(SessionLocal)
        self._plano_repo = SQLitePlanoContaRepository(SessionLocal)
        self._titulo_repo = SQLiteTituloRepository(SessionLocal)
        self._centro_repo = SQLiteCentroCustoRepository(SessionLocal)

        from application.use_cases.alerta_titulo_use_cases import (
            ObterDashboardAlertasTitulosUseCase,
        )
        from application.use_cases.centro_custo_use_cases import (
            CadastrarCentroCustoUseCase,
            DesativarCentroCustoUseCase,
            EditarCentroCustoUseCase,
            ListarCentroCustoUseCase,
            ObterCentroCustoUseCase,
        )
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
        from application.use_cases.dashboard_use_cases import (
            ResumoFinanceiroUseCase,
        )
        from application.use_cases.empresa_use_cases import (
            CadastrarEmpresaUseCase,
            EditarEmpresaUseCase,
            ExcluirEmpresaUseCase,
            ListarEmpresasUseCase,
            ObterEmpresaUseCase,
        )
        from application.use_cases.escritorio_use_cases import (
            CriarEscritorioUseCase,
            EditarEscritorioUseCase,
            ExcluirEscritorioUseCase,
            ListarEscritoriosUseCase,
            ObterEscritorioUseCase,
        )
        from application.use_cases.plano_conta_use_cases import (
            CadastrarPlanoContaUseCase,
            EditarPlanoContaUseCase,
            GarantirContaPadraoUseCase,
            ListarPlanoContaUseCase,
            ObterPlanoContaUseCase,
            RemoverPlanoContaUseCase,
        )
        from application.use_cases.relatorio_titulos_use_cases import (
            FluxoCaixaUseCase,
            ProjecaoFinanceiraUseCase,
            RelatorioTitulosUseCase,
        )
        from application.use_cases.titulo_use_cases import (
            CadastrarTituloUseCase,
            CancelarTituloUseCase,
            EditarTituloUseCase,
            ListarTitulosUseCase,
            ObterTituloUseCase,
            QuitarTituloUseCase,
            RemoverTituloUseCase,
        )

        self._uc_listar_esc = ListarEscritoriosUseCase(self._esc_repo)
        self._uc_obter_esc = ObterEscritorioUseCase(self._esc_repo)
        self._uc_resumo_dashboard = ResumoFinanceiroUseCase(self._titulo_repo)
        self._uc_criar_esc = CriarEscritorioUseCase(self._esc_repo)
        self._uc_editar_esc = EditarEscritorioUseCase(self._esc_repo)
        self._uc_excluir_esc = ExcluirEscritorioUseCase(self._esc_repo)

        self._uc_listar_emp = ListarEmpresasUseCase(self._emp_repo)
        self._uc_obter_emp = ObterEmpresaUseCase(self._emp_repo)
        self._uc_criar_emp = CadastrarEmpresaUseCase(self._emp_repo)
        self._uc_editar_emp = EditarEmpresaUseCase(self._emp_repo)
        self._uc_excluir_emp = ExcluirEmpresaUseCase(self._emp_repo)

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

        self._uc_listar_plano = ListarPlanoContaUseCase(self._plano_repo)
        self._uc_obter_plano = ObterPlanoContaUseCase(self._plano_repo)
        self._uc_criar_plano = CadastrarPlanoContaUseCase(self._plano_repo)
        self._uc_editar_plano = EditarPlanoContaUseCase(self._plano_repo)
        self._uc_remover_plano = RemoverPlanoContaUseCase(self._plano_repo)
        self._uc_garantir_conta_padrao = GarantirContaPadraoUseCase(
            self._plano_repo
        )

        self._uc_listar_titulo = ListarTitulosUseCase(self._titulo_repo)
        self._uc_obter_titulo = ObterTituloUseCase(self._titulo_repo)
        self._uc_dashboard_alertas = ObterDashboardAlertasTitulosUseCase(
            self._titulo_repo
        )
        self._uc_criar_titulo = CadastrarTituloUseCase(self._titulo_repo)
        self._uc_editar_titulo = EditarTituloUseCase(self._titulo_repo)
        self._uc_quitar_titulo = QuitarTituloUseCase(
            self._titulo_repo, self._conta_repo
        )
        self._uc_cancelar_titulo = CancelarTituloUseCase(self._titulo_repo)
        self._uc_remover_titulo = RemoverTituloUseCase(self._titulo_repo)
        self._uc_relatorio_titulos = RelatorioTitulosUseCase(self._titulo_repo)
        self._uc_fluxo_caixa = FluxoCaixaUseCase(self._titulo_repo)
        self._uc_projecao_financeira = ProjecaoFinanceiraUseCase(
            self._titulo_repo
        )

        self._uc_listar_centro = ListarCentroCustoUseCase(self._centro_repo)
        self._uc_obter_centro = ObterCentroCustoUseCase(self._centro_repo)
        self._uc_criar_centro = CadastrarCentroCustoUseCase(self._centro_repo)
        self._uc_editar_centro = EditarCentroCustoUseCase(self._centro_repo)
        self._uc_desativar_centro = DesativarCentroCustoUseCase(self._centro_repo)

    def _montar_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        principal = QVBoxLayout(central)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        header = self._criar_header_empresa()
        principal.addWidget(header)

        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)

        sidebar = self._criar_sidebar()
        corpo.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        self._criar_paginas()
        corpo.addWidget(self._stack)

        principal.addLayout(corpo)
        self._atualizar_label_empresa_ativa()

        # Conectar mudanca de pagina para ocultar/mostrar seletor empresa
        self._stack.currentChanged.connect(self._ao_trocar_pagina)
        self._ao_trocar_pagina(0)  # Oculta seletor na tela inicial (Alertas)

        # Timer para auto-refresh dos alertas (a cada 5 minutos)
        self._timer_alertas = QTimer(self)
        self._timer_alertas.timeout.connect(self._atualizar_alertas_seguranca)
        self._timer_alertas.start(300000)  # 5 minutos

        # Verificar alertas criticos na abertura
        QTimer.singleShot(1000, self._verificar_alertas_abertura)

    def _criar_header_empresa(self) -> QWidget:
        """Cria o cabecalho superior com seletor de empresa ativa."""
        header = QWidget()
        header.setObjectName("headerEmpresa")
        header.setFixedHeight(48)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self._label_empresa_ativa = QLabel("Empresa ativa: —")
        self._label_empresa_ativa.setObjectName("labelEmpresaAtiva")
        layout.addWidget(self._label_empresa_ativa)
        layout.addStretch()

        self._lbl_trocar_empresa = QLabel("Trocar empresa:")
        layout.addWidget(self._lbl_trocar_empresa)
        self._combo_empresa_ativa = QComboBox()
        self._combo_empresa_ativa.setMinimumWidth(300)
        self._combo_empresa_ativa.addItem("Selecione...", None)
        for empresa in self._empresas.values():
            texto = f"{empresa.nome_fantasia} ({self._formatar_cnpj(empresa.cnpj)})"
            self._combo_empresa_ativa.addItem(texto, empresa.id)

        empresa_ativa = self._contexto_empresa.get_empresa_ativa()
        if empresa_ativa is not None:
            idx = self._combo_empresa_ativa.findData(empresa_ativa)
            if idx >= 0:
                self._combo_empresa_ativa.setCurrentIndex(idx)

        self._combo_empresa_ativa.currentIndexChanged.connect(
            self._empresa_ativa_alterada
        )
        layout.addWidget(self._combo_empresa_ativa)

        return header

    @staticmethod
    def _formatar_cnpj(cnpj: str) -> str:
        """Formata CNPJ para exibicao."""
        if len(cnpj) != 14:
            return cnpj
        return (
            f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/"
            f"{cnpj[8:12]}-{cnpj[12:]}"
        )

    def _empresa_ativa_alterada(self) -> None:
        empresa_id = self._combo_empresa_ativa.currentData()
        if empresa_id is None:
            return
        empresa = self._empresas.get(empresa_id)
        self._contexto_empresa.set_empresa_ativa(empresa_id, empresa)
        self._atualizar_label_empresa_ativa()
        self._recarregar_telas_operacionais()

    def _atualizar_label_empresa_ativa(self) -> None:
        empresa = self._contexto_empresa.get_empresa_ativa_detalhes()
        if empresa is None:
            self._label_empresa_ativa.setText("Empresa ativa: —")
            return
        texto = (
            f"Empresa ativa: {empresa.nome_fantasia} — "
            f"CNPJ {self._formatar_cnpj(empresa.cnpj)}"
        )
        self._label_empresa_ativa.setText(texto)

    def _recarregar_telas_operacionais(self) -> None:
        if hasattr(self, "_view_titulos"):
            self._view_titulos.carregar_empresa_ativa()
        if hasattr(self, "_view_contas"):
            self._view_contas.carregar_empresa_ativa()
        if hasattr(self, "_view_dashboard"):
            self._view_dashboard.carregar_empresa_ativa()
        if hasattr(self, "_view_alertas"):
            self._view_alertas.atualizar()

    def _atualizar_dashboard_e_alertas(self) -> None:
        """Atualiza Dashboard e Alertas apos operacao de titulos."""
        if hasattr(self, "_view_dashboard"):
            self._view_dashboard.atualizar()
        if hasattr(self, "_view_alertas"):
            self._view_alertas.atualizar()
        self._atualizar_badge_alertas()

    def _ao_trocar_pagina(self, indice: int) -> None:
        """Oculta seletor de empresa quando na tela de Alertas (indice 0)."""
        ocultar = indice == 0
        self._lbl_trocar_empresa.setVisible(not ocultar)
        self._combo_empresa_ativa.setVisible(not ocultar)
        self._label_empresa_ativa.setVisible(not ocultar)

    def _atualizar_alertas_seguranca(self) -> None:
        """Atualiza alertas periodicamente (timer de 5 min)."""
        if hasattr(self, "_view_alertas"):
            self._view_alertas.atualizar()
            self._atualizar_badge_alertas()

    def _atualizar_badge_alertas(self) -> None:
        """Atualiza o badge de contagem no botao Alertas."""
        if not hasattr(self, "_btn_alertas") or not hasattr(self, "_view_alertas"):
            return
        try:
            criticos = self._view_alertas.obter_contagem_criticos()
            if criticos > 0:
                self._btn_alertas.setText(f"  Alertas ({criticos})")
                self._btn_alertas.setStyleSheet(
                    "background-color: #c62828; color: white; font-weight: bold;"
                )
            else:
                self._btn_alertas.setText("  Alertas")
                self._btn_alertas.setStyleSheet("")
        except Exception:
            pass

    def _verificar_alertas_abertura(self) -> None:
        """Verifica alertas criticos na abertura do sistema."""
        if not hasattr(self, "_view_alertas"):
            return
        try:
            criticos = self._view_alertas.obter_contagem_criticos()
            self._atualizar_badge_alertas()
            if criticos > 0:
                from PySide6.QtWidgets import QMessageBox

                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Atenção: Titulos Vencidos")
                msg.setText(
                    f"Existem {criticos} titulo(s) VENCIDO(S)!\n\n"
                    "Verifique a tela de Alertas para mais detalhes."
                )
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        except Exception:
            pass

    def _criar_backup(self) -> None:
        """Cria um backup do banco de dados pedindo onde salvar."""
        from datetime import datetime

        from PySide6.QtWidgets import QFileDialog, QMessageBox

        from application.services.backup_service import criar_backup

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_padrao = f"bpo_backup_{timestamp}.db"

        arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Backup",
            nome_padrao,
            "Banco de dados (*.db);;Todos os arquivos (*)",
        )
        if not arquivo:
            return

        if not arquivo.endswith(".db"):
            arquivo += ".db"

        try:
            backup_path = criar_backup(Path(arquivo))
            QMessageBox.information(
                self,
                "Backup realizado",
                f"Backup criado com sucesso:\n{backup_path}",
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro no backup",
                f"Erro ao criar backup:\n{e}",
            )

    def _restaurar_backup(self) -> None:
        """Restaura o banco de dados a partir de um arquivo de backup."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        from application.services.backup_service import (
            criar_backup,
            restaurar_backup,
        )

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Backup para Restaurar",
            "",
            "Banco de dados (*.db);;Todos os arquivos (*)",
        )
        if not arquivo:
            return

        backup_selecionado = Path(arquivo)

        confirmacao = QMessageBox.question(
            self,
            "Confirmar restauracao",
            "ATENÇÃO: Esta acao ira substituir o banco de dados atual.\n"
            "Um backup do banco atual sera criado antes da restauracao.\n\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmacao != QMessageBox.StandardButton.Yes:
            return

        with contextlib.suppress(Exception):
            criar_backup()

        try:
            restaurar_backup(backup_selecionado)
            QMessageBox.information(
                self,
                "Restauracao concluida",
                "Banco de dados restaurado com sucesso.\n"
                "O sistema sera reiniciado para aplicar as alteracoes.",
            )
            import sys

            from infrastructure.database import engine
            engine.dispose()
            import os
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro na restauracao",
                f"Erro ao restaurar backup:\n{e}",
            )

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

        # Itens principais (operacionais)
        main_items = [
            ("  Alertas", 0),
            ("  Dashboard", 1),
            ("  Titulos", 2),
        ]

        for texto, indice in main_items:
            btn = QPushButton(texto)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=indice: self._navegar(i))
            layout.addWidget(btn)
            self._botoes_nav.append(btn)
            if indice == 0:
                self._btn_alertas = btn

        # Separador antes de Configurações
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setObjectName("separator")
        layout.addWidget(sep2)

        # Botão Configurações (expansível)
        self._btn_config = QPushButton("  Configurações")
        self._btn_config.setObjectName("navButton")
        self._btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_config.setCheckable(True)
        self._btn_config.clicked.connect(self._toggle_config)
        layout.addWidget(self._btn_config)

        # Container dos itens de configuração (inicialmente oculto)
        self._config_container = QWidget()
        self._config_container.setVisible(False)
        config_layout = QVBoxLayout(self._config_container)
        config_layout.setContentsMargins(16, 8, 0, 8)
        config_layout.setSpacing(4)

        config_items = [
            ("    Contas Bancarias", 3),
            ("    Empresas", 4),
            ("    Escritorios", 5),
            ("    Contadores", 6),
        ]

        self._botoes_config: list[QPushButton] = []
        for texto, indice in config_items:
            btn = QPushButton(texto)
            btn.setObjectName("navButtonConfig")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=indice: self._navegar(i))
            config_layout.addWidget(btn)
            self._botoes_config.append(btn)

        btn_restaurar = QPushButton("    Restaurar Backup")
        btn_restaurar.setObjectName("navButtonConfig")
        btn_restaurar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restaurar.clicked.connect(self._restaurar_backup)
        config_layout.addWidget(btn_restaurar)

        btn_backup = QPushButton("    Backup")
        btn_backup.setObjectName("navButtonConfig")
        btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_backup.clicked.connect(self._criar_backup)
        config_layout.addWidget(btn_backup)

        layout.addWidget(self._config_container)

        layout.addStretch()

        # Marca d'água REISTECH (rodapé da sidebar)
        sep3 = QWidget()
        sep3.setFixedHeight(1)
        sep3.setObjectName("separator")
        layout.addWidget(sep3)

        marca = QLabel("Desenvolvido por\nREISTECH")
        marca.setObjectName("marcaReistech")
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marca.setStyleSheet(
            """
            QLabel#marcaReistech {
                color: #888888;
                font-size: 10px;
                padding: 8px 4px;
                border: none;
            }
            """
        )
        layout.addWidget(marca)

        return sidebar

    def _toggle_config(self) -> None:
        """Alterna visibilidade do menu de configuracoes."""
        visivel = self._config_container.isVisible()
        self._config_container.setVisible(not visivel)
        self._btn_config.setChecked(not visivel)

    def _colapsar_config(self) -> None:
        """Colapsa o menu de configuracoes se estiver aberto."""
        if self._config_container.isVisible():
            self._config_container.setVisible(False)
            self._btn_config.setChecked(False)

    def _navegar(self, indice: int) -> None:
        # Colapsa config ao navegar para item principal
        if indice in (0, 1, 2):  # indices dos itens principais
            self._colapsar_config()
        self._stack.setCurrentIndex(indice)

        for i, btn in enumerate(self._botoes_nav):
            btn.setProperty("active", i == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        for i, btn in enumerate(self._botoes_config):
            btn.setProperty("active", i == (indice - 3))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _criar_paginas(self) -> None:
        # 0: Alertas
        self._view_alertas = AlertasTitulosView(
            dashboard_use_case=self._uc_dashboard_alertas,
            listar_escritorios=self._uc_listar_esc,
            contexto_empresa=self._contexto_empresa,
        )
        self._stack.addWidget(self._view_alertas)

        # 1: Dashboard
        self._view_dashboard = DashboardView(
            listar_titulos=self._uc_listar_titulo,
            contexto_empresa=self._contexto_empresa,
        )
        self._stack.addWidget(self._view_dashboard)

        # 2: Titulos
        self._view_titulos = TitulosView(
            listar=self._uc_listar_titulo,
            obter=self._uc_obter_titulo,
            criar=self._uc_criar_titulo,
            editar=self._uc_editar_titulo,
            quitar=self._uc_quitar_titulo,
            cancelar=self._uc_cancelar_titulo,
            remover=self._uc_remover_titulo,
            listar_escritorios=self._uc_listar_esc,
            listar_empresas=self._uc_listar_emp,
            listar_contas_bancarias=self._uc_listar_conta,
            garantir_conta_padrao=self._uc_garantir_conta_padrao,
            relatorio_titulos=self._uc_relatorio_titulos,
            fluxo_caixa=self._uc_fluxo_caixa,
            projecao_financeira=self._uc_projecao_financeira,
            contexto_empresa=self._contexto_empresa,
            on_titulo_alterado=self._atualizar_dashboard_e_alertas,
        )
        self._stack.addWidget(self._view_titulos)

        # 3: Contas Bancarias (config)
        self._view_contas = ContasBancariasView(
            listar=self._uc_listar_conta,
            obter=self._uc_obter_conta,
            criar=self._uc_criar_conta,
            editar=self._uc_editar_conta,
            desativar=self._uc_desativar_conta,
            listar_empresas=self._uc_listar_emp,
            contexto_empresa=self._contexto_empresa,
        )
        self._stack.addWidget(self._view_contas)

        # 4: Empresas (config)
        self._view_empresas = EmpresasView(
            listar=self._uc_listar_emp,
            obter=self._uc_obter_emp,
            criar=self._uc_criar_emp,
            editar=self._uc_editar_emp,
            excluir=self._uc_excluir_emp,
            listar_escritorios=self._uc_listar_esc,
            on_empresas_alteradas=self._recarregar_empresas,
        )
        self._stack.addWidget(self._view_empresas)

        # 4: Escritorios (config)
        self._view_escritorios = EscritoriosView(
            listar=self._uc_listar_esc,
            obter=self._uc_obter_esc,
            criar=self._uc_criar_esc,
            editar=self._uc_editar_esc,
            excluir=self._uc_excluir_esc,
        )
        self._stack.addWidget(self._view_escritorios)

        # 5: Contadores (config)
        self._view_contadores = ContadoresView(
            listar=self._uc_listar_cont,
            obter=self._uc_obter_cont,
            criar=self._uc_criar_cont,
            editar=self._uc_editar_cont,
            excluir=self._uc_excluir_cont,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_contadores)

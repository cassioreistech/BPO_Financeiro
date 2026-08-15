"""Folha de estilo (QSS) do aplicativo."""

APP_STYLESHEET = """
/* === Geral === */
QMainWindow {
    background-color: #f8f9fa;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #1f2937;
}

/* === Sidebar === */
#sidebar {
    background-color: #1e293b;
    border-right: 1px solid #0f172a;
}

#logo {
    background-color: #1e293b;
    color: #f1f5f9;
    font-size: 15px;
    font-weight: bold;
    padding: 20px 16px;
    border: none;
    text-align: left;
}

#separator {
    background-color: #334155;
}

#navButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    text-align: left;
    padding: 12px 16px;
    font-size: 13px;
}

#navButton:hover {
    background-color: #334155;
    color: #e2e8f0;
}

#navButton[active="true"] {
    background-color: #334155;
    color: #ffffff;
    border-left: 3px solid #3b82f6;
}

/* === Conteudo === */
#contentArea {
    background-color: #f8f9fa;
}

/* === Titulos === */
#viewTitulo {
    font-size: 20px;
    font-weight: bold;
    color: #0f172a;
}

#formTitulo {
    font-size: 17px;
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 8px;
}

/* === Botoes === */
#btnPrimario {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    min-width: 120px;
}

#btnPrimario:hover {
    background-color: #2563eb;
}

#btnPrimario:pressed {
    background-color: #1d4ed8;
}

#btnSalvar {
    background-color: #22c55e;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    min-width: 100px;
}

#btnSalvar:hover {
    background-color: #16a34a;
}

#btnCancelar {
    background-color: #e5e7eb;
    color: #374151;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    min-width: 100px;
}

#btnCancelar:hover {
    background-color: #d1d5db;
}

QPushButton {
    background-color: #e5e7eb;
    color: #374151;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #d1d5db;
}

/* === Tabelas === */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    gridline-color: #f3f4f6;
    selection-background-color: #dbeafe;
    selection-color: #1e40af;
    font-size: 12px;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f3f4f6;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #1e40af;
}

QHeaderView::section {
    background-color: #f9fafb;
    color: #6b7280;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #e5e7eb;
}

/* === Formularios === */
QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #3b82f6;
    outline: none;
}

QLineEdit::placeholder {
    color: #9ca3af;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    selection-background-color: #dbeafe;
    selection-color: #1e40af;
}

QFormLayout QLabel {
    color: #374151;
    font-weight: bold;
    font-size: 12px;
}

/* === Dialog === */
QDialog {
    background-color: #f8f9fa;
}

/* === Scrollbar === */
QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #94a3b8;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

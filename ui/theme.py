"""
Design system: color palette, font sizes, and the master QSS stylesheet.
Dark premium theme with teal/purple accents.
"""


class Colors:
    """Centralized color tokens."""
    # ── Backgrounds ──
    BG_DARKEST   = "#080810"
    BG_DARK      = "#0c0c1d"
    BG_SURFACE   = "#12122a"
    BG_CARD      = "#181838"
    BG_ELEVATED  = "#1f1f42"
    BG_INPUT     = "#16163a"

    # ── Sidebar ──
    SIDEBAR_BG     = "#0a0a18"
    SIDEBAR_HOVER  = "#18183a"
    SIDEBAR_ACTIVE = "#1e1e4a"

    # ── Primary accent (teal-emerald) ──
    PRIMARY        = "#00d4aa"
    PRIMARY_HOVER  = "#00f0c0"
    PRIMARY_DARK   = "#009977"
    PRIMARY_BG     = "#00d4aa18"

    # ── Secondary accent (purple) ──
    SECONDARY       = "#7c3aed"
    SECONDARY_HOVER = "#9061f0"
    SECONDARY_BG    = "#7c3aed18"

    # ── Status colors ──
    SUCCESS   = "#10b981"
    WARNING   = "#f59e0b"
    DANGER    = "#ef4444"
    INFO      = "#3b82f6"

    SUCCESS_BG = "#10b98118"
    WARNING_BG = "#f59e0b18"
    DANGER_BG  = "#ef444418"
    INFO_BG    = "#3b82f618"

    # ── Text ──
    TEXT_PRIMARY   = "#e8ecf4"
    TEXT_SECONDARY = "#8892a8"
    TEXT_MUTED     = "#555e72"
    TEXT_ON_PRIMARY = "#080810"

    # ── Borders ──
    BORDER       = "#252548"
    BORDER_LIGHT = "#353560"

    # ── QSS Gradients ──
    GRAD_PRIMARY = (
        "qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        "stop:0 #00d4aa, stop:1 #7c3aed)"
    )
    GRAD_PRIMARY_HOVER = (
        "qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        "stop:0 #00f0c0, stop:1 #9061f0)"
    )
    GRAD_CARD = (
        "qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        "stop:0 #181838, stop:1 #12122a)"
    )
    GRAD_DANGER = (
        "qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        "stop:0 #ef4444, stop:1 #dc2626)"
    )


class Fonts:
    """Font tokens."""
    FAMILY  = "'Segoe UI', 'Roboto', 'Arial', sans-serif"
    SIZE_XS  = "10px"
    SIZE_SM  = "12px"
    SIZE_MD  = "14px"
    SIZE_LG  = "16px"
    SIZE_XL  = "20px"
    SIZE_2XL = "26px"
    SIZE_3XL = "34px"
    SIZE_4XL = "46px"


# ── Role metadata (icon emoji, sidebar color accent) ──
ROLE_META = {
    'admin':   {'icon': '🛡️', 'label': 'Admin',         'accent': Colors.DANGER},
    'funder':  {'icon': '💰', 'label': 'Funder',        'accent': Colors.PRIMARY},
    'analyst': {'icon': '📊', 'label': 'Data Analyst',  'accent': Colors.INFO},
    'survey':  {'icon': '📋', 'label': 'Survey Taker',  'accent': Colors.WARNING},
}


def get_main_stylesheet() -> str:
    """Return the global QSS stylesheet string."""
    C = Colors
    F = Fonts
    return f"""
    /* ═══════════════════ GLOBAL ═══════════════════ */
    QWidget {{
        background-color: {C.BG_DARK};
        color: {C.TEXT_PRIMARY};
        font-family: {F.FAMILY};
        font-size: {F.SIZE_MD};
    }}

    /* ═══════════════════ SCROLLBARS ═══════════════════ */
    QScrollBar:vertical {{
        background: {C.BG_DARKEST};
        width: 7px;
        border-radius: 3px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {C.BORDER};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {C.BORDER_LIGHT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {C.BG_DARKEST};
        height: 7px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal {{
        background: {C.BORDER};
        border-radius: 3px;
        min-width: 30px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ═══════════════════ INPUTS ═══════════════════ */
    QLineEdit {{
        background-color: {C.BG_INPUT};
        border: 1.5px solid {C.BORDER};
        border-radius: 10px;
        padding: 11px 16px;
        color: {C.TEXT_PRIMARY};
        font-size: {F.SIZE_MD};
        selection-background-color: {C.PRIMARY_DARK};
    }}
    QLineEdit:focus {{
        border: 1.5px solid {C.PRIMARY};
    }}
    QLineEdit:hover {{
        border: 1.5px solid {C.BORDER_LIGHT};
    }}

    QTextEdit, QPlainTextEdit {{
        background-color: {C.BG_INPUT};
        border: 1.5px solid {C.BORDER};
        border-radius: 10px;
        padding: 10px;
        color: {C.TEXT_PRIMARY};
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1.5px solid {C.PRIMARY};
    }}

    /* ═══════════════════ COMBO BOX ═══════════════════ */
    QComboBox {{
        background-color: {C.BG_INPUT};
        border: 1.5px solid {C.BORDER};
        border-radius: 10px;
        padding: 10px 16px;
        color: {C.TEXT_PRIMARY};
        min-width: 100px;
    }}
    QComboBox:hover {{
        border: 1.5px solid {C.BORDER_LIGHT};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 14px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C.BG_CARD};
        border: 1px solid {C.BORDER};
        color: {C.TEXT_PRIMARY};
        selection-background-color: {C.PRIMARY_DARK};
        padding: 4px;
        outline: none;
    }}

    /* ═══════════════════ LABELS ═══════════════════ */
    QLabel {{
        background: transparent;
        color: {C.TEXT_PRIMARY};
    }}

    /* ═══════════════════ TABLE ═══════════════════ */
    QTableWidget {{
        background-color: {C.BG_SURFACE};
        border: 1px solid {C.BORDER};
        border-radius: 10px;
        gridline-color: {C.BORDER};
        color: {C.TEXT_PRIMARY};
        font-size: {F.SIZE_SM};
        outline: none;
    }}
    QTableWidget::item {{
        padding: 6px 10px;
        border-bottom: 1px solid {C.BORDER};
    }}
    QTableWidget::item:selected {{
        background-color: {C.PRIMARY_DARK};
        color: {C.TEXT_PRIMARY};
    }}
    QTableWidget::item:hover {{
        background-color: {C.BG_ELEVATED};
    }}
    QHeaderView::section {{
        background-color: {C.BG_CARD};
        color: {C.PRIMARY};
        font-weight: bold;
        font-size: {F.SIZE_SM};
        padding: 8px 10px;
        border: none;
        border-bottom: 2px solid {C.PRIMARY_DARK};
    }}

    /* ═══════════════════ PROGRESS BAR ═══════════════════ */
    QProgressBar {{
        background-color: {C.BG_ELEVATED};
        border: none;
        border-radius: 6px;
        text-align: center;
        color: {C.TEXT_PRIMARY};
        font-size: {F.SIZE_XS};
        font-weight: bold;
        min-height: 14px;
        max-height: 14px;
    }}
    QProgressBar::chunk {{
        background: {C.GRAD_PRIMARY};
        border-radius: 6px;
    }}

    /* ═══════════════════ TOOLTIPS ═══════════════════ */
    QToolTip {{
        background-color: {C.BG_CARD};
        color: {C.TEXT_PRIMARY};
        border: 1px solid {C.BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {F.SIZE_SM};
    }}

    /* ═══════════════════ MESSAGE BOX ═══════════════════ */
    QMessageBox {{
        background-color: {C.BG_CARD};
    }}
    QMessageBox QLabel {{
        color: {C.TEXT_PRIMARY};
        font-size: {F.SIZE_MD};
    }}
    QMessageBox QPushButton {{
        background-color: {C.PRIMARY};
        color: {C.TEXT_ON_PRIMARY};
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: bold;
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {C.PRIMARY_HOVER};
    }}

    /* ═══════════════════ SPIN BOX ═══════════════════ */
    QDoubleSpinBox, QSpinBox {{
        background-color: {C.BG_INPUT};
        border: 1.5px solid {C.BORDER};
        border-radius: 10px;
        padding: 10px 14px;
        color: {C.TEXT_PRIMARY};
        font-size: {F.SIZE_MD};
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{
        border: 1.5px solid {C.PRIMARY};
    }}
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
    QSpinBox::up-button, QSpinBox::down-button {{
        width: 20px;
        border: none;
        background: {C.BG_ELEVATED};
    }}
    """

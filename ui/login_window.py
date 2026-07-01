"""
Login Window: animated role-selection + credential entry with particle-like effects.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsOpacityEffect, QSizePolicy, QSpacerItem,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize,
    pyqtSignal, QParallelAnimationGroup,
)
from PyQt6.QtGui import QCursor, QFont, QPainter, QColor, QLinearGradient

from ui.theme import Colors, Fonts, ROLE_META
from ui.components import (
    AnimatedButton, GlowButton, AnimatedLineEdit, Toast, Separator,
)

C = Colors
F = Fonts


class RoleCard(QFrame):
    """Clickable role-selection card with hover glow."""
    clicked = pyqtSignal(str)

    def __init__(self, role_key: str, parent=None):
        super().__init__(parent)
        meta = ROLE_META[role_key]
        self._role = role_key
        self._accent = meta['accent']
        self._selected = False

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(155, 140)

        self._set_normal_style()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        icon_lbl = QLabel(meta['icon'])
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 36px; background: transparent;")
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(meta['label'])
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(
            f"font-size: {F.SIZE_MD}; font-weight: 600; "
            f"color: {C.TEXT_PRIMARY}; background: transparent;"
        )
        layout.addWidget(name_lbl)

    def _set_normal_style(self):
        self.setStyleSheet(f"""
            .QFrame {{
                background-color: {C.BG_CARD};
                border: 1.5px solid {C.BORDER};
                border-radius: 16px;
            }}
            .QFrame:hover {{
                border: 1.5px solid {self._accent};
                background-color: {C.BG_ELEVATED};
            }}
        """)

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.setStyleSheet(f"""
                .QFrame {{
                    background-color: {C.BG_ELEVATED};
                    border: 2px solid {self._accent};
                    border-radius: 16px;
                }}
            """)
        else:
            self._set_normal_style()

    def mousePressEvent(self, event):
        self.clicked.emit(self._role)
        super().mousePressEvent(event)


class LoginWindow(QWidget):
    """Full-screen login window with role selection and credential entry."""
    login_success = pyqtSignal(str, str)  # role, username

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._selected_role = None
        self._role_cards = {}

        self.setStyleSheet(f"background-color: {C.BG_DARKEST};")
        self._build_ui()
        self._animate_entrance()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(0)

        # ── Container card ──
        container = QFrame()
        container.setObjectName("LoginContainer")
        container.setFixedSize(720, 620)
        container.setStyleSheet(f"""
            QFrame#LoginContainer {{
                background-color: {C.BG_SURFACE};
                border: 1px solid {C.BORDER};
                border-radius: 24px;
            }}
        """)
        card_layout = QVBoxLayout(container)
        card_layout.setContentsMargins(40, 32, 40, 32)
        card_layout.setSpacing(6)

        # ── Logo / Title ──
        logo_lbl = QLabel("💎")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("font-size: 42px; background: transparent;")
        card_layout.addWidget(logo_lbl)

        title = QLabel("Fund Raising Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: {F.SIZE_XL}; font-weight: 700; "
            f"color: {C.PRIMARY}; background: transparent; letter-spacing: 0.5px;"
        )
        card_layout.addWidget(title)

        subtitle = QLabel("Transparent · Secure · Accountable")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"font-size: {F.SIZE_SM}; color: {C.TEXT_SECONDARY}; background: transparent;"
        )
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(16)

        # ── Role Selection ──
        role_label = QLabel("SELECT YOUR ROLE")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_label.setStyleSheet(
            f"font-size: {F.SIZE_SM}; font-weight: 600; color: {C.TEXT_MUTED}; "
            f"letter-spacing: 2px; background: transparent;"
        )
        card_layout.addWidget(role_label)

        card_layout.addSpacing(8)

        roles_row = QHBoxLayout()
        roles_row.setSpacing(24)
        roles_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for role_key in ['admin', 'funder', 'analyst', 'survey']:
            card = RoleCard(role_key)
            card.clicked.connect(self._on_role_selected)
            self._role_cards[role_key] = card
            roles_row.addWidget(card)
        card_layout.addLayout(roles_row)

        card_layout.addSpacing(16)

        # ── Credentials ──
        self.cred_frame = QFrame()
        self.cred_frame.setStyleSheet("background: transparent;")
        cred_layout = QVBoxLayout(self.cred_frame)
        cred_layout.setContentsMargins(40, 0, 40, 0)
        cred_layout.setSpacing(12)

        self.username_input = AnimatedLineEdit("Enter username")
        cred_layout.addWidget(self.username_input)

        self.password_input = AnimatedLineEdit("Enter password", is_password=True)
        self.password_input.returnPressed.connect(self._attempt_login)
        cred_layout.addWidget(self.password_input)

        self.login_btn = GlowButton("Sign In")
        self.login_btn.clicked.connect(self._attempt_login)
        cred_layout.addWidget(self.login_btn)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet(
            f"color: {C.DANGER}; font-size: {F.SIZE_SM}; background: transparent;"
        )
        cred_layout.addWidget(self.error_label)

        card_layout.addWidget(self.cred_frame)
        self.cred_frame.setVisible(False)

        # ── Hint ──
        self.hint_label = QLabel("↑  Select a role to continue")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(
            f"color: {C.TEXT_MUTED}; font-size: {F.SIZE_SM}; background: transparent;"
        )
        card_layout.addWidget(self.hint_label)

        card_layout.addStretch()

        # ── Footer ──
        footer = QLabel("Developed for Fund Raising Management · 2025")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"color: {C.TEXT_MUTED}; font-size: {F.SIZE_XS}; background: transparent;"
        )
        card_layout.addWidget(footer)

        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Opacity effect for the whole container (for entrance animation)
        self._container = container
        self._opacity = QGraphicsOpacityEffect(container)
        container.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

    def _animate_entrance(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(600)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_role_selected(self, role: str):
        self._selected_role = role
        # Update card visuals
        for key, card in self._role_cards.items():
            card.set_selected(key == role)

        # Show credentials with animation
        self.hint_label.setVisible(False)
        self.cred_frame.setVisible(True)
        self.error_label.setText("")

        # Animate cred_frame fade-in
        effect = QGraphicsOpacityEffect(self.cred_frame)
        self.cred_frame.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: self.cred_frame.setGraphicsEffect(None))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        self.username_input.setFocus()

        # Update button accent
        accent = ROLE_META[role]['accent']
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: {C.TEXT_ON_PRIMARY};
                border: none;
                border-radius: 12px;
                padding: 12px 32px;
                font-weight: 700;
                font-size: {F.SIZE_LG};
                font-family: {F.FAMILY};
            }}
            QPushButton:hover {{
                background-color: {QColor(accent).lighter(115).name()};
            }}
        """)

    def _attempt_login(self):
        if not self._selected_role:
            self.error_label.setText("Please select a role first")
            return

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username:
            self.error_label.setText("Please enter your username")
            self._shake(self.username_input)
            return

        if not password:
            self.error_label.setText("Please enter your password")
            self._shake(self.password_input)
            return

        if self.dm.authenticate(self._selected_role, username, password):
            self.error_label.setText("")
            self.login_success.emit(self._selected_role, username)
        else:
            self.error_label.setText("❌  Invalid credentials. Please try again.")
            self._shake(self.password_input)
            self.password_input.clear()

    def _shake(self, widget):
        """Horizontal shake animation for invalid input."""
        from PyQt6.QtCore import QPoint
        original_pos = widget.pos()
        anim = QPropertyAnimation(widget, b"pos", self)
        anim.setDuration(300)
        anim.setKeyValueAt(0, original_pos)
        anim.setKeyValueAt(0.15, original_pos + QPoint(8, 0))
        anim.setKeyValueAt(0.3, original_pos + QPoint(-8, 0))
        anim.setKeyValueAt(0.45, original_pos + QPoint(6, 0))
        anim.setKeyValueAt(0.6, original_pos + QPoint(-4, 0))
        anim.setKeyValueAt(0.75, original_pos + QPoint(2, 0))
        anim.setKeyValueAt(1, original_pos)
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def reset(self):
        """Reset login form for next use."""
        self._selected_role = None
        for card in self._role_cards.values():
            card.set_selected(False)
        self.cred_frame.setVisible(False)
        self.hint_label.setVisible(True)
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setText("")

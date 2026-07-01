"""
Reusable animated UI components:
  AnimatedButton, GlowButton, SidebarButton,
  StatCard, GlowCard, HeaderLabel, AnimatedLineEdit,
  FadeStackedWidget, Toast
"""

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QStackedWidget, QGraphicsOpacityEffect, QSizePolicy,
    QFrame,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, pyqtSignal,
    QParallelAnimationGroup, QPoint, QRect,
)
from PyQt6.QtGui import (
    QCursor, QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QIcon,
)
from ui.theme import Colors, Fonts

C = Colors
F = Fonts


# ═══════════════════════════════════════════════════════════
#  ANIMATED BUTTON  –  hover color shift + cursor change
# ═══════════════════════════════════════════════════════════
class AnimatedButton(QPushButton):
    """A styled push-button with hover animation and pointer cursor."""

    def __init__(self, text="", color=C.PRIMARY, hover_color=None,
                 text_color=C.TEXT_ON_PRIMARY, radius=10, parent=None,
                 icon_text="", min_height=44):
        super().__init__(text, parent)
        self._color = color
        self._hover = hover_color or self._lighter(color)
        self._text_color = text_color
        self._radius = radius
        self._icon_text = icon_text

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(min_height)
        self._apply_style(self._color)

    # noinspection PyMethodMayBeStatic
    def _lighter(self, hex_color: str) -> str:
        c = QColor(hex_color)
        c = c.lighter(120)
        return c.name()

    def _apply_style(self, bg):
        prefix = self._icon_text + "  " if self._icon_text else ""
        self.setText(prefix + self.text().lstrip(self._icon_text).strip() if self._icon_text else self.text())
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {self._text_color};
                border: none;
                border-radius: {self._radius}px;
                padding: 10px 22px;
                font-weight: 600;
                font-size: {F.SIZE_MD};
                font-family: {F.FAMILY};
            }}
        """)

    def enterEvent(self, event):
        self._apply_style(self._hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_style(self._color)
        super().leaveEvent(event)


# ═══════════════════════════════════════════════════════════
#  GLOW BUTTON  –  gradient background + glow on hover
# ═══════════════════════════════════════════════════════════
class GlowButton(QPushButton):
    """Primary CTA button with gradient background."""

    def __init__(self, text="", parent=None, min_height=48):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(min_height)
        self._set_normal()

    def _set_normal(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {C.GRAD_PRIMARY};
                color: {C.TEXT_ON_PRIMARY};
                border: none;
                border-radius: 12px;
                padding: 12px 32px;
                font-weight: 700;
                font-size: {F.SIZE_LG};
                font-family: {F.FAMILY};
                letter-spacing: 0.5px;
            }}
        """)

    def _set_hover(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {C.GRAD_PRIMARY_HOVER};
                color: {C.TEXT_ON_PRIMARY};
                border: none;
                border-radius: 12px;
                padding: 12px 32px;
                font-weight: 700;
                font-size: {F.SIZE_LG};
                font-family: {F.FAMILY};
                letter-spacing: 0.5px;
            }}
        """)

    def enterEvent(self, event):
        self._set_hover()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._set_normal()
        super().leaveEvent(event)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR BUTTON  –  nav item with active indicator
# ═══════════════════════════════════════════════════════════
class SidebarButton(QPushButton):
    """Sidebar navigation button with left accent bar when active."""

    def __init__(self, text="", icon_text="", parent=None):
        display = f"  {icon_text}   {text}" if icon_text else f"  {text}"
        super().__init__(display, parent)
        self._active = False
        self._icon_text = icon_text
        self._base_text = text
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(46)
        self.setCheckable(True)
        self._update_style()

    def set_active(self, active: bool):
        self._active = active
        self.setChecked(active)
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C.SIDEBAR_ACTIVE};
                    color: {C.PRIMARY};
                    border: none;
                    border-left: 3px solid {C.PRIMARY};
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-weight: 600;
                    font-size: {F.SIZE_MD};
                    font-family: {F.FAMILY};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {C.TEXT_SECONDARY};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-size: {F.SIZE_MD};
                    font-family: {F.FAMILY};
                }}
                QPushButton:hover {{
                    background-color: {C.SIDEBAR_HOVER};
                    color: {C.TEXT_PRIMARY};
                }}
            """)

    def enterEvent(self, event):
        if not self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C.SIDEBAR_HOVER};
                    color: {C.TEXT_PRIMARY};
                    border: none;
                    border-left: 3px solid {C.BORDER_LIGHT};
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-size: {F.SIZE_MD};
                    font-family: {F.FAMILY};
                }}
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._update_style()
        super().leaveEvent(event)


# ═══════════════════════════════════════════════════════════
#  STAT CARD  –  metric display with icon + animated counter
# ═══════════════════════════════════════════════════════════
class StatCard(QFrame):
    """Card displaying a single metric: icon, value, label."""

    def __init__(self, icon_text="📊", value="0", label="Metric",
                 accent=C.PRIMARY, parent=None):
        super().__init__(parent)
        self._accent = accent
        self.setFixedHeight(120)
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.setStyleSheet(f"""
            .QFrame {{
                background-color: {C.BG_CARD};
                border: 1px solid {C.BORDER};
                border-radius: 14px;
                padding: 0px;
            }}
            .QFrame:hover {{
                border: 1px solid {accent};
                background-color: {C.BG_ELEVATED};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        # Icon + label row
        top = QHBoxLayout()
        icon_lbl = QLabel(icon_text)
        icon_lbl.setStyleSheet(f"font-size: 22px; background: transparent;")
        top.addWidget(icon_lbl)
        top.addStretch()

        label_lbl = QLabel(label)
        label_lbl.setStyleSheet(
            f"color: {C.TEXT_SECONDARY}; font-size: {F.SIZE_SM}; background: transparent;")
        top.addWidget(label_lbl)
        layout.addLayout(top)

        layout.addStretch()

        # Value
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setStyleSheet(
            f"color: {accent}; font-size: {F.SIZE_2XL}; font-weight: 700; background: transparent;")
        layout.addWidget(self.value_lbl)

    def set_value(self, val):
        self.value_lbl.setText(str(val))


# ═══════════════════════════════════════════════════════════
#  GLOW CARD  –  container with subtle border glow
# ═══════════════════════════════════════════════════════════
class GlowCard(QFrame):
    """A card frame with rounded corners and hover glow."""

    def __init__(self, parent=None, accent=C.PRIMARY):
        super().__init__(parent)
        self._accent = accent
        self.setStyleSheet(f"""
            .QFrame {{
                background-color: {C.BG_CARD};
                border: 1px solid {C.BORDER};
                border-radius: 14px;
            }}
            .QFrame:hover {{
                border: 1px solid {accent};
            }}
        """)


# ═══════════════════════════════════════════════════════════
#  HEADER LABEL  –  page title with accent underline
# ═══════════════════════════════════════════════════════════
class HeaderLabel(QWidget):
    """A styled page header: title + optional subtitle + accent bar."""

    def __init__(self, title="", subtitle="", accent=C.PRIMARY, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: {F.SIZE_2XL}; font-weight: 700; color: {C.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet(
                f"font-size: {F.SIZE_SM}; color: {C.TEXT_SECONDARY}; background: transparent;")
            layout.addWidget(sub_lbl)

        # Accent bar
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"background: {accent}; border-radius: 1px;")
        layout.addWidget(bar)


# ═══════════════════════════════════════════════════════════
#  ANIMATED LINE EDIT  –  input with focus glow
# ═══════════════════════════════════════════════════════════
class AnimatedLineEdit(QLineEdit):
    """QLineEdit with pointer cursor on hover."""

    def __init__(self, placeholder="", parent=None, is_password=False):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        if is_password:
            self.setEchoMode(QLineEdit.EchoMode.Password)


# ═══════════════════════════════════════════════════════════
#  FADE STACKED WIDGET  –  page transitions with opacity
# ═══════════════════════════════════════════════════════════
class FadeStackedWidget(QStackedWidget):
    """QStackedWidget that fades between pages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._duration = 250

    def fade_to(self, index: int):
        if index == self.currentIndex():
            return
        next_widget = self.widget(index)
        if next_widget is None:
            return

        # Set up opacity effect on the incoming page
        effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        self.setCurrentIndex(index)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(self._duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(lambda: next_widget.setGraphicsEffect(None))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


# ═══════════════════════════════════════════════════════════
#  TOAST  –  temporary notification popup
# ═══════════════════════════════════════════════════════════
class Toast(QLabel):
    """A brief notification that fades in, stays, then fades out."""

    def __init__(self, message: str, parent=None, duration_ms=2500,
                 bg=C.SUCCESS, text_color=C.TEXT_ON_PRIMARY):
        super().__init__(message, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {text_color};
                font-size: {F.SIZE_MD};
                font-weight: 600;
                padding: 12px 28px;
                border-radius: 10px;
                font-family: {F.FAMILY};
            }}
        """)
        self.setFixedHeight(44)
        self.adjustSize()
        self.setMinimumWidth(250)

        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(0.0)

        self._duration = duration_ms

    def show_toast(self):
        """Position at the bottom-center of parent and animate."""
        if self.parent():
            pw = self.parent().width()
            ph = self.parent().height()
            self.move(
                (pw - self.width()) // 2,
                ph - self.height() - 30
            )

        self.show()
        self.raise_()

        # Fade in
        fade_in = QPropertyAnimation(self._effect, b"opacity", self)
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out after duration
        fade_out = QPropertyAnimation(self._effect, b"opacity", self)
        fade_out.setDuration(400)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out.finished.connect(self.deleteLater)

        fade_in.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer.singleShot(self._duration, lambda: fade_out.start(
            QPropertyAnimation.DeletionPolicy.DeleteWhenStopped))


# ═══════════════════════════════════════════════════════════
#  SEPARATOR  –  thin horizontal line
# ═══════════════════════════════════════════════════════════
class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {C.BORDER};")

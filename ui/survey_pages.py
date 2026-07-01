"""
Survey-taker role pages:
  SurveyDashboardPage, FillSurveyPage, SurveyFAQPage
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QDoubleSpinBox, QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from ui.theme import Colors, Fonts
from ui.components import (
    AnimatedButton, GlowButton, StatCard, GlowCard,
    HeaderLabel, AnimatedLineEdit, Toast, Separator,
)

C = Colors
F = Fonts


# ═══════════════════════════════════════════════════════════
#  1. SURVEY DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════
class SurveyDashboardPage(QWidget):
    """Welcome dashboard showing the survey taker's submission stats."""

    # Signal-like callback: set by the parent shell so the quick-action
    # button can navigate to the FillSurveyPage.
    navigate_to_fill = None  # callable, set externally

    def __init__(self, dm, taker_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.taker_user = taker_user
        self._build_ui()
        self.refresh_data()

    # ── UI ──
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        root.addWidget(HeaderLabel(
            "📋  Survey Dashboard",
            f"Welcome back, {self.taker_user}!",
            accent=C.WARNING,
        ))

        # Welcome card
        welcome = GlowCard(accent=C.WARNING)
        wl = QVBoxLayout(welcome)
        wl.setContentsMargins(22, 18, 22, 18)
        wl.setSpacing(8)

        wt = QLabel(f"Hello, {self.taker_user}! 👋")
        wt.setStyleSheet(
            f"font-size: {F.SIZE_XL}; font-weight: 700; color: {C.TEXT_PRIMARY}; background: transparent;")
        ws = QLabel(
            "Your survey submissions help identify communities in need. "
            "Fill a new survey from the sidebar or use the quick-action button below."
        )
        ws.setStyleSheet(f"font-size: {F.SIZE_SM}; color: {C.TEXT_SECONDARY}; background: transparent;")
        ws.setWordWrap(True)
        wl.addWidget(wt)
        wl.addWidget(ws)
        root.addWidget(welcome)

        # Stat cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self.card_submitted = StatCard("📝", "0", "My Surveys", C.WARNING)
        self.card_approved = StatCard("✅", "0", "Approved Surveys", C.SUCCESS)

        cards_row.addWidget(self.card_submitted)
        cards_row.addWidget(self.card_approved)
        cards_row.addStretch()
        root.addLayout(cards_row)

        # Quick-action
        root.addWidget(Separator())
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        action_lbl = QLabel("Quick Action:")
        action_lbl.setStyleSheet(
            f"font-size: {F.SIZE_MD}; font-weight: 600; color: {C.TEXT_SECONDARY}; background: transparent;")
        action_row.addWidget(action_lbl)

        self.btn_fill = GlowButton("📝  Fill New Survey")
        self.btn_fill.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_fill.setMaximumWidth(260)
        self.btn_fill.clicked.connect(self._on_fill_click)
        action_row.addWidget(self.btn_fill)
        action_row.addStretch()
        root.addLayout(action_row)

        root.addStretch()

    def _on_fill_click(self):
        if callable(self.navigate_to_fill):
            self.navigate_to_fill()

    # ── Data ──
    def refresh_data(self):
        df = self.dm.get_all_surveys()
        if df.empty:
            self.card_submitted.set_value("0")
            self.card_approved.set_value("0")
            return

        my = df[df["taker"] == self.taker_user]
        self.card_submitted.set_value(str(len(my)))
        approved = my[my["status"] == "Approved"] if not my.empty else my
        self.card_approved.set_value(str(len(approved)))


# ═══════════════════════════════════════════════════════════
#  2. FILL SURVEY PAGE
# ═══════════════════════════════════════════════════════════
class FillSurveyPage(QWidget):
    """Form to submit a new ground-level survey."""

    def __init__(self, dm, taker_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.taker_user = taker_user
        self._build_ui()

    # ── UI ──
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "📝  Fill New Survey",
            "Provide details about a community that needs funding support",
            accent=C.WARNING,
        ))

        # Form card
        form_card = GlowCard(accent=C.WARNING)
        fl = QVBoxLayout(form_card)
        fl.setContentsMargins(26, 22, 26, 22)
        fl.setSpacing(16)

        # Region
        fl.addWidget(self._field_label("Region / Area"))
        self.inp_region = AnimatedLineEdit("e.g. Sindh, Punjab, Islamabad…")
        fl.addWidget(self.inp_region)

        # Type of fund
        fl.addWidget(self._field_label("Type of Fund Needed"))
        self.inp_type = AnimatedLineEdit("e.g. Education, Healthcare, Infrastructure…")
        fl.addWidget(self.inp_type)

        # Amount
        fl.addWidget(self._field_label("Requested Amount ($)"))
        self.inp_amount = QDoubleSpinBox()
        self.inp_amount.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.inp_amount.setMinimum(1.0)
        self.inp_amount.setMaximum(999_999_999.0)
        self.inp_amount.setDecimals(2)
        self.inp_amount.setPrefix("$ ")
        self.inp_amount.setSingleStep(100.0)
        self.inp_amount.setValue(1000.0)
        self.inp_amount.setMinimumHeight(44)
        fl.addWidget(self.inp_amount)

        # Description
        fl.addWidget(self._field_label("Description of Need"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.inp_desc.setPlaceholderText(
            "Describe the community's situation, the urgency, "
            "and how the funds would be used…"
        )
        self.inp_desc.setMinimumHeight(110)
        self.inp_desc.setMaximumHeight(180)
        fl.addWidget(self.inp_desc)

        root.addWidget(form_card)

        # Submit button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_submit = GlowButton("✅  Submit Survey")
        self.btn_submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_submit.setMinimumWidth(220)
        self.btn_submit.clicked.connect(self._on_submit)
        btn_row.addWidget(self.btn_submit)
        btn_row.addStretch()
        root.addLayout(btn_row)

        root.addStretch()

    @staticmethod
    def _field_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: {F.SIZE_MD}; font-weight: 600; color: {C.TEXT_SECONDARY}; "
            f"background: transparent; padding-left: 2px;")
        return lbl

    # ── Submit ──
    def _on_submit(self):
        region = self.inp_region.text().strip()
        fund_type = self.inp_type.text().strip()
        amount = self.inp_amount.value()
        description = self.inp_desc.toPlainText().strip()

        # Validation
        errors = []
        if not region:
            errors.append("Region / Area is required.")
        if not fund_type:
            errors.append("Type of fund is required.")
        if amount <= 0:
            errors.append("Amount must be greater than zero.")
        if not description:
            errors.append("Description is required.")

        if errors:
            Toast(
                " | ".join(errors),
                parent=self,
                bg=C.DANGER,
                text_color="#fff",
            ).show_toast()
            return

        try:
            survey_id = self.dm.submit_survey(
                region=region,
                fund_type=fund_type,
                amount=amount,
                description=description,
                taker=self.taker_user,
            )
            Toast(
                f"✅  Survey submitted!  ID: {survey_id}",
                parent=self,
                bg=C.SUCCESS,
            ).show_toast()
            self._clear_form()
        except Exception as e:
            Toast(
                f"Error: {e}",
                parent=self,
                bg=C.DANGER,
                text_color="#fff",
            ).show_toast()

    def _clear_form(self):
        self.inp_region.clear()
        self.inp_type.clear()
        self.inp_amount.setValue(1000.0)
        self.inp_desc.clear()

    def refresh_data(self):
        """No table to refresh; exists for interface consistency."""
        pass


# ═══════════════════════════════════════════════════════════
#  3. SURVEY FAQ PAGE
# ═══════════════════════════════════════════════════════════
class SurveyFAQPage(QWidget):
    """Frequently asked questions for the survey taker role."""

    def __init__(self, dm, taker_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.taker_user = taker_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "❓  Frequently Asked Questions",
            "Common questions about the survey process",
            accent=C.WARNING,
        ))

        faqs = [
            (
                "Who can fill surveys?",
                "Surveys are filled by designated Survey Takers – field workers, community "
                "liaisons, or volunteers who have firsthand knowledge of a region's needs. "
                "Each survey taker logs in with the 'Survey Taker' role and their username "
                "is automatically recorded with every submission for accountability and tracking."
            ),
            (
                "How are submitted surveys used?",
                "Once submitted, surveys enter a 'Pending' state and are reviewed by the Admin. "
                "If an admin deems the survey valid, they can approve it and create a fundraising "
                "campaign directly from the survey data. The campaign inherits the region, fund type, "
                "requested amount, and description from the survey. This ensures that every campaign "
                "is rooted in real, ground-level needs.\n\n"
                "You can track the status of your surveys on the Dashboard page – the 'Approved' "
                "counter shows how many of your submissions have been turned into active campaigns."
            ),
        ]

        for question, answer in faqs:
            card = GlowCard(accent=C.WARNING)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(22, 18, 22, 18)
            cl.setSpacing(8)

            q_lbl = QLabel(f"Q:  {question}")
            q_lbl.setStyleSheet(
                f"font-size: {F.SIZE_LG}; font-weight: 700; color: {C.WARNING}; background: transparent;")
            q_lbl.setWordWrap(True)
            cl.addWidget(q_lbl)

            a_lbl = QLabel(f"A:  {answer}")
            a_lbl.setStyleSheet(
                f"font-size: {F.SIZE_MD}; color: {C.TEXT_SECONDARY}; background: transparent; line-height: 1.5;")
            a_lbl.setWordWrap(True)
            cl.addWidget(a_lbl)

            root.addWidget(card)

        root.addStretch()

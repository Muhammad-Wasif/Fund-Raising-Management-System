"""
Admin role pages:
  AdminDashboardPage, CreateCampaignPage, ViewSurveysPage,
  DonationReportPage, ViewInvoicesPage, AdminFAQPage
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QScrollArea,
    QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QColor

from ui.theme import Colors, Fonts
from ui.components import (
    AnimatedButton, GlowButton, StatCard, GlowCard,
    HeaderLabel, AnimatedLineEdit, Toast, Separator,
)

C = Colors
F = Fonts


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _make_table(columns: list[str], parent=None) -> QTableWidget:
    """Create a consistently-styled QTableWidget."""
    table = QTableWidget(0, len(columns), parent)
    table.setHorizontalHeaderLabels(columns)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(False)
    table.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    table.setShowGrid(False)
    return table


def _item(text: str, align=Qt.AlignmentFlag.AlignCenter) -> QTableWidgetItem:
    """Create a centered, read-only table item."""
    it = QTableWidgetItem(str(text))
    it.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
    return it


def _colored_item(text: str, color: str) -> QTableWidgetItem:
    it = _item(text)
    it.setForeground(QColor(color))
    return it


def _quick_btn(text: str, icon: str = "", color=C.BG_ELEVATED,
               hover=C.BORDER_LIGHT) -> AnimatedButton:
    btn = AnimatedButton(
        text, color=color, hover_color=hover,
        text_color=C.TEXT_PRIMARY, radius=12, icon_text=icon, min_height=48,
    )
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return btn


def _scrollable(inner_widget: QWidget) -> QScrollArea:
    """Wrap *inner_widget* in a transparent QScrollArea."""
    sa = QScrollArea()
    sa.setWidget(inner_widget)
    sa.setWidgetResizable(True)
    sa.setStyleSheet("QScrollArea{background:transparent;border:none;}")
    return sa


# ═══════════════════════════════════════════════════════════════
#  1.  ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════
class AdminDashboardPage(QWidget):
    """Main admin overview with stat cards and quick-action buttons."""

    # Signals so the parent shell can navigate
    navigate = pyqtSignal(str)  # emits page key like "create_campaign"

    def __init__(self, dm, admin_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.admin_user = admin_user
        self._build_ui()

    # ── UI ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Welcome header
        self.header = HeaderLabel(
            f"Welcome back, {self.admin_user}  🛡️",
            "Admin Dashboard  •  Manage campaigns, surveys & donations",
            accent=C.DANGER,
        )
        root.addWidget(self.header)

        # ── Stat cards row ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_campaigns = StatCard("📂", "0", "Total Campaigns", C.PRIMARY)
        self.card_active    = StatCard("🚀", "0", "Active Campaigns", C.SUCCESS)
        self.card_donations = StatCard("💵", "$0", "Total Donations", C.INFO)
        self.card_surveys   = StatCard("📋", "0", "Pending Surveys", C.WARNING)

        for card in (self.card_campaigns, self.card_active,
                     self.card_donations, self.card_surveys):
            cards_row.addWidget(card)

        root.addLayout(cards_row)

        root.addWidget(Separator())

        # ── Quick actions ──
        actions_lbl = QLabel("⚡  Quick Actions")
        actions_lbl.setStyleSheet(
            f"font-size:{F.SIZE_LG};font-weight:700;color:{C.TEXT_PRIMARY};"
            f"background:transparent;")
        root.addWidget(actions_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        self.btn_create   = _quick_btn("Create Campaign", "📂")
        self.btn_surveys  = _quick_btn("View Surveys", "📋")
        self.btn_donations = _quick_btn("Donation Report", "💰")
        self.btn_invoices = _quick_btn("View Invoices", "🧾")
        self.btn_faq      = _quick_btn("FAQ", "❓")

        self.btn_create.clicked.connect(lambda: self.navigate.emit("create_campaign"))
        self.btn_surveys.clicked.connect(lambda: self.navigate.emit("view_surveys"))
        self.btn_donations.clicked.connect(lambda: self.navigate.emit("donation_report"))
        self.btn_invoices.clicked.connect(lambda: self.navigate.emit("view_invoices"))
        self.btn_faq.clicked.connect(lambda: self.navigate.emit("admin_faq"))

        for b in (self.btn_create, self.btn_surveys, self.btn_donations,
                  self.btn_invoices, self.btn_faq):
            btn_row.addWidget(b)

        root.addLayout(btn_row)
        root.addStretch()

    # ── Data ────────────────────────────────────────────
    def refresh_data(self):
        stats = self.dm.get_financial_stats()
        self.card_campaigns.set_value(str(stats.get("total_campaigns", 0)))

        active = self.dm.get_active_campaigns()
        self.card_active.set_value(str(len(active)))

        total_amt = stats.get("total_raised", 0)
        self.card_donations.set_value(f"${total_amt:,.0f}")

        pending = self.dm.get_pending_surveys()
        self.card_surveys.set_value(str(len(pending)))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  2.  CREATE CAMPAIGN
# ═══════════════════════════════════════════════════════════════
class CreateCampaignPage(QWidget):
    """Select a pending survey → name project → create campaign."""

    def __init__(self, dm, admin_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.admin_user = admin_user
        self._selected_survey_idx = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "Create Campaign",
            "Select a pending survey and assign a project name",
            accent=C.PRIMARY,
        ))

        # ── Table ──
        self.table = _make_table(
            ["ID", "Region", "Type", "Amount", "Description", "Status"])
        self.table.cellClicked.connect(self._on_row_clicked)
        root.addWidget(self.table, 1)

        # ── Selected info ──
        self.sel_label = QLabel("No survey selected")
        self.sel_label.setStyleSheet(
            f"color:{C.TEXT_SECONDARY};font-size:{F.SIZE_MD};background:transparent;")
        root.addWidget(self.sel_label)

        # ── Project name ──
        form_row = QHBoxLayout()
        form_row.setSpacing(12)

        name_lbl = QLabel("Project Name:")
        name_lbl.setStyleSheet(
            f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
        form_row.addWidget(name_lbl)

        self.name_input = AnimatedLineEdit("Enter project name …")
        self.name_input.setMinimumHeight(44)
        form_row.addWidget(self.name_input, 1)

        self.btn_create = GlowButton("🚀  Create Campaign")
        self.btn_create.clicked.connect(self._create_campaign)
        form_row.addWidget(self.btn_create)

        root.addLayout(form_row)

    # ── Interaction ─────────────────────────────────────
    def _on_row_clicked(self, row, _col):
        idx_item = self.table.item(row, 0)
        if idx_item:
            self._selected_survey_idx = idx_item.data(Qt.ItemDataRole.UserRole)
            self.sel_label.setText(
                f"✅  Selected survey: {idx_item.text()}  (row {row + 1})")
            self.sel_label.setStyleSheet(
                f"color:{C.SUCCESS};font-size:{F.SIZE_MD};background:transparent;")

    def _create_campaign(self):
        if self._selected_survey_idx is None:
            Toast("⚠️  Please select a survey first", self, bg=C.WARNING).show_toast()
            return

        name = self.name_input.text().strip()
        if not name:
            Toast("⚠️  Please enter a project name", self, bg=C.WARNING).show_toast()
            return

        try:
            cid = self.dm.create_campaign_from_survey(
                self._selected_survey_idx, name, self.admin_user)
            Toast(f"✅  Campaign {cid} created!", self, bg=C.SUCCESS).show_toast()
            self.name_input.clear()
            self._selected_survey_idx = None
            self.sel_label.setText("No survey selected")
            self.sel_label.setStyleSheet(
                f"color:{C.TEXT_SECONDARY};font-size:{F.SIZE_MD};background:transparent;")
            self.refresh_data()
        except Exception as e:
            Toast(f"❌  Error: {e}", self, bg=C.DANGER).show_toast()

    # ── Data ────────────────────────────────────────────
    def refresh_data(self):
        df = self.dm.get_pending_surveys()
        self.table.setRowCount(0)
        if df.empty:
            return
        for _, r in df.iterrows():
            row = self.table.rowCount()
            self.table.insertRow(row)
            id_item = _item(str(r.get("id", "")))
            id_item.setData(Qt.ItemDataRole.UserRole, r.get("index"))
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, _item(str(r.get("region", ""))))
            self.table.setItem(row, 2, _item(str(r.get("type", ""))))
            self.table.setItem(row, 3, _item(f"${float(r.get('amount', 0)):,.0f}"))
            self.table.setItem(row, 4, _item(str(r.get("description", ""))))
            status = str(r.get("status", ""))
            color = C.SUCCESS if status == "Approved" else C.WARNING
            self.table.setItem(row, 5, _colored_item(status, color))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  3.  VIEW SURVEYS
# ═══════════════════════════════════════════════════════════════
class ViewSurveysPage(QWidget):
    """Read-only table of every submitted survey."""

    def __init__(self, dm, admin_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.admin_user = admin_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        # Header + refresh btn
        top_row = QHBoxLayout()
        top_row.addWidget(HeaderLabel(
            "All Surveys", "Complete survey history", accent=C.INFO))
        top_row.addStretch()

        self.btn_refresh = AnimatedButton(
            "🔄  Refresh", color=C.BG_ELEVATED, hover_color=C.BORDER_LIGHT,
            text_color=C.TEXT_PRIMARY, min_height=40)
        self.btn_refresh.clicked.connect(self.refresh_data)
        top_row.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addLayout(top_row)

        self.table = _make_table([
            "ID", "Region", "Type", "Amount", "Description",
            "Taker", "Submitted", "Status",
        ])
        root.addWidget(self.table, 1)

    def refresh_data(self):
        df = self.dm.get_all_surveys()
        self.table.setRowCount(0)
        if df.empty:
            return
        for _, r in df.iterrows():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, _item(str(r.get("id", ""))))
            self.table.setItem(row, 1, _item(str(r.get("region", ""))))
            self.table.setItem(row, 2, _item(str(r.get("type", ""))))
            self.table.setItem(row, 3, _item(f"${float(r.get('amount', 0)):,.0f}"))
            desc = str(r.get("description", ""))
            self.table.setItem(row, 4, _item(desc[:60] + "…" if len(desc) > 60 else desc))
            self.table.setItem(row, 5, _item(str(r.get("taker", ""))))
            self.table.setItem(row, 6, _item(str(r.get("submitted", ""))))
            status = str(r.get("status", ""))
            color = C.SUCCESS if status == "Approved" else C.WARNING
            self.table.setItem(row, 7, _colored_item(status, color))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  4.  DONATION REPORT
# ═══════════════════════════════════════════════════════════════
class DonationReportPage(QWidget):
    """All donations in a table with total stat card at bottom."""

    def __init__(self, dm, admin_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.admin_user = admin_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "Donation Report",
            "Complete record of all donations received",
            accent=C.SUCCESS,
        ))

        self.table = _make_table([
            "Donation ID", "Campaign", "Funder", "Amount",
            "Payment Method", "Date",
        ])
        root.addWidget(self.table, 1)

        # Bottom stat
        self.total_card = StatCard("💰", "$0", "Total Donated", C.SUCCESS)
        root.addWidget(self.total_card)

    def refresh_data(self):
        df = self.dm.get_all_donations()
        self.table.setRowCount(0)
        total = 0.0
        if df.empty:
            self.total_card.set_value("$0")
            return
        for _, r in df.iterrows():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, _item(str(r.get("donation_id", ""))))
            cname = self.dm.get_campaign_name(r.get("campaign_id", ""))
            self.table.setItem(row, 1, _item(cname))
            self.table.setItem(row, 2, _item(str(r.get("funder_user", ""))))
            amt = float(r.get("amount", 0))
            total += amt
            self.table.setItem(row, 3, _item(f"${amt:,.2f}"))
            self.table.setItem(row, 4, _item(str(r.get("payment_method", ""))))
            self.table.setItem(row, 5, _item(str(r.get("date", ""))))

        self.total_card.set_value(f"${total:,.2f}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  5.  VIEW INVOICES
# ═══════════════════════════════════════════════════════════════
class ViewInvoicesPage(QWidget):
    """Invoice listing derived from all donation records."""

    def __init__(self, dm, admin_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.admin_user = admin_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "Invoices", "Financial records for every donation",
            accent=C.SECONDARY,
        ))

        self.table = _make_table([
            "Invoice ID", "Challan #", "Campaign", "Amount",
            "Payment Method", "Date",
        ])
        root.addWidget(self.table, 1)

    def refresh_data(self):
        df = self.dm.get_all_donations()
        self.table.setRowCount(0)
        if df.empty:
            return
        for _, r in df.iterrows():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, _item(str(r.get("invoice_id", ""))))
            self.table.setItem(row, 1, _item(str(r.get("challan_id", ""))))
            cname = self.dm.get_campaign_name(r.get("campaign_id", ""))
            self.table.setItem(row, 2, _item(cname))
            self.table.setItem(row, 3, _item(f"${float(r.get('amount', 0)):,.2f}"))
            self.table.setItem(row, 4, _item(str(r.get("payment_method", ""))))
            self.table.setItem(row, 5, _item(str(r.get("date", ""))))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  6.  ADMIN FAQ
# ═══════════════════════════════════════════════════════════════
class AdminFAQPage(QWidget):
    """Expandable FAQ cards for the admin role."""

    _FAQ = [
        ("How is data stored?",
         "All data is stored in CSV files inside the /data directory. "
         "There are four files: campaigns.csv, donations.csv, surveys.csv, "
         "and funders.csv. The DataManager class handles reading, writing, "
         "and schema initialization automatically."),
        ("When is data saved?",
         "Data is saved automatically after every mutation — creating a "
         "campaign, processing a donation, or submitting a survey. You can "
         "also trigger a manual save from the menu if available."),
        ("How is data loaded at startup?",
         "On startup the DataManager reads each CSV file. If a file does "
         "not exist yet, an empty DataFrame with the correct column schema "
         "is created in memory and the file is written on the first save."),
        ("How are IDs generated?",
         "IDs use a prefix (CMP, DON, INV, CH, SUR) followed by a random "
         "5-digit number (10000–99999). This gives a very low collision "
         "probability for typical fund-raising volumes."),
        ("How do campaign statuses change?",
         "A campaign starts as 'Active' when created from a survey. Once "
         "the total raised amount meets or exceeds the target, the status "
         "is automatically set to 'Completed'."),
    ]

    def __init__(self, dm, admin_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.admin_user = admin_user
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(HeaderLabel(
            "Frequently Asked Questions",
            "Common admin questions about the system",
            accent=C.WARNING,
        ))

        for question, answer in self._FAQ:
            card = GlowCard(accent=C.WARNING)
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(20, 16, 20, 16)
            card_lay.setSpacing(10)

            q_lbl = QLabel(f"❓  {question}")
            q_lbl.setStyleSheet(
                f"font-size:{F.SIZE_LG};font-weight:700;color:{C.PRIMARY};"
                f"background:transparent;")
            q_lbl.setWordWrap(True)
            card_lay.addWidget(q_lbl)

            a_lbl = QLabel(answer)
            a_lbl.setStyleSheet(
                f"font-size:{F.SIZE_MD};color:{C.TEXT_SECONDARY};"
                f"background:transparent;line-height:1.5;")
            a_lbl.setWordWrap(True)
            card_lay.addWidget(a_lbl)

            root.addWidget(card)

        root.addStretch()
        outer.addWidget(_scrollable(container))

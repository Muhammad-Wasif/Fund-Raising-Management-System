"""
Funder role pages:
  FunderDashboardPage, BrowseCampaignsPage, MakeDonationPage,
  TrackDonationsPage, ViewMyInvoicesPage, FunderFAQPage
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QScrollArea,
    QSizePolicy, QFrame, QComboBox, QDoubleSpinBox, QProgressBar,
    QDialog, QDialogButtonBox, QGridLayout,
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


def _scrollable(inner: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidget(inner)
    sa.setWidgetResizable(True)
    sa.setStyleSheet("QScrollArea{background:transparent;border:none;}")
    return sa


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:{F.SIZE_LG};font-weight:700;color:{C.TEXT_PRIMARY};"
        f"background:transparent;")
    return lbl


# ═══════════════════════════════════════════════════════════════
#  1.  FUNDER DASHBOARD
# ═══════════════════════════════════════════════════════════════
class FunderDashboardPage(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, dm, funder_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.funder_user = funder_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        self.header = HeaderLabel(
            f"Welcome, {self.funder_user}  💰",
            "Funder Dashboard  •  Browse campaigns & track your impact",
            accent=C.PRIMARY,
        )
        root.addWidget(self.header)

        # Stat cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_count = StatCard("🎯", "0", "My Donations", C.PRIMARY)
        self.card_total = StatCard("💵", "$0", "Total Donated", C.SUCCESS)
        self.card_active = StatCard("🚀", "0", "Active Campaigns", C.INFO)

        for c in (self.card_count, self.card_total, self.card_active):
            cards_row.addWidget(c)
        root.addLayout(cards_row)

        root.addWidget(Separator())

        actions_lbl = QLabel("⚡  Quick Actions")
        actions_lbl.setStyleSheet(
            f"font-size:{F.SIZE_LG};font-weight:700;color:{C.TEXT_PRIMARY};"
            f"background:transparent;")
        root.addWidget(actions_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        self.btn_browse  = _quick_btn("Browse Campaigns", "🔍")
        self.btn_donate  = _quick_btn("Make Donation", "💳")
        self.btn_track   = _quick_btn("Track Donations", "📊")
        self.btn_invoices = _quick_btn("My Invoices", "🧾")
        self.btn_faq     = _quick_btn("FAQ", "❓")

        self.btn_browse.clicked.connect(lambda: self.navigate.emit("browse_campaigns"))
        self.btn_donate.clicked.connect(lambda: self.navigate.emit("make_donation"))
        self.btn_track.clicked.connect(lambda: self.navigate.emit("track_donations"))
        self.btn_invoices.clicked.connect(lambda: self.navigate.emit("my_invoices"))
        self.btn_faq.clicked.connect(lambda: self.navigate.emit("funder_faq"))

        for b in (self.btn_browse, self.btn_donate, self.btn_track,
                  self.btn_invoices, self.btn_faq):
            btn_row.addWidget(b)
        root.addLayout(btn_row)
        root.addStretch()

    def refresh_data(self):
        my = self.dm.get_user_donations(self.funder_user)
        self.card_count.set_value(str(len(my)))
        total = float(my["amount"].sum()) if not my.empty else 0
        self.card_total.set_value(f"${total:,.0f}")
        active = self.dm.get_active_campaigns()
        self.card_active.set_value(str(len(active)))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  2.  BROWSE CAMPAIGNS
# ═══════════════════════════════════════════════════════════════
class BrowseCampaignsPage(QWidget):
    def __init__(self, dm, funder_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.funder_user = funder_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        top = QHBoxLayout()
        top.addWidget(HeaderLabel(
            "Browse Campaigns",
            "View all fund-raising campaigns and their progress",
            accent=C.PRIMARY,
        ))
        top.addStretch()
        self.btn_refresh = AnimatedButton(
            "🔄  Refresh", color=C.BG_ELEVATED, hover_color=C.BORDER_LIGHT,
            text_color=C.TEXT_PRIMARY, min_height=40)
        self.btn_refresh.clicked.connect(self.refresh_data)
        top.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addLayout(top)

        self.table = _make_table([
            "ID", "Project Name", "Region", "Type", "Target",
            "Raised", "Remaining", "Progress", "Status",
        ])
        root.addWidget(self.table, 1)

    def refresh_data(self):
        df = self.dm.get_all_campaigns()
        self.table.setRowCount(0)
        if df.empty:
            return
        for _, r in df.iterrows():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, _item(str(r.get("id", ""))))
            self.table.setItem(row, 1, _item(str(r.get("project_name", ""))))
            self.table.setItem(row, 2, _item(str(r.get("region", ""))))
            self.table.setItem(row, 3, _item(str(r.get("type", ""))))

            target = float(r.get("target", 0))
            raised = float(r.get("raised", 0))
            remaining = max(target - raised, 0)

            self.table.setItem(row, 4, _item(f"${target:,.0f}"))
            self.table.setItem(row, 5, _item(f"${raised:,.0f}"))
            self.table.setItem(row, 6, _item(f"${remaining:,.0f}"))

            # Progress bar cell
            pct = int((raised / target * 100) if target > 0 else 0)
            pbar = QProgressBar()
            pbar.setRange(0, 100)
            pbar.setValue(min(pct, 100))
            pbar.setFormat(f"{pct}%")
            pbar.setFixedHeight(18)
            self.table.setCellWidget(row, 7, pbar)

            status = str(r.get("status", ""))
            color = C.SUCCESS if status == "Completed" else C.PRIMARY
            self.table.setItem(row, 8, _colored_item(status, color))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  3.  MAKE DONATION  –  the complex multi-step page
# ═══════════════════════════════════════════════════════════════
class MakeDonationPage(QWidget):
    """Multi-step donation form with validation and receipt dialog."""

    def __init__(self, dm, funder_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.funder_user = funder_user
        self._selected_campaign_id = None
        self._build_ui()

    # ── Build ───────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(HeaderLabel(
            "Make a Donation",
            "Select a campaign, verify identity, and donate",
            accent=C.SUCCESS,
        ))

        # ────── Step 1: Campaign selection ──────
        root.addWidget(_section_label("Step 1 — Select Campaign"))

        self.campaign_table = _make_table([
            "ID", "Project Name", "Region", "Target", "Raised", "Remaining",
        ])
        self.campaign_table.setMaximumHeight(200)
        self.campaign_table.cellClicked.connect(self._on_campaign_click)
        root.addWidget(self.campaign_table)

        self.camp_sel_label = QLabel("No campaign selected")
        self.camp_sel_label.setStyleSheet(
            f"color:{C.TEXT_SECONDARY};font-size:{F.SIZE_SM};background:transparent;")
        root.addWidget(self.camp_sel_label)

        root.addWidget(Separator())

        # ────── Step 2: Amount ──────
        root.addWidget(_section_label("Step 2 — Donation Amount"))

        amt_row = QHBoxLayout()
        amt_row.setSpacing(12)

        amt_lbl = QLabel("Amount ($):")
        amt_lbl.setStyleSheet(
            f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
        amt_row.addWidget(amt_lbl)

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(1.00, 99_999_999.00)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(100.00)
        self.amount_spin.setPrefix("$ ")
        self.amount_spin.setMinimumHeight(44)
        self.amount_spin.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        amt_row.addWidget(self.amount_spin, 1)

        self.remaining_label = QLabel("")
        self.remaining_label.setStyleSheet(
            f"color:{C.TEXT_SECONDARY};font-size:{F.SIZE_SM};background:transparent;")
        amt_row.addWidget(self.remaining_label)
        root.addLayout(amt_row)

        root.addWidget(Separator())

        # ────── Step 3: Identity verification ──────
        root.addWidget(_section_label("Step 3 — Identity Verification"))

        id_row = QHBoxLayout()
        id_row.setSpacing(12)

        id_lbl = QLabel("Username:")
        id_lbl.setStyleSheet(
            f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
        id_row.addWidget(id_lbl)
        self.verify_user = AnimatedLineEdit("Re-enter your username")
        self.verify_user.setMinimumHeight(44)
        id_row.addWidget(self.verify_user, 1)

        pw_lbl = QLabel("Password:")
        pw_lbl.setStyleSheet(
            f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
        id_row.addWidget(pw_lbl)
        self.verify_pass = AnimatedLineEdit("Re-enter your password", is_password=True)
        self.verify_pass.setMinimumHeight(44)
        id_row.addWidget(self.verify_pass, 1)
        root.addLayout(id_row)

        root.addWidget(Separator())

        # ────── Step 4: CNIC ──────
        root.addWidget(_section_label("Step 4 — CNIC Verification"))

        cnic_row = QHBoxLayout()
        cnic_row.setSpacing(12)
        cnic_lbl = QLabel("CNIC (13 digits):")
        cnic_lbl.setStyleSheet(
            f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
        cnic_row.addWidget(cnic_lbl)

        self.cnic_input = AnimatedLineEdit("e.g. 3520112345678")
        self.cnic_input.setMinimumHeight(44)
        self.cnic_input.setMaxLength(13)
        cnic_row.addWidget(self.cnic_input, 1)
        root.addLayout(cnic_row)

        root.addWidget(Separator())

        # ────── Step 5: Payment method ──────
        root.addWidget(_section_label("Step 5 — Payment Method"))

        pay_row = QHBoxLayout()
        pay_row.setSpacing(12)

        method_lbl = QLabel("Method:")
        method_lbl.setStyleSheet(
            f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
        pay_row.addWidget(method_lbl)

        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Mobile Payment", "Bank Transfer", "Cheque Payment",
        ])
        self.method_combo.setMinimumHeight(44)
        self.method_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.method_combo.currentIndexChanged.connect(self._on_method_change)
        pay_row.addWidget(self.method_combo, 1)
        root.addLayout(pay_row)

        # Dynamic fields container
        self.dyn_widget = QWidget()
        self.dyn_layout = QHBoxLayout(self.dyn_widget)
        self.dyn_layout.setContentsMargins(0, 0, 0, 0)
        self.dyn_layout.setSpacing(12)
        root.addWidget(self.dyn_widget)

        # Pre-create dynamic inputs
        self.mobile_input = AnimatedLineEdit("11-digit phone number")
        self.mobile_input.setMaxLength(11)
        self.mobile_input.setMinimumHeight(44)

        self.bank_name_input = AnimatedLineEdit("Bank name")
        self.bank_name_input.setMinimumHeight(44)
        self.bank_last4_input = AnimatedLineEdit("Last 4 digits")
        self.bank_last4_input.setMaxLength(4)
        self.bank_last4_input.setMinimumHeight(44)

        self.cheque_bank_input = AnimatedLineEdit("Bank name")
        self.cheque_bank_input.setMinimumHeight(44)
        self.cheque_num_input = AnimatedLineEdit("Cheque number")
        self.cheque_num_input.setMinimumHeight(44)

        self._on_method_change(0)

        root.addWidget(Separator())

        # ────── Step 6: Confirm ──────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_confirm = GlowButton("💳  Confirm Donation")
        self.btn_confirm.setMinimumWidth(260)
        self.btn_confirm.clicked.connect(self._confirm_donation)
        btn_row.addWidget(self.btn_confirm)
        btn_row.addStretch()
        root.addLayout(btn_row)

        root.addStretch()
        outer.addWidget(_scrollable(container))

    # ── Dynamic payment fields ──────────────────────────
    def _clear_dynamic(self):
        while self.dyn_layout.count():
            child = self.dyn_layout.takeAt(0)
            w = child.widget()
            if w:
                w.setParent(None)

    def _on_method_change(self, idx):
        self._clear_dynamic()
        method = self.method_combo.currentText()
        if method == "Mobile Payment":
            lbl = QLabel("Phone:")
            lbl.setStyleSheet(
                f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
            self.dyn_layout.addWidget(lbl)
            self.dyn_layout.addWidget(self.mobile_input, 1)
        elif method == "Bank Transfer":
            lbl1 = QLabel("Bank:")
            lbl1.setStyleSheet(
                f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
            self.dyn_layout.addWidget(lbl1)
            self.dyn_layout.addWidget(self.bank_name_input, 1)
            lbl2 = QLabel("Last 4:")
            lbl2.setStyleSheet(
                f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
            self.dyn_layout.addWidget(lbl2)
            self.dyn_layout.addWidget(self.bank_last4_input)
        elif method == "Cheque Payment":
            lbl1 = QLabel("Bank:")
            lbl1.setStyleSheet(
                f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
            self.dyn_layout.addWidget(lbl1)
            self.dyn_layout.addWidget(self.cheque_bank_input, 1)
            lbl2 = QLabel("Cheque #:")
            lbl2.setStyleSheet(
                f"color:{C.TEXT_PRIMARY};font-weight:600;background:transparent;")
            self.dyn_layout.addWidget(lbl2)
            self.dyn_layout.addWidget(self.cheque_num_input, 1)

    # ── Campaign selection ──────────────────────────────
    def _on_campaign_click(self, row, _col):
        id_item = self.campaign_table.item(row, 0)
        if not id_item:
            return
        self._selected_campaign_id = id_item.text()
        name = self.campaign_table.item(row, 1).text()
        remaining_txt = self.campaign_table.item(row, 5).text()
        self.camp_sel_label.setText(
            f"✅  Selected: {name}  ({self._selected_campaign_id})")
        self.camp_sel_label.setStyleSheet(
            f"color:{C.SUCCESS};font-size:{F.SIZE_SM};background:transparent;")
        self.remaining_label.setText(f"Remaining needed: {remaining_txt}")

    # ── Validation & donation ───────────────────────────
    def _confirm_donation(self):
        # 1 — Campaign
        if not self._selected_campaign_id:
            Toast("⚠️  Select a campaign first", self, bg=C.WARNING).show_toast()
            return

        # 2 — Amount
        amount = self.amount_spin.value()
        if amount <= 0:
            Toast("⚠️  Amount must be > $0", self, bg=C.WARNING).show_toast()
            return

        # 3 — Identity
        uname = self.verify_user.text().strip()
        pwd   = self.verify_pass.text().strip()
        if not uname or not pwd:
            Toast("⚠️  Enter username and password", self, bg=C.WARNING).show_toast()
            return
        if uname != self.funder_user:
            Toast("❌  Username doesn't match your session", self, bg=C.DANGER).show_toast()
            return
        if not self.dm.authenticate("funder", uname, pwd):
            Toast("❌  Authentication failed", self, bg=C.DANGER).show_toast()
            return

        # 4 — CNIC
        cnic = self.cnic_input.text().strip()
        valid, msg = self.dm.validate_cnic(cnic, self.funder_user)
        if not valid:
            Toast(f"❌  {msg}", self, bg=C.DANGER).show_toast()
            return

        # 5 — Payment detail string
        method = self.method_combo.currentText()
        detail = ""
        if method == "Mobile Payment":
            phone = self.mobile_input.text().strip()
            if not phone.isdigit() or len(phone) != 11:
                Toast("⚠️  Phone must be 11 digits", self, bg=C.WARNING).show_toast()
                return
            detail = f"Mobile Payment - {phone}"
        elif method == "Bank Transfer":
            bank = self.bank_name_input.text().strip()
            last4 = self.bank_last4_input.text().strip()
            if not bank:
                Toast("⚠️  Enter bank name", self, bg=C.WARNING).show_toast()
                return
            if not last4.isdigit() or len(last4) != 4:
                Toast("⚠️  Enter last 4 digits", self, bg=C.WARNING).show_toast()
                return
            detail = f"Bank Transfer - {bank} (****{last4})"
        elif method == "Cheque Payment":
            bank = self.cheque_bank_input.text().strip()
            cheque_no = self.cheque_num_input.text().strip()
            if not bank:
                Toast("⚠️  Enter bank name", self, bg=C.WARNING).show_toast()
                return
            if not cheque_no:
                Toast("⚠️  Enter cheque number", self, bg=C.WARNING).show_toast()
                return
            detail = f"Cheque Payment - {bank} #{cheque_no}"

        # 6 — Process
        success, info, excess = self.dm.make_donation(
            self._selected_campaign_id, cnic, self.funder_user, amount, detail)

        if not success:
            Toast("❌  Donation failed — campaign not found", self, bg=C.DANGER).show_toast()
            return

        # Show receipt
        self._show_receipt(info, excess)

        # Reset form
        self._reset_form()
        self.refresh_data()

    def _reset_form(self):
        self._selected_campaign_id = None
        self.camp_sel_label.setText("No campaign selected")
        self.camp_sel_label.setStyleSheet(
            f"color:{C.TEXT_SECONDARY};font-size:{F.SIZE_SM};background:transparent;")
        self.remaining_label.setText("")
        self.amount_spin.setValue(100.00)
        self.verify_user.clear()
        self.verify_pass.clear()
        self.cnic_input.clear()
        self.mobile_input.clear()
        self.bank_name_input.clear()
        self.bank_last4_input.clear()
        self.cheque_bank_input.clear()
        self.cheque_num_input.clear()
        self.method_combo.setCurrentIndex(0)

    # ── Receipt dialog ──────────────────────────────────
    def _show_receipt(self, info: dict, excess: float):
        dlg = QDialog(self)
        dlg.setWindowTitle("Donation Receipt")
        dlg.setMinimumWidth(460)
        dlg.setStyleSheet(f"""
            QDialog {{
                background-color: {C.BG_CARD};
                border: 1px solid {C.BORDER};
                border-radius: 14px;
            }}
        """)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(14)

        title = QLabel("✅  Donation Successful!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size:{F.SIZE_XL};font-weight:700;color:{C.SUCCESS};"
            f"background:transparent;")
        lay.addWidget(title)

        lay.addWidget(Separator())

        # Receipt grid
        grid = QGridLayout()
        grid.setSpacing(8)

        fields = [
            ("Donation ID", info.get("donation_id", "")),
            ("Invoice ID", info.get("invoice_id", "")),
            ("Challan #", info.get("challan_id", "")),
            ("Campaign", info.get("campaign_name", "")),
            ("Campaign ID", info.get("campaign_id", "")),
            ("Amount", f"${info.get('amount', 0):,.2f}"),
            ("Payment", info.get("payment_method", "")),
            ("Date", info.get("date", "")),
        ]

        for i, (label, value) in enumerate(fields):
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(
                f"color:{C.TEXT_SECONDARY};font-weight:600;"
                f"font-size:{F.SIZE_MD};background:transparent;")
            val = QLabel(str(value))
            val.setStyleSheet(
                f"color:{C.TEXT_PRIMARY};font-size:{F.SIZE_MD};"
                f"background:transparent;")
            val.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)

        lay.addLayout(grid)

        if excess > 0:
            ex_lbl = QLabel(
                f"⚠️  Excess amount: ${excess:,.2f} — Campaign was fully funded. "
                f"Only the required amount was accepted.")
            ex_lbl.setWordWrap(True)
            ex_lbl.setStyleSheet(
                f"color:{C.WARNING};font-size:{F.SIZE_SM};background:transparent;"
                f"padding:8px;border:1px solid {C.WARNING};border-radius:8px;")
            lay.addWidget(ex_lbl)

        if info.get("fully_funded"):
            ff_lbl = QLabel("🎉  This campaign is now fully funded!")
            ff_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ff_lbl.setStyleSheet(
                f"color:{C.SUCCESS};font-size:{F.SIZE_MD};font-weight:700;"
                f"background:transparent;")
            lay.addWidget(ff_lbl)

        lay.addWidget(Separator())

        close_btn = GlowButton("Close")
        close_btn.clicked.connect(dlg.accept)
        lay.addWidget(close_btn)

        dlg.exec()

    # ── Data ────────────────────────────────────────────
    def refresh_data(self):
        df = self.dm.get_active_campaigns()
        self.campaign_table.setRowCount(0)
        if df.empty:
            return
        for _, r in df.iterrows():
            row = self.campaign_table.rowCount()
            self.campaign_table.insertRow(row)
            self.campaign_table.setItem(row, 0, _item(str(r.get("id", ""))))
            self.campaign_table.setItem(row, 1, _item(str(r.get("project_name", ""))))
            self.campaign_table.setItem(row, 2, _item(str(r.get("region", ""))))

            target = float(r.get("target", 0))
            raised = float(r.get("raised", 0))
            remaining = max(target - raised, 0)

            self.campaign_table.setItem(row, 3, _item(f"${target:,.0f}"))
            self.campaign_table.setItem(row, 4, _item(f"${raised:,.0f}"))
            self.campaign_table.setItem(row, 5, _item(f"${remaining:,.0f}"))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  4.  TRACK DONATIONS
# ═══════════════════════════════════════════════════════════════
class TrackDonationsPage(QWidget):
    def __init__(self, dm, funder_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.funder_user = funder_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "Track Donations",
            "History of your contributions",
            accent=C.PRIMARY,
        ))

        self.table = _make_table([
            "Donation ID", "Campaign", "Amount", "Date",
            "Payment Method", "Progress %", "Status",
        ])
        root.addWidget(self.table, 1)

        self.total_card = StatCard("💰", "$0", "Total Donated", C.SUCCESS)
        root.addWidget(self.total_card)

    def refresh_data(self):
        df = self.dm.get_user_donations(self.funder_user)
        self.table.setRowCount(0)
        total = 0.0
        if df.empty:
            self.total_card.set_value("$0")
            return

        all_camps = self.dm.get_all_campaigns()

        for _, r in df.iterrows():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, _item(str(r.get("donation_id", ""))))

            cid = r.get("campaign_id", "")
            cname = self.dm.get_campaign_name(cid)
            self.table.setItem(row, 1, _item(cname))

            amt = float(r.get("amount", 0))
            total += amt
            self.table.setItem(row, 2, _item(f"${amt:,.2f}"))
            self.table.setItem(row, 3, _item(str(r.get("date", ""))))
            self.table.setItem(row, 4, _item(str(r.get("payment_method", ""))))

            # Campaign progress
            pct_str = "N/A"
            status = "Unknown"
            if not all_camps.empty:
                camp_row = all_camps[all_camps["id"] == cid]
                if not camp_row.empty:
                    cr = camp_row.iloc[0]
                    t = float(cr.get("target", 1))
                    raised_val = float(cr.get("raised", 0))
                    pct = int(raised_val / t * 100) if t > 0 else 0
                    pct_str = f"{min(pct, 100)}%"
                    status = str(cr.get("status", "Active"))

            self.table.setItem(row, 5, _item(pct_str))
            color = C.SUCCESS if status == "Completed" else C.PRIMARY
            self.table.setItem(row, 6, _colored_item(status, color))

        self.total_card.set_value(f"${total:,.2f}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()


# ═══════════════════════════════════════════════════════════════
#  5.  VIEW MY INVOICES
# ═══════════════════════════════════════════════════════════════
class ViewMyInvoicesPage(QWidget):
    def __init__(self, dm, funder_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.funder_user = funder_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "My Invoices",
            "Invoice records for your donations",
            accent=C.SECONDARY,
        ))

        self.table = _make_table([
            "Invoice ID", "Challan #", "Campaign", "Amount",
            "Payment Method", "Date",
        ])
        root.addWidget(self.table, 1)

    def refresh_data(self):
        df = self.dm.get_user_donations(self.funder_user)
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
#  6.  FUNDER FAQ
# ═══════════════════════════════════════════════════════════════
class FunderFAQPage(QWidget):
    _FAQ = [
        ("How do I make a donation?",
         "Navigate to 'Make Donation', select an active campaign from the "
         "table, enter the amount, verify your identity by re-entering your "
         "username and password, provide your 13-digit CNIC, choose a payment "
         "method, and click Confirm. A receipt will be shown on success."),
        ("What payment methods are supported?",
         "Three methods are available:\n"
         "• Mobile Payment — requires an 11-digit phone number.\n"
         "• Bank Transfer — requires the bank name and last 4 digits of your account.\n"
         "• Cheque Payment — requires the bank name and cheque number."),
        ("How can I track my donations?",
         "Go to 'Track Donations' to see every donation you've made, including "
         "the campaign progress percentage and whether the campaign has been "
         "completed. Your total donated amount is shown at the bottom."),
        ("What happens after a campaign is fully funded?",
         "Once total donations reach or exceed the campaign's target, the "
         "campaign status changes to 'Completed'. If your donation causes an "
         "excess, only the needed amount is accepted and the excess is returned "
         "or noted in your receipt."),
    ]

    def __init__(self, dm, funder_user: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.funder_user = funder_user
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
            "Common questions about donating",
            accent=C.PRIMARY,
        ))

        for question, answer in self._FAQ:
            card = GlowCard(accent=C.PRIMARY)
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

"""
Analyst role pages:
  AnalystDashboardPage, TopFundersPage, FinancialStatsPage,
  RegionalAnalysisPage, DataVisualizationPage, AnalystFAQPage
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSizePolicy,
    QFrame, QProgressBar, QComboBox, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor, QFont, QColor

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.theme import Colors, Fonts
from ui.components import (
    AnimatedButton, GlowButton, SidebarButton, StatCard,
    GlowCard, HeaderLabel, AnimatedLineEdit, Toast, Separator,
)

C = Colors
F = Fonts


# ═══════════════════════════════════════════════════════════
#  HELPER: dark-themed matplotlib figure
# ═══════════════════════════════════════════════════════════
def _make_dark_figure(width=7, height=4.5, dpi=100):
    """Return a Figure pre-configured for the dark theme."""
    fig = Figure(figsize=(width, height), dpi=dpi, facecolor=C.BG_DARK)
    ax = fig.add_subplot(111)
    ax.set_facecolor("#0e0e22")
    ax.tick_params(colors=C.TEXT_SECONDARY, labelsize=9)
    ax.xaxis.label.set_color(C.TEXT_PRIMARY)
    ax.yaxis.label.set_color(C.TEXT_PRIMARY)
    ax.title.set_color(C.TEXT_PRIMARY)
    for spine in ax.spines.values():
        spine.set_color(C.BORDER)
    return fig, ax


def _style_table(table: QTableWidget):
    """Apply common tweaks to a QTableWidget."""
    table.setAlternatingRowColors(False)
    table.setShowGrid(False)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


def _centered_item(text, color=C.TEXT_PRIMARY, bold=False):
    """Return a center-aligned QTableWidgetItem."""
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setForeground(QColor(color))
    if bold:
        f = QFont()
        f.setBold(True)
        item.setFont(f)
    return item


def _money(val):
    """Format a number as $X,XXX.XX."""
    try:
        return f"${float(val):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


# ═══════════════════════════════════════════════════════════
#  1. ANALYST DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════
class AnalystDashboardPage(QWidget):
    """Welcome dashboard with 4 high-level stat cards."""

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._build_ui()
        self.refresh_data()

    # ── UI ──
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        root.addWidget(HeaderLabel(
            "📊  Analyst Dashboard",
            "Real-time overview of fundraising performance",
            accent=C.INFO,
        ))

        # Welcome card
        welcome = GlowCard(accent=C.INFO)
        wl = QVBoxLayout(welcome)
        wl.setContentsMargins(22, 18, 22, 18)
        wl.setSpacing(6)
        wt = QLabel("Welcome, Data Analyst!")
        wt.setStyleSheet(
            f"font-size: {F.SIZE_XL}; font-weight: 700; color: {C.TEXT_PRIMARY}; background: transparent;")
        ws = QLabel("Dive into campaigns, donations, and regional insights from the sidebar.")
        ws.setStyleSheet(f"font-size: {F.SIZE_SM}; color: {C.TEXT_SECONDARY}; background: transparent;")
        ws.setWordWrap(True)
        wl.addWidget(wt)
        wl.addWidget(ws)
        root.addWidget(welcome)

        # Stat cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self.card_campaigns = StatCard("📋", "0", "Total Campaigns", C.INFO)
        self.card_donations = StatCard("💵", "$0", "Total Donations", C.PRIMARY)
        self.card_funders = StatCard("👥", "0", "Total Funders", C.SECONDARY)
        self.card_avg = StatCard("📈", "$0", "Avg Donation", C.WARNING)

        for card in (self.card_campaigns, self.card_donations, self.card_funders, self.card_avg):
            cards_row.addWidget(card)
        root.addLayout(cards_row)

        root.addStretch()

    # ── Data ──
    def refresh_data(self):
        stats = self.dm.get_financial_stats()
        self.card_campaigns.set_value(str(stats.get("total_campaigns", 0)))
        self.card_donations.set_value(_money(stats.get("total_raised", 0)))
        # Funders = unique funder_user count
        donations = self.dm.get_all_donations()
        funder_count = donations["funder_user"].nunique() if not donations.empty else 0
        self.card_funders.set_value(str(funder_count))
        self.card_avg.set_value(_money(stats.get("avg_donation", 0)))


# ═══════════════════════════════════════════════════════════
#  2. TOP FUNDERS PAGE
# ═══════════════════════════════════════════════════════════
class TopFundersPage(QWidget):
    """Leaderboard of the highest-contributing funders."""

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(HeaderLabel(
            "🏆  Top Funders",
            "Leaderboard of the most generous contributors",
            accent=C.WARNING,
        ))

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Rank", "CNIC", "Username", "Total Donated", "# Donations", "Badge"])
        _style_table(self.table)
        root.addWidget(self.table, 1)

        # Summary row
        self.summary_lbl = QLabel("")
        self.summary_lbl.setStyleSheet(
            f"color: {C.TEXT_SECONDARY}; font-size: {F.SIZE_SM}; padding: 6px; background: transparent;")
        root.addWidget(self.summary_lbl)

    def refresh_data(self):
        df = self.dm.get_top_funders(top_n=15)
        self.table.setRowCount(0)

        if df.empty:
            self.summary_lbl.setText("No funder data available yet.")
            return

        self.table.setRowCount(len(df))
        grand_total = 0.0

        for i, (_, row) in enumerate(df.iterrows()):
            rank = i + 1
            donated = float(row.get("total_donated", 0))
            grand_total += donated

            # Badge
            if rank == 1:
                badge = "🏆"
            elif rank <= 3:
                badge = "⭐"
            else:
                badge = ""

            self.table.setItem(i, 0, _centered_item(str(rank), C.PRIMARY, bold=True))
            self.table.setItem(i, 1, _centered_item(str(row.get("cnic", ""))))
            self.table.setItem(i, 2, _centered_item(str(row.get("username", "")), C.TEXT_PRIMARY))
            self.table.setItem(i, 3, _centered_item(_money(donated), C.PRIMARY))
            self.table.setItem(i, 4, _centered_item(str(int(row.get("num_donations", 0)))))
            self.table.setItem(i, 5, _centered_item(badge))

        self.summary_lbl.setText(
            f"Total funders shown: {len(df)}   |   Grand total donated: {_money(grand_total)}"
        )


# ═══════════════════════════════════════════════════════════
#  3. FINANCIAL STATS PAGE
# ═══════════════════════════════════════════════════════════
class FinancialStatsPage(QWidget):
    """Detailed financial metrics with a raised-vs-target progress bar."""

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        root.addWidget(HeaderLabel(
            "💰  Financial Overview",
            "Key financial metrics across all campaigns",
            accent=C.PRIMARY,
        ))

        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(14)
        self.card_total_camp = StatCard("📋", "0", "Total Campaigns", C.INFO)
        self.card_successful = StatCard("✅", "0", "Successful Campaigns", C.SUCCESS)
        self.card_raised = StatCard("💵", "$0", "Total Raised", C.PRIMARY)
        self.card_target = StatCard("🎯", "$0", "Total Target", C.SECONDARY)
        for c in (self.card_total_camp, self.card_successful, self.card_raised, self.card_target):
            row1.addWidget(c)
        root.addLayout(row1)

        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(14)
        self.card_don_count = StatCard("📊", "0", "Donation Count", C.WARNING)
        self.card_avg_don = StatCard("📈", "$0", "Average Donation", C.INFO)
        row2.addWidget(self.card_don_count)
        row2.addWidget(self.card_avg_don)
        row2.addStretch()
        root.addLayout(row2)

        # Progress card
        progress_card = GlowCard(accent=C.PRIMARY)
        pl = QVBoxLayout(progress_card)
        pl.setContentsMargins(22, 18, 22, 18)
        pl.setSpacing(10)

        pt = QLabel("🎯  Fundraising Progress  (Raised / Target)")
        pt.setStyleSheet(f"font-size: {F.SIZE_LG}; font-weight: 600; color: {C.TEXT_PRIMARY}; background: transparent;")
        pl.addWidget(pt)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(22)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {C.BG_ELEVATED};
                border: none;
                border-radius: 11px;
                text-align: center;
                color: {C.TEXT_PRIMARY};
                font-size: {F.SIZE_SM};
                font-weight: bold;
                min-height: 22px;
                max-height: 22px;
            }}
            QProgressBar::chunk {{
                background: {C.GRAD_PRIMARY};
                border-radius: 11px;
            }}
        """)
        pl.addWidget(self.progress_bar)

        self.progress_detail = QLabel("")
        self.progress_detail.setStyleSheet(
            f"color: {C.TEXT_SECONDARY}; font-size: {F.SIZE_SM}; background: transparent;")
        pl.addWidget(self.progress_detail)

        root.addWidget(progress_card)
        root.addStretch()

    def refresh_data(self):
        stats = self.dm.get_financial_stats()
        self.card_total_camp.set_value(str(stats.get("total_campaigns", 0)))
        self.card_successful.set_value(str(stats.get("successful", 0)))
        self.card_raised.set_value(_money(stats.get("total_raised", 0)))
        self.card_target.set_value(_money(stats.get("total_target", 0)))
        self.card_don_count.set_value(str(stats.get("total_donations", 0)))
        self.card_avg_don.set_value(_money(stats.get("avg_donation", 0)))

        raised = stats.get("total_raised", 0)
        target = stats.get("total_target", 0)
        pct = int((raised / target * 100) if target > 0 else 0)
        pct = min(pct, 100)
        self.progress_bar.setValue(pct)
        self.progress_detail.setText(
            f"{_money(raised)} raised of {_money(target)} target  ({pct}%)"
        )


# ═══════════════════════════════════════════════════════════
#  4. REGIONAL ANALYSIS PAGE
# ═══════════════════════════════════════════════════════════
class RegionalAnalysisPage(QWidget):
    """Regional breakdown of campaign activity."""

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(HeaderLabel(
            "🗺️  Regional Analysis",
            "Campaign distribution and performance by region",
            accent=C.SECONDARY,
        ))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Region", "Campaigns", "Total Raised", "Total Target"])
        _style_table(self.table)
        root.addWidget(self.table, 1)

        self.info_lbl = QLabel("")
        self.info_lbl.setStyleSheet(
            f"color: {C.TEXT_SECONDARY}; font-size: {F.SIZE_SM}; padding: 4px; background: transparent;")
        root.addWidget(self.info_lbl)

    def refresh_data(self):
        df = self.dm.get_regional_data()
        self.table.setRowCount(0)

        if df.empty:
            self.info_lbl.setText("No regional data available yet.")
            return

        self.table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            self.table.setItem(i, 0, _centered_item(str(row["Region"]), C.TEXT_PRIMARY, bold=True))
            self.table.setItem(i, 1, _centered_item(str(int(row["Campaigns"]))))
            self.table.setItem(i, 2, _centered_item(_money(row["Total Raised"]), C.PRIMARY))
            self.table.setItem(i, 3, _centered_item(_money(row["Total Target"]), C.SECONDARY))

        self.info_lbl.setText(f"Showing {len(df)} region(s)")


# ═══════════════════════════════════════════════════════════
#  5. DATA VISUALIZATION PAGE  (embedded Matplotlib)
# ═══════════════════════════════════════════════════════════
class DataVisualizationPage(QWidget):
    """Interactive chart viewer with 4 visualizations embedded in-page."""

    CHART_CAMPAIGN_PROGRESS = 0
    CHART_REGIONAL_DIST = 1
    CHART_TOP_FUNDERS = 2
    CHART_PAYMENT_METHODS = 3

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._build_ui()
        self._draw_current_chart()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(HeaderLabel(
            "📈  Data Visualization",
            "Interactive charts for campaign and donation analytics",
            accent=C.PRIMARY,
        ))

        # Controls row
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)

        selector_label = QLabel("Select Chart:")
        selector_label.setStyleSheet(
            f"color: {C.TEXT_SECONDARY}; font-size: {F.SIZE_MD}; background: transparent;")
        ctrl.addWidget(selector_label)

        self.chart_combo = QComboBox()
        self.chart_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chart_combo.addItems([
            "📊 Campaign Progress",
            "🗺️ Regional Distribution",
            "🏆 Top Funders",
            "💳 Payment Methods",
        ])
        self.chart_combo.setMinimumWidth(220)
        self.chart_combo.currentIndexChanged.connect(self._draw_current_chart)
        ctrl.addWidget(self.chart_combo)

        ctrl.addStretch()

        self.btn_refresh = AnimatedButton("🔄  Refresh", color=C.INFO, text_color="#fff", min_height=38)
        self.btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_refresh.clicked.connect(self._draw_current_chart)
        ctrl.addWidget(self.btn_refresh)
        root.addLayout(ctrl)

        # Canvas area
        self.canvas_container = QVBoxLayout()
        self.canvas_container.setContentsMargins(0, 0, 0, 0)
        self._current_canvas = None
        root.addLayout(self.canvas_container, 1)

    # ── Chart drawing ──
    def _draw_current_chart(self):
        idx = self.chart_combo.currentIndex()
        # Remove old canvas
        if self._current_canvas is not None:
            self.canvas_container.removeWidget(self._current_canvas)
            self._current_canvas.setParent(None)
            self._current_canvas.deleteLater()
            self._current_canvas = None

        fig, ax = _make_dark_figure(width=9, height=5)

        if idx == self.CHART_CAMPAIGN_PROGRESS:
            self._chart_campaign_progress(fig, ax)
        elif idx == self.CHART_REGIONAL_DIST:
            self._chart_regional_distribution(fig, ax)
        elif idx == self.CHART_TOP_FUNDERS:
            self._chart_top_funders(fig, ax)
        elif idx == self.CHART_PAYMENT_METHODS:
            self._chart_payment_methods(fig, ax)

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas_container.addWidget(canvas)
        self._current_canvas = canvas
        canvas.draw()

    def _chart_campaign_progress(self, fig, ax):
        """Bar chart: target vs raised for each campaign."""
        camps = self.dm.get_all_campaigns()
        if camps.empty:
            ax.text(0.5, 0.5, "No campaign data", ha="center", va="center",
                    color=C.TEXT_SECONDARY, fontsize=14, transform=ax.transAxes)
            ax.set_title("Campaign Progress", fontsize=14, pad=12)
            fig.tight_layout()
            return

        names = camps["project_name"].fillna(camps["id"]).tolist()
        targets = camps["target"].astype(float).tolist()
        raised = camps["raised"].astype(float).tolist()

        # Limit to latest 12 for readability
        if len(names) > 12:
            names = names[-12:]
            targets = targets[-12:]
            raised = raised[-12:]

        import numpy as np
        x = np.arange(len(names))
        w = 0.35

        bars1 = ax.bar(x - w / 2, targets, w, label="Target", color=C.SECONDARY, alpha=0.85)
        bars2 = ax.bar(x + w / 2, raised, w, label="Raised", color=C.PRIMARY, alpha=0.85)

        ax.set_xticks(x)
        short_names = [n[:14] + "…" if len(str(n)) > 14 else str(n) for n in names]
        ax.set_xticklabels(short_names, rotation=35, ha="right", fontsize=8, color=C.TEXT_SECONDARY)
        ax.set_ylabel("Amount ($)", fontsize=10)
        ax.set_title("Campaign Progress: Target vs Raised", fontsize=14, pad=12)
        ax.legend(facecolor=C.BG_CARD, edgecolor=C.BORDER, labelcolor=C.TEXT_PRIMARY, fontsize=9)
        fig.tight_layout()

    def _chart_regional_distribution(self, fig, ax):
        """Pie chart: raised amount by region."""
        df = self.dm.get_regional_data()
        if df.empty:
            ax.text(0.5, 0.5, "No regional data", ha="center", va="center",
                    color=C.TEXT_SECONDARY, fontsize=14, transform=ax.transAxes)
            ax.set_title("Regional Distribution", fontsize=14, pad=12)
            fig.tight_layout()
            return

        labels = df["Region"].tolist()
        values = df["Total Raised"].astype(float).tolist()
        palette = ["#00d4aa", "#7c3aed", "#3b82f6", "#f59e0b", "#ef4444",
                    "#10b981", "#8b5cf6", "#06b6d4", "#f97316", "#ec4899"]
        colors = [palette[i % len(palette)] for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            colors=colors, textprops={"color": C.TEXT_PRIMARY, "fontsize": 9},
            startangle=140, pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color("#ffffff")
        ax.set_title("Funds Raised by Region", fontsize=14, pad=12)
        fig.tight_layout()

    def _chart_top_funders(self, fig, ax):
        """Horizontal bar chart: top funders by total donated."""
        df = self.dm.get_top_funders(top_n=10)
        if df.empty:
            ax.text(0.5, 0.5, "No funder data", ha="center", va="center",
                    color=C.TEXT_SECONDARY, fontsize=14, transform=ax.transAxes)
            ax.set_title("Top Funders", fontsize=14, pad=12)
            fig.tight_layout()
            return

        names = df["username"].fillna(df["cnic"]).tolist()[::-1]
        amounts = df["total_donated"].astype(float).tolist()[::-1]

        import numpy as np
        y = np.arange(len(names))
        gradient_colors = [C.PRIMARY if i >= len(names) - 3 else C.INFO for i in range(len(names))]

        ax.barh(y, amounts, color=gradient_colors, height=0.6, alpha=0.85)
        ax.set_yticks(y)
        ax.set_yticklabels([str(n)[:18] for n in names], fontsize=9, color=C.TEXT_SECONDARY)
        ax.set_xlabel("Total Donated ($)", fontsize=10)
        ax.set_title("Top Funders by Donation Amount", fontsize=14, pad=12)
        fig.tight_layout()

    def _chart_payment_methods(self, fig, ax):
        """Pie chart: donation counts by payment method."""
        dist = self.dm.get_payment_method_distribution()
        if dist.empty:
            ax.text(0.5, 0.5, "No payment data", ha="center", va="center",
                    color=C.TEXT_SECONDARY, fontsize=14, transform=ax.transAxes)
            ax.set_title("Payment Methods", fontsize=14, pad=12)
            fig.tight_layout()
            return

        labels = dist.index.tolist()
        values = dist.values.tolist()
        palette = ["#00d4aa", "#7c3aed", "#3b82f6", "#f59e0b", "#ef4444",
                    "#10b981", "#8b5cf6", "#06b6d4"]
        colors = [palette[i % len(palette)] for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            colors=colors, textprops={"color": C.TEXT_PRIMARY, "fontsize": 9},
            startangle=140, pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color("#ffffff")
        ax.set_title("Donations by Payment Method", fontsize=14, pad=12)
        fig.tight_layout()

    def refresh_data(self):
        self._draw_current_chart()


# ═══════════════════════════════════════════════════════════
#  6. ANALYST FAQ PAGE
# ═══════════════════════════════════════════════════════════
class AnalystFAQPage(QWidget):
    """Frequently asked questions for the analyst role."""

    def __init__(self, dm, parent=None):
        super().__init__(parent)
        self.dm = dm
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addWidget(HeaderLabel(
            "❓  Frequently Asked Questions",
            "Common questions about the analyst dashboard",
            accent=C.INFO,
        ))

        faqs = [
            (
                "Where does the data come from?",
                "All data is sourced from the system's CSV-based database. Campaign, "
                "donation, funder, and survey records are loaded automatically on startup "
                "and refreshed whenever you navigate between pages. The data reflects "
                "real-time changes made by admins, funders, and survey takers."
            ),
            (
                "How is the Top Funders ranking calculated?",
                "Funders are ranked by their cumulative donation amount across all campaigns. "
                "The system groups donations by CNIC, sums the amounts, and sorts in descending "
                "order. The 🏆 trophy is awarded to the #1 funder, while ⭐ stars mark ranks 2 and 3."
            ),
            (
                "What visualizations are available?",
                "The Data Visualization page offers four chart types:\n"
                "• Campaign Progress – grouped bar chart comparing target vs raised for each campaign.\n"
                "• Regional Distribution – pie chart showing how raised funds are spread across regions.\n"
                "• Top Funders – horizontal bar chart of the highest donors.\n"
                "• Payment Methods – pie chart of donation counts by payment method.\n\n"
                "All charts are embedded directly in the application using Matplotlib and can be "
                "refreshed on demand."
            ),
        ]

        for question, answer in faqs:
            card = GlowCard(accent=C.INFO)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(22, 18, 22, 18)
            cl.setSpacing(8)

            q_lbl = QLabel(f"Q:  {question}")
            q_lbl.setStyleSheet(
                f"font-size: {F.SIZE_LG}; font-weight: 700; color: {C.PRIMARY}; background: transparent;")
            q_lbl.setWordWrap(True)
            cl.addWidget(q_lbl)

            a_lbl = QLabel(f"A:  {answer}")
            a_lbl.setStyleSheet(
                f"font-size: {F.SIZE_MD}; color: {C.TEXT_SECONDARY}; background: transparent; line-height: 1.5;")
            a_lbl.setWordWrap(True)
            cl.addWidget(a_lbl)

            root.addWidget(card)

        root.addStretch()

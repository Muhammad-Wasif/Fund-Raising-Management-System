"""
Main application window: sidebar navigation + stacked page content.
Created after successful login. Shows different page sets per role.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsOpacityEffect, QSizePolicy, QScrollArea,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal,
)
from PyQt6.QtGui import QCursor, QColor

from ui.theme import Colors, Fonts, ROLE_META
from ui.components import (
    SidebarButton, FadeStackedWidget, Separator, AnimatedButton, Toast,
)

C = Colors
F = Fonts


class MainWindow(QWidget):
    """Main dashboard window with sidebar + page content."""
    logout_requested = pyqtSignal()

    def __init__(self, dm, role: str, username: str, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.role = role
        self.username = username
        self._sidebar_buttons = []
        self._pages = []

        self._build_ui()
        self._animate_entrance()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ═══════════ SIDEBAR ═══════════
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            .QFrame {{
                background-color: {C.SIDEBAR_BG};
                border-right: 1px solid {C.BORDER};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # ── Brand header ──
        brand = QFrame()
        brand.setFixedHeight(70)
        brand.setStyleSheet(f"background: transparent; border-bottom: 1px solid {C.BORDER};")
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(16, 0, 16, 0)

        meta = ROLE_META[self.role]
        brand_icon = QLabel(meta['icon'])
        brand_icon.setStyleSheet("font-size: 26px; background: transparent;")
        brand_layout.addWidget(brand_icon)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(0)
        brand_title = QLabel("FRMS")
        brand_title.setStyleSheet(
            f"font-size: {F.SIZE_LG}; font-weight: 700; color: {C.PRIMARY}; background: transparent;"
        )
        brand_text_layout.addWidget(brand_title)

        brand_role = QLabel(meta['label'] + " Module")
        brand_role.setStyleSheet(
            f"font-size: {F.SIZE_XS}; color: {C.TEXT_MUTED}; background: transparent;"
        )
        brand_text_layout.addWidget(brand_role)
        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()

        sidebar_layout.addWidget(brand)

        # ── User info ──
        user_frame = QFrame()
        user_frame.setFixedHeight(52)
        user_frame.setStyleSheet(f"background: transparent; border-bottom: 1px solid {C.BORDER};")
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(16, 0, 16, 0)

        avatar_lbl = QLabel("👤")
        avatar_lbl.setStyleSheet("font-size: 18px; background: transparent;")
        user_layout.addWidget(avatar_lbl)

        username_lbl = QLabel(self.username)
        username_lbl.setStyleSheet(
            f"font-size: {F.SIZE_SM}; font-weight: 600; color: {C.TEXT_PRIMARY}; background: transparent;"
        )
        user_layout.addWidget(username_lbl)
        user_layout.addStretch()

        sidebar_layout.addWidget(user_frame)

        sidebar_layout.addSpacing(8)

        # ── Nav section label ──
        nav_label = QLabel("  NAVIGATION")
        nav_label.setStyleSheet(
            f"font-size: {F.SIZE_XS}; color: {C.TEXT_MUTED}; letter-spacing: 2px; "
            f"padding: 6px 16px; background: transparent;"
        )
        sidebar_layout.addWidget(nav_label)

        # ── Nav buttons (role-dependent) ──
        menu_items = self._get_menu_items()
        for i, (icon, label) in enumerate(menu_items):
            btn = SidebarButton(label, icon_text=icon)
            btn.clicked.connect(lambda checked, idx=i: self._on_nav_click(idx))
            self._sidebar_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # ── Logout button ──
        sidebar_layout.addWidget(Separator())
        logout_btn = SidebarButton("Logout", icon_text="🚪")
        logout_btn.clicked.connect(self._on_logout)
        sidebar_layout.addWidget(logout_btn)
        sidebar_layout.addSpacing(12)

        main_layout.addWidget(sidebar)

        # ═══════════ CONTENT AREA ═══════════
        content_area = QFrame()
        content_area.setStyleSheet(f"background-color: {C.BG_DARK};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Page stack
        self.page_stack = FadeStackedWidget()
        self._build_pages()
        content_layout.addWidget(self.page_stack)

        main_layout.addWidget(content_area)

        # Set first page active
        if self._sidebar_buttons:
            self._on_nav_click(0)

        # Opacity for entrance
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

    def _get_menu_items(self):
        """Return list of (icon, label) tuples for sidebar based on role."""
        if self.role == 'admin':
            return [
                ("📊", "Dashboard"),
                ("📝", "Create Campaign"),
                ("📋", "View Surveys"),
                ("💰", "Donation Report"),
                ("🧾", "View Invoices"),
                ("❓", "FAQs"),
            ]
        elif self.role == 'funder':
            return [
                ("📊", "Dashboard"),
                ("🔍", "Browse Campaigns"),
                ("💳", "Make Donation"),
                ("📈", "Track Donations"),
                ("🧾", "My Invoices"),
                ("❓", "FAQs"),
            ]
        elif self.role == 'analyst':
            return [
                ("📊", "Dashboard"),
                ("🏆", "Top Funders"),
                ("💹", "Financial Stats"),
                ("🗺️", "Regional Analysis"),
                ("📉", "Visualization"),
                ("❓", "FAQs"),
            ]
        elif self.role == 'survey':
            return [
                ("📊", "Dashboard"),
                ("📝", "Fill Survey"),
                ("❓", "FAQs"),
            ]
        return []

    def _build_pages(self):
        """Import and instantiate role-specific page widgets."""
        try:
            if self.role == 'admin':
                from ui.admin_pages import (
                    AdminDashboardPage, CreateCampaignPage, ViewSurveysPage,
                    DonationReportPage, ViewInvoicesPage, AdminFAQPage,
                )
                pages = [
                    AdminDashboardPage(self.dm, self.username),
                    CreateCampaignPage(self.dm, self.username),
                    ViewSurveysPage(self.dm, self.username),
                    DonationReportPage(self.dm, self.username),
                    ViewInvoicesPage(self.dm, self.username),
                    AdminFAQPage(self.dm, self.username),
                ]
            elif self.role == 'funder':
                from ui.funder_pages import (
                    FunderDashboardPage, BrowseCampaignsPage, MakeDonationPage,
                    TrackDonationsPage, ViewMyInvoicesPage, FunderFAQPage,
                )
                pages = [
                    FunderDashboardPage(self.dm, self.username),
                    BrowseCampaignsPage(self.dm, self.username),
                    MakeDonationPage(self.dm, self.username),
                    TrackDonationsPage(self.dm, self.username),
                    ViewMyInvoicesPage(self.dm, self.username),
                    FunderFAQPage(self.dm, self.username),
                ]
            elif self.role == 'analyst':
                from ui.analyst_pages import (
                    AnalystDashboardPage, TopFundersPage, FinancialStatsPage,
                    RegionalAnalysisPage, DataVisualizationPage, AnalystFAQPage,
                )
                pages = [
                    AnalystDashboardPage(self.dm),
                    TopFundersPage(self.dm),
                    FinancialStatsPage(self.dm),
                    RegionalAnalysisPage(self.dm),
                    DataVisualizationPage(self.dm),
                    AnalystFAQPage(self.dm),
                ]
            elif self.role == 'survey':
                from ui.survey_pages import (
                    SurveyDashboardPage, FillSurveyPage, SurveyFAQPage,
                )
                pages = [
                    SurveyDashboardPage(self.dm, self.username),
                    FillSurveyPage(self.dm, self.username),
                    SurveyFAQPage(self.dm, self.username),
                ]
            else:
                pages = []

            self._pages = pages
            for page in pages:
                # Wrap each page in a scroll area
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(page)
                scroll.setStyleSheet(f"""
                    QScrollArea {{
                        background-color: {C.BG_DARK};
                        border: none;
                    }}
                """)
                self.page_stack.addWidget(scroll)
        except ImportError as e:
            # Fallback if pages aren't built yet
            placeholder = QLabel(f"⚠️ Pages not found: {e}")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet(f"color: {C.WARNING}; font-size: {F.SIZE_LG};")
            self.page_stack.addWidget(placeholder)

    def _on_nav_click(self, index: int):
        """Switch to the selected page with fade animation."""
        # Update button states
        for i, btn in enumerate(self._sidebar_buttons):
            btn.set_active(i == index)

        # Refresh data on the target page
        if index < len(self._pages):
            page = self._pages[index]
            if hasattr(page, 'refresh_data'):
                page.refresh_data()

        self.page_stack.fade_to(index)

    def _on_logout(self):
        self.logout_requested.emit()

    def _animate_entrance(self):
        QTimer.singleShot(50, self._run_entrance_anim)

    def _run_entrance_anim(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: self.setGraphicsEffect(None))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

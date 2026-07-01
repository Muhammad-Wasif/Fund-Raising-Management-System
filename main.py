"""
Fund Raising Management System — PyQt6 Desktop Application
Entry point: creates the QApplication, shows login, transitions to dashboard.
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from data_manager import DataManager
from ui.theme import get_main_stylesheet, Colors
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


class AppShell(QMainWindow):
    """
    Top-level shell that manages transitions between
    Login and the role-specific Dashboard.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fund Raising Management System")
        self.setMinimumSize(QSize(1100, 700))
        self.resize(1280, 780)
        self.setStyleSheet(f"background-color: {Colors.BG_DARKEST};")

        # Data layer
        self.dm = DataManager()

        # Central stacked widget: page 0 = login, page 1 = dashboard
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Build login page
        self.login_page = LoginWindow(self.dm)
        self.login_page.login_success.connect(self._on_login_success)
        self.stack.addWidget(self.login_page)

        self.dashboard_page = None

    def _on_login_success(self, role: str, username: str):
        """Transition from login to the role dashboard."""
        # Remove old dashboard if exists
        if self.dashboard_page is not None:
            self.stack.removeWidget(self.dashboard_page)
            self.dashboard_page.deleteLater()
            self.dashboard_page = None

        # Create new dashboard for this role/user
        self.dashboard_page = MainWindow(self.dm, role, username)
        self.dashboard_page.logout_requested.connect(self._on_logout)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.dashboard_page)

    def _on_logout(self):
        """Return to login screen."""
        self.dm.save_data()
        self.login_page.reset()
        self.stack.setCurrentWidget(self.login_page)

        # Clean up dashboard
        if self.dashboard_page is not None:
            self.stack.removeWidget(self.dashboard_page)
            self.dashboard_page.deleteLater()
            self.dashboard_page = None


def main():
    print("Starting main...")
    import sys
    sys.stdout.reconfigure(line_buffering=True)
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print("Setting stylesheet...")
    app.setStyleSheet(get_main_stylesheet())

    # Set global cursor for the application
    print("Setting cursor...")
    app.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))

    print("Initializing AppShell...")
    window = AppShell()
    print("Showing window...")
    window.show()

    print("Entering event loop...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

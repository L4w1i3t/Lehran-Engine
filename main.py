"""
Lehran Engine - Fire Emblem Fan Game Editor
Main application entry point
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Lehran Engine")
    app.setOrganizationName("Lehran Engine")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""
Lehran Engine - Fire Emblem Fan Game Editor
Main application entry point
"""

import sys
import os
import traceback
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from gui.theme_manager import ThemeManager
from gui.settings_manager import SettingsManager


# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Set up logging - console only by default, file only on crash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_crash_log(exctype, value, tb):
    """Create a crash log file and write error details"""
    log_filename = os.path.join(logs_dir, f"lehran_crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Create file handler for crash log
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Add file handler temporarily
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Log crash details
    logger.critical("=" * 80)
    logger.critical("UNHANDLED EXCEPTION - APPLICATION CRASH")
    logger.critical("=" * 80)
    logger.critical(f"Exception Type: {exctype.__name__}")
    logger.critical(f"Exception Value: {value}")
    logger.critical("Traceback:")
    for line in traceback.format_tb(tb):
        logger.critical(line.rstrip())
    logger.critical("=" * 80)
    
    # Remove file handler
    root_logger.removeHandler(file_handler)
    file_handler.close()
    
    return log_filename


def exception_hook(exctype, value, tb):
    """Global exception handler to log crashes"""
    # Create crash log file
    log_filename = create_crash_log(exctype, value, tb)
    
    # Show error dialog
    try:
        error_msg = f"{exctype.__name__}: {value}\n\nA crash log has been saved to:\n{log_filename}"
        QMessageBox.critical(None, "Lehran Engine - Critical Error", error_msg)
    except:
        pass
    
    # Force application exit
    try:
        QApplication.quit()
    except:
        pass
    
    # Exit with error code
    sys.exit(1)


def main():
    # Install global exception handler
    sys.excepthook = exception_hook
    
    logger.info("=" * 80)
    logger.info("LEHRAN ENGINE STARTING")
    logger.info("=" * 80)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    
    try:
        logger.info("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Lehran Engine")
        app.setOrganizationName("Lehran Engine")
        
        logger.info("Initializing theme manager (capturing system theme)...")
        theme_manager = ThemeManager(app)
        
        logger.info("Initializing settings manager...")
        settings_manager = SettingsManager()
        
        logger.info("Applying saved theme...")
        saved_theme = settings_manager.get_theme()
        theme_manager.set_theme(saved_theme)
        logger.info(f"Theme set to: {saved_theme}")
        
        logger.info("Creating MainWindow...")
        window = MainWindow(theme_manager=theme_manager, settings_manager=settings_manager)
        
        logger.info("Showing MainWindow...")
        window.show()
        
        logger.info("Application started successfully")
        logger.info("=" * 80)
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        logger.critical(traceback.format_exc())
        
        # Create crash log for startup errors
        log_filename = create_crash_log(type(e), e, e.__traceback__)
        
        QMessageBox.critical(None, "Startup Error", f"Failed to start Lehran Engine:\n\n{e}\n\nCheck {log_filename} for details")
        sys.exit(1)


if __name__ == "__main__":
    main()

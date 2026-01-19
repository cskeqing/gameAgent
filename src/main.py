import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from loguru import logger

def main():
    # Ensure log dir exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    logger.add("logs/agent.log", rotation="10 MB")
    logger.info("Starting Game Agent...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

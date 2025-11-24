import sys
from PyQt5.QtWidgets import QApplication
from gui import RockInMindGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RockInMindGUI()
    window.show()
    sys.exit(app.exec_())

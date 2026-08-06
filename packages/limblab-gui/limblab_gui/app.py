# pyright: reportOptionalMemberAccess=false
from PyQt6.QtWidgets import  QApplication
from .main import MainWindow

# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
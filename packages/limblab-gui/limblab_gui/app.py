# pyright: reportOptionalMemberAccess=false
from PyQt6.QtWidgets import  QApplication
from main import MainWindow
from limblab import print_hello

  # Call the function from database.py to verify import 
# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
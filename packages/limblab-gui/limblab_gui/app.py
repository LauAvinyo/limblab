# pyright: reportOptionalMemberAccess=false
from PyQt6.QtWidgets import  QApplication
from main import MainWindow

  # Call the function from database.py to verify import 
# Run the application
app = QApplication([])
window = MainWindow()

print("LimbLab GUI is running. Version:", __import__('limblab').__version__)  # Print the version of limblab package
window.show()
app.exec()
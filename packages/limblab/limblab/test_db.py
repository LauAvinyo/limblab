from typing import Callable

from PyQt6.QtCore import Qt
from PIL import Image
import os
import webbrowser
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QLabel, QMainWindow, QStatusBar, QVBoxLayout,
    QPushButton, QWidget, QHBoxLayout, QMessageBox,
    QMenuBar, QMenu, QToolButton, QFileDialog,
    QCheckBox, QInputDialog, QSpinBox,
    QScrollArea, QComboBox, QDialog, QDoubleSpinBox, QGroupBox
)

from limblab.utils import *
from limblab.config import *
from limblab.main import MainWindow
#from limblab.NavigationMixin import NavigationMixin



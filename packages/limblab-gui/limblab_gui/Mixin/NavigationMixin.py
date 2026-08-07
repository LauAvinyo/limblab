# pyright: reportOptionalMemberAccess=false

from typing import Callable

from PyQt6.QtCore import Qt


from utils import *
from config import *


class NavigationMixin:
    # Types
    nav_stack: list
    current_screen: Callable | None
    menuBar: Callable

    # Navigation Methods
    def navigate_to(self, screen_func):
        if self.current_screen is not None:
            self.nav_stack.append(self.current_screen)
        self.current_screen = screen_func
        screen_func()

    def go_back(self):
        if self.nav_stack:
            previous_screen = self.nav_stack.pop()
            self.current_screen = previous_screen
            previous_screen()

    def reset_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setVisible(False)
        old_corner = menu_bar.cornerWidget(Qt.Corner.TopRightCorner)
        menu_bar.setCornerWidget(None)
        if old_corner is not None:
            old_corner.deleteLater()
        menu_bar.clear()
        menu_bar.setStyleSheet("")

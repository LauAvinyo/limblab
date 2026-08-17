# pyright: reportOptionalMemberAccess=false

from typing import Callable

from PyQt6.QtCore import Qt


from utils import *
from config import *
from PyQt6.QtWidgets import QMessageBox

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



    PIPELINE_STEPS = ["Clean", "Surface", "Stage", "Align", "Visualize"]

    STEP_CONTROLLERS = {
    "Clean": lambda self: lambda: self.clean.show(self.current_experiment),
    "Surface": lambda self: lambda: self.surface.show(self.current_experiment),
    "Stage": lambda self: lambda: self.stage.show(self.current_experiment),
    "Align": lambda self: lambda: self.align.show(self.current_experiment),
    "Visualize": lambda self: lambda: self.show_viz(),  # <-- Changed to match others
}

    STEP_DONE_FLAG = {
        "Clean": "clean_done",
        "Surface": "surface_done",
        "Stage": "stage_done",
        "Align": "align_done",
    }

    def _navigate_to_step(self, target_step, current_step):
        steps = self.PIPELINE_STEPS
        target_idx = steps.index(target_step)
        current_idx = steps.index(current_step)

        if target_idx == current_idx:
            return

        if target_idx < current_idx:
            self._navigate_backward_to_step(target_step, target_idx, current_idx)
        else:
            self._navigate_forward_to_step(target_step, target_idx, current_idx)


    def _handle_back(self, step, guard=None):
        """Go back, warning the user first if the current step isn't finished."""
        if guard is not None:
            done, message = guard()
            if not done:
                reply = QMessageBox.question(
                    self, "Step not completed",
                    f"{message}\n\nGo back anyway? Progress on this step will be lost.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

        if step is not None:
            self._reset_workflow_from(step)
        self.go_back()




##################USE HERE TO DELETE FROM DATABASE####################################################
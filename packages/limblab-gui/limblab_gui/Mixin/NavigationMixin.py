# pyright: reportOptionalMemberAccess=false

from typing import Callable

from config import *
from limblab.vizutils import *
from PyQt6.QtCore import Qt
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
    "Clean": lambda self: lambda: self.clean.show(self.experiment),
    "Surface": lambda self: lambda: self.surface.show(self.experiment),
    "Stage": lambda self: lambda: self.stage.show(self.experiment),
    "Align": lambda self: lambda: self.align.show(self.experiment),
    "Visualize": lambda self: lambda: self.show_viz(),  # <-- Changed to match others
}

    STEP_DONE_FLAG = {
        "Clean": "clean_done",
        "Surface": "surface_done",
        "Stage": "stage_done",
        "Align": "align_done",
    }

    def navigate_to_step(self, target_step, current_step):
        steps = self.PIPELINE_STEPS
        target_idx = steps.index(target_step)
        current_idx = steps.index(current_step)

        if target_idx == current_idx:
            return

        if target_idx < current_idx:
            self._navigate_backward_to_step(target_step, target_idx, current_idx)
        else:
            self._navigate_forward_to_step(target_step, target_idx, current_idx)


    def _navigate_backward_to_step(self, target_step, target_idx, current_idx):
        """Jump back to an earlier pipeline step. Anything between the
        target and where we currently are is now stale, so clear those
        steps' 'done' flags."""
        steps = self.PIPELINE_STEPS

        for step in steps[target_idx + 1 : current_idx + 1]:
            flag = self.STEP_DONE_FLAG.get(step)
            if flag is not None:
                self.workflow_state[flag] = False

        screen_func = self.STEP_CONTROLLERS[target_step](self)
        self.navigate_to(screen_func)

    def _navigate_forward_to_step(self, target_step, target_idx, current_idx):
        """Jump ahead to a later pipeline step, but only if every step in
        between has actually been completed."""
        steps = self.PIPELINE_STEPS

        for step in steps[current_idx:target_idx]:
            flag = self.STEP_DONE_FLAG.get(step)
            if flag is not None and not self.workflow_state.get(flag):
                QMessageBox.warning(
                    self, "Step not completed",
                    f"Finish '{step}' before moving on to '{target_step}'."
                )
                return

        screen_func = self.STEP_CONTROLLERS[target_step](self)
        self.navigate_to(screen_func)


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

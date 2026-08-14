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

    def _navigate_backward_to_step(self, target_step, target_idx, current_idx):
        steps = self.PIPELINE_STEPS
        affected = [
            s for s in steps[target_idx:current_idx + 1]
            if s in self.STEP_DONE_FLAG and self.workflow_state.get(self.STEP_DONE_FLAG[s])
        ]

        if affected:
            reply = QMessageBox.question(
                self,
                "Reset progress?",
                f"Going back to {target_step} will reset progress on: {', '.join(affected)}.\n"
                "You'll need to redo these steps. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            for s in affected:
                self.workflow_state[self.STEP_DONE_FLAG[s]] = False
            if target_step == "Clean":
                self.workflow_state["last_cleaned_channel"] = None
            if target_step in ("Clean", "Surface"):
                self.workflow_state["selected_stage"] = None
            if target_step in ("Clean", "Surface", "Stage"):
                self.workflow_state["alignment_method"] = None

        self.navigate_to(self.STEP_CONTROLLERS[target_step](self))

    def _navigate_forward_to_step(self, target_step, target_idx, current_idx):
        steps = self.PIPELINE_STEPS
        for s in steps[current_idx:target_idx]:
            flag = self.STEP_DONE_FLAG.get(s)
            if flag and not self.workflow_state.get(flag):
                QMessageBox.warning(
                    self, "Step required",
                    f"Please complete '{s}' before jumping ahead to '{target_step}'.",
                )
                return

        if target_step in ("Surface", "Stage", "Align"):
    # Check if DAPI has been cleaned
            dapi_cleaned = False
            for ch in self.current_experiment.channels or []:
                if ch.channel_name.upper() == "DAPI" and self.workflow_state.get("clean_done"):
                    dapi_cleaned = True
                    break
        
            if not dapi_cleaned:
                QMessageBox.warning(
                self, "DAPI required",
                f"'{target_step}' requires a cleaned DAPI channel (.vti). "
                "Please clean the DAPI channel first.",
            )
                return

        self.navigate_to(self.STEP_CONTROLLERS[target_step](self))


    def _navigate_backward_to_step(self, target_step, target_idx, current_idx):
        steps = self.PIPELINE_STEPS
        affected = [
            s for s in steps[target_idx:current_idx + 1]
            if s in self.STEP_DONE_FLAG and self.workflow_state.get(self.STEP_DONE_FLAG[s])
        ]

        if affected:
            reply = QMessageBox.question(
                self,
                "Reset progress?",
                f"Going back to {target_step} will reset progress on: {', '.join(affected)}.\n"
                "You'll need to redo these steps. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            for s in affected:
                self.workflow_state[self.STEP_DONE_FLAG[s]] = False
            if target_step == "Clean":
                self.workflow_state["last_cleaned_channel"] = None
            if target_step in ("Clean", "Surface"):
                self.workflow_state["selected_stage"] = None
            if target_step in ("Clean", "Surface", "Stage"):
                self.workflow_state["alignment_method"] = None
            if "Align" in affected:
                self.align.source = None
                self.align.surface_path = None

            # The history from BEFORE this reset is no longer valid — later
            # screens in it reflect a pipeline state that just got wiped.
            # Rebuild it as the correct chain leading up to target_step so
            # "Back" walks exp -> Clean -> Surface -> ... instead of into
            # stale, now-invalidated later steps.
            self._jump_to_step(target_step)
            return

        self.navigate_to(self.STEP_CONTROLLERS[target_step](self))


    def _jump_to_step(self, step):
        """Navigate to `step` with a freshly-built nav_stack (exp -> ... -> step),
        replacing whatever history existed before a reset."""
        chain = {
            "Clean":     [self.show_exp],
            "Surface":   [self.show_exp,
                        lambda: self.clean.show(self.current_experiment)],
            "Stage":     [self.show_exp,
                        lambda: self.clean.show(self.current_experiment),
                        lambda: self.surface.show(self.current_experiment)],
            "Align":     [self.show_exp,
                        lambda: self.clean.show(self.current_experiment),
                        lambda: self.surface.show(self.current_experiment),
                        lambda: self.stage.show(self.current_experiment)],
            "Visualize": [self.show_exp,
                        lambda: self.clean.show(self.current_experiment),
                        lambda: self.surface.show(self.current_experiment),
                        lambda: self.stage.show(self.current_experiment),
                        lambda: self.align.show(self.current_experiment)],
        }
        self.nav_stack = chain.get(step, [self.show_exp])
        self.current_screen = self.STEP_CONTROLLERS[step](self)
        self.current_screen()

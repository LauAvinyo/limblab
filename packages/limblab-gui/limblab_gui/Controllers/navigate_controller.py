import webbrowser

from limblab.design import theme
from mixin.NavigationMixin import NavigationMixin
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from utils import create_back_button
from vedo import printc

PIPELINE_STEPS = ["Clean", "Surface", "Stage", "Align", "Visualize"]
PIPELINE_INDEX = {
    "Clean": 0, 
    "Surface": 1, 
    "Stage": 2, 
    "Align": 3, 
    "Visualize": 4
}

class NavigationController:
    def __init__(self, window):
        self.window = window


        self.state__navigate_to = {
            "Clean": self.navigate_to_clean,
            "Surface": lambda: print("TO BE DONE"),
            "Stage": lambda: print("TO BE DONE"), 
            "Align": lambda: print("TO BE DONE"),
            "Visualize": lambda: print("TO BE DONE")
        }

    # Navigation Methods
    def navigate_to(self, screen_func):
        if self.window.current_screen is not None:
            self.window.navigation_stack.append(self.window.current_screen)
        self.window.current_screen = screen_func
        screen_func()

    def go_back(self):
        if self.window.navigation_stack:
            previous_screen = self.window.navigation_stack.pop()
            self.window.current_screen = previous_screen
            previous_screen()


    def navigate_to_clean(self):
        printc("Navigating to CLEAN", c="orange")
        print(self._current_step)
        self.navigate_to(lambda:self.window.clean.show(self.window.current_experiment))


    def _refresh_pipeline_actions(self, current_step=None, to_next = False):
        printc("Refreshing the pipeline!", c="cyan")
        self.window.action_bar.setVisible(True)
        self._current_step = current_step

        last_done = 1
        for i, step in enumerate(PIPELINE_STEPS[:-1]):
            if self.window.workflow_checkpoints[step]:
                last_done = i

        printc(last_done, PIPELINE_STEPS[last_done])
        if to_next:
            last_done += 2

            printc(last_done, PIPELINE_STEPS[last_done])
            
        for idx, step in enumerate(PIPELINE_STEPS):

            printc(f"{step}:{idx}", c="green")

            act = self._step_actions[step]
            # flag = self.window.workflow_checkpoints[step]
            is_done = self.window.workflow_checkpoints[step]
            is_reachable = idx < last_done
            printc(".    ", is_reachable,  c="green")
            printc(".    ", is_done,  c="green")

            is_current = step == current_step
            # Build the emoji prefix
            if is_current:
                prefix = "▶ "  # or "● ", "◉ ", "⚙ ", "→ "
            if is_done:
                prefix = "✓ "
            elif not is_reachable:
                prefix = "🔒︎ "
            else:
                prefix = ""

            act.setText(prefix + step)
            act.setEnabled(is_reachable or is_current)
            act.setChecked(is_current)
 



    def _build_permanent_chrome(self):
        if getattr(self, "_chrome_built", False):
            return
        self._chrome_built = True


        self.window.action_bar = self.window.addToolBar("Pipeline")
        self.window.action_bar.setMovable(False)
        self.window.action_bar.setStyleSheet(f"""
                QToolBar {{ background-color: {theme('palette.background', '#141414')}; border: none; spacing: 4px; padding: 4px; }}
                QToolButton {{ color: {theme('palette.textSecondary', '#A0A0A0')}; padding: 6px 14px; border-radius: 4px; }}
                QToolButton:disabled {{ color: {theme('palette.textDisabled', '#3A3A3A')}; }}
                QToolButton:checked {{ background-color: {theme('palette.panel', '#2A2A2A')}; color: {theme('palette.textPrimary', '#FFFFFF')}; }}
            """)

            # Same back button widget show_exp/show_first_screen use — real QWidget,
            # so addWidget (not addAction).
        self._active_back_guard = None
        self.back_btn = create_back_button(
            lambda: print("U clicked the back button!"))
        self.window.action_bar.addWidget(self.back_btn)
        self.window.action_bar.addSeparator()

        self._step_actions = {}
        for step in PIPELINE_STEPS:
            act = QAction(step, self.window)
            act.setCheckable(True)
            act.triggered.connect(lambda _, step=step: self.state__navigate_to[step]())
            self.window.action_bar.addAction(act)
            self._step_actions[step] = act

        self.window.action_bar.setVisible(False)



    # def _reset_workflow_from(self, step):
    #     """Clear *_done flags for `step` and everything after it, so the
    #         toolbar re-locks those steps until they're redone. Called only after
    #         the user has explicitly confirmed they want to overwrite prior output."""
    #     idx = self.PIPELINE_STEPS.index(step)
    #     for s in self.PIPELINE_STEPS[idx:]:
    #         flag = self.STEP_DONE_FLAG.get(s)
    #         if flag:
    #             self.workflow_state[flag] = False

    #         # fields that ride alongside the *_done flags
    #     if idx <= self.PIPELINE_STEPS.index("Clean"):
    #         self.workflow_state["last_cleaned_channel"] = None
    #     if idx <= self.PIPELINE_STEPS.index("Stage"):
    #         self.workflow_state["selected_stage"] = None
    #     if idx <= self.PIPELINE_STEPS.index("Align"):
    #         self.workflow_state["alignment_method"] = None
    #         self.align.source = None
    #         self.align.surface_path = None

    #     self._refresh_pipeline_actions(current_step=step)
    #     self.log_pipeline(f"Reset workflow state from '{step}' onward — redoing this step.")


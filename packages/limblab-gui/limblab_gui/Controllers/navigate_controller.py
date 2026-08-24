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
    QMessageBox
)
from utils import create_back_button
from vedo import printc

from limblab.database.navigation import delete_from_database_going_back_action


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
            "Surface": self.navigate_to_surface,
            "Stage": self.navigate_to_stage, 
            "Align": self.navigate_to_align,
            "Visualize": self.navigate_to_visualize
        }


    # Navigation Methods
    def navigate_to(self, screen_func):
        if self.window.current_screen is not None:
            self.window.navigation_stack.append(self.window.current_screen)

        self.window.current_screen = screen_func
        screen_func()

    def go_back_using_arrow_btn(self):
        if self.window.navigation_stack:
            previous_screen = self.window.navigation_stack.pop()
            self.window.current_screen = previous_screen
            previous_screen()

    def arrow_click_on_viz(self):#potser es molt cutre
        self.navigate_to(self.window.show_user_experiment_list)


    def limb_action_clicked(self, step):
        current_action_idx = PIPELINE_INDEX[step]

        if self.window.workflow_checkpoints[step] == True:  #shouldnt be clickable anyway but just to make sure
            affected = [s for s in PIPELINE_STEPS[current_action_idx:] if self.window.workflow_checkpoints.get(s)]
            #actions affected until the action we're in"!
            
            reply = QMessageBox.question(
                self.window,
                "Reset pipeline?",
                f"Going back to '{step}' will erase progress for: {', '.join(affected)}.\n"
                "This will delete their generated files. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:#the user doesnt want to go back!
                return 

            for s in affected:
                self.window.workflow_checkpoints[s] = False #not done anymore
                self._refresh_pipeline_actions(current_step=step)
                self.state__navigate_to[step]()#the user goes back to that window!
                
            
            channel, channel_cleared, experiment_cleared = delete_from_database_going_back_action(
                db_path=self.window.db_path,
                experiment=self.window.current_experiment,
                channel_name=self.window.current_channel_name,
                action_undone=affected,
            )

            self.window.log_pipeline(
                f'Deleted database information:\n'
                f'from {channel} channel: {channel_cleared}\n'
                f'from experiment: {experiment_cleared}'
            )
            
            #databse fcuntion called!

        else: #the step hasnt been done before!
            self.state__navigate_to[step]()


    def navigate_to_clean(self):
        printc("Navigating to CLEAN", c="orange")
        print(self._current_step)
        self.navigate_to(lambda:self.window.clean.show(self.window.current_experiment))


    def navigate_to_surface(self):
        printc("Navigating to SURFACE", c="orange")
        print(self._current_step)
        self.navigate_to(lambda:self.window.surface.show(self.window.current_experiment))


    def navigate_to_stage(self):
        printc("Navigating to STAGE", c="orange")
        print(self._current_step)
        self.navigate_to(lambda:self.window.stage.show(self.window.current_experiment))


    def navigate_to_align(self):
        printc("Navigating to ALIGN", c="orange")
        print(self._current_step)
        self.navigate_to(lambda:self.window.align.show(self.window.current_experiment))


    def navigate_to_visualize(self):
        printc("Navigating to VISUALIZE", c="orange")
        print(self._current_step)
        self.navigate_to(lambda:self.window.visualizer.show_experiment(self.window.current_experiment))


    def _refresh_pipeline_actions(self, current_step=None, to_next = None):#to_next = False
        printc("Refreshing the pipeline!", c="cyan")
        self.window.action_bar.setVisible(True)
        self._current_step = current_step

        # -1 means nothing has been done yet.
        last_done = -1
        for i, step in enumerate(PIPELINE_STEPS):
            print(i)
            print(step)
            if self.window.workflow_checkpoints[step]:
                last_done = i
 
        for idx, step in enumerate(PIPELINE_STEPS):
 
            act = self._step_actions[step]
            is_done = self.window.workflow_checkpoints[step]
 
            # A step is reachable if it's already done (idx <= last_done),
            # or it's the very next step after the furthest done one
            # (idx == last_done + 1). Nothing further ahead is reachable.
            is_reachable = idx <= last_done + 1
            is_current = step == current_step
            # Build the emoji prefix
            if is_current:
                prefix = "▶  "  # or "● ", "◉ ", "⚙ ", "→ "
            elif is_done:
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
        self.back_btn = create_back_button(self.arrow_click_on_viz)
        self.window.action_bar.addWidget(self.back_btn)
        self.window.action_bar.addSeparator()

        self._step_actions = {}
        for step in PIPELINE_STEPS:
            act = QAction(step, self.window)
            act.setCheckable(True)
            act.triggered.connect(lambda _, step=step: self.limb_action_clicked(step))#connectes buttons to navigate functions
            self.window.action_bar.addAction(act)
            self._step_actions[step] = act

        self.window.action_bar.setVisible(False)


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

from limblab.database import save_experiment

DATABASE_EXPERIMENT_ACTION = {
    'Clean': ['clean_path', 'clean_isovalue_min', 'clean_isovalue_max'],
    'Surface': ['surface_path', 'surface_isovalue'],
    'Stage': ['stage'],
    'Align': ['transformation_matrix_path', 'linear_transform', 'nonlinear_transform']
}


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
                #TODO: delete database generated arguments from the step theyu wnat to go back! -> hard

                #call delete from database function -> yet to define

            #print(affected)
            print(self.window.current_experiment)
            self.delete_from_database_going_back_action(self.window.current_experiment, action_undone = affected)

        else: #the step hasnt been done before!
            self.state__navigate_to[step]()


    def delete_from_database_going_back_action(self, experiment, action_undone: list):
        printc('here to delete', c='pink')

        channel_name = self.window.current_channel#defined at clean controller! (as clean gets done)
        channel = next(
            (ch for ch in experiment.channels if ch.channel_name == channel_name),
            None,
        )#get channel object that matches with the current channel name
        print(experiment, experiment.channels ,'BEFORE DELETION!')
        for action in action_undone:
            if action == 'Clean':
                if channel is None:
                    printc(f"No channel '{channel_name}' found — nothing to undo.", c='red')
                    continue

                what_to_delete = DATABASE_EXPERIMENT_ACTION[action]  # e.g. ['clean_path', 'isovalue_min', 'isovalue_max']
                print(what_to_delete)

                for field in what_to_delete:
                    if hasattr(channel, field):#if the channel has what to delete argument, we set it to None!
                        setattr(channel, field, None)

                    else:
                        printc(f"Channel has no attribute '{field}'", c='red')

            #for processing actions that are not Clean
            for field in what_to_delete:
                if hasattr(experiment, field):
                    setattr(experiment, field, None)

        print(experiment, experiment.channels ,'AFTER DELETION!')
        save_experiment(self.window.db_path, experiment)



                

        

        
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
        self.navigate_to(lambda:self.window.visualizer.show(self.window.current_experiment))


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

            #printc(f"{step}:{idx}", c="green")

            act = self._step_actions[step]
            # flag = self.window.workflow_checkpoints[step]
            is_done = self.window.workflow_checkpoints[step]
            is_reachable = idx < last_done
            printc(step, idx, last_done, c = 'red')
            printc(".    ", is_reachable,  c="green")
            printc(".    ", is_done,  c="green")

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




    # def go_back_from_chrome(self):
    #     if self.window.navigation_stack:
    #         previous_screen = self.window.navigation_stack.pop()
    #         self.window.current_screen = previous_screen
    #         previous_screen()




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


from limblab import save_experiment, stage_limb_embedded
from limblab.design import theme
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QMessageBox, QWidget
from utils import create_label, create_styled_button

CURRENT_STEP = 'Stage'

class StageController:
    def __init__(self, window):
        self.window = window
        self.experiment = None
        self.plotter = None

    def show(self, experiment):
        self.experiment = experiment

        container = self.window._build_workflow_container(
            next_label="Align",
            experiment = self.experiment,
            #next_callback=self._go_next_from_stage,
            # back_guard=lambda: (
            #     self.window.workflow_state["stage_done"],
            #     "You haven't selected and confirmed a stage yet.",
            # ),
            action_widget=self._build_stage_action_bar(),
        )
        self.window.setCentralWidget(container)

        self.window.navigation._refresh_pipeline_actions(current_step="Stage")

        try:
            self.plotter = stage_limb_embedded(
                experiment=experiment,
                renderer="pyqt",
                outside_class=self.window,
            )
        except ConnectionError as e:
            QMessageBox.critical(self.window, "Staging server error", str(e))
        except ValueError as e:
            QMessageBox.critical(self.window, "Missing data", str(e))


    def _build_stage_action_bar(self):
        bar = QWidget()
        bar.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        #current = self.window.workflow_state.get("selected_stage")
        #label_text = f"Stage: {current}" if current is not None else "Stage: not staged"
        #self.stage_label = create_label(label_text, f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeSmall', 13)}px;")

        stage_btn = create_styled_button("Confirm Stage")
        stage_btn.clicked.connect(self._confirm_stage)

        #layout.addWidget(self.stage_label)
        layout.addStretch()
        layout.addWidget(stage_btn)
        return bar

    def _confirm_stage(self):
        stage = self.plotter.stage_result.get("stage") # type: ignore
        if stage is None:
            QMessageBox.warning(self.window, "Not staged", "Press 's' in the 3D view to stage the limb first.")
            return

    
        stage = int(stage)

        self.experiment.stage = stage
    
        save_experiment(self.window.db_path, self.experiment)#DB!!!!!!!!!!!!!!!!!!!!


        self.window.log_pipeline(f"Stage confirmed: {stage}")
        self.window._refresh_visualizer_list(self.experiment)
        self.window.workflow_checkpoints[CURRENT_STEP] = True
        self.window.navigation._refresh_pipeline_actions(CURRENT_STEP, True)


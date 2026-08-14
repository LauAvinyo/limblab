from limblab import save_experiment, stage_limb_embedded
from limblab.design import theme
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QMessageBox, QWidget
from utils import create_label, create_styled_button


class StageController:
    def __init__(self, window):
        self.window = window
        self.experiment = None
        self.plotter = None

    def show(self, experiment):
        self.experiment = experiment

        container = self.window._build_workflow_container(
            next_label="Align",
            next_callback=self._go_next_from_stage,
            back_guard=lambda: (
                self.window.workflow_state["stage_done"],
                "You haven't selected and confirmed a stage yet.",
            ),
            action_widget=self._build_stage_action_bar(),
        )
        self.window.setCentralWidget(container)

        self.window._refresh_pipeline_actions(current_step="Stage")

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

        current = self.window.workflow_state.get("selected_stage")
        label_text = f"Stage: {current}" if current is not None else "Stage: not staged"
        self.stage_label = create_label(label_text, f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeSmall', 13)}px;")

        stage_btn = create_styled_button("Confirm Stage")
        stage_btn.clicked.connect(self._confirm_stage)

        layout.addWidget(self.stage_label)
        layout.addStretch()
        layout.addWidget(stage_btn)
        return bar

    def _confirm_stage(self):
        if self.plotter is None or not hasattr(self.plotter, "stage_result"):
            QMessageBox.warning(self.window, "Not staged", "Press 's' in the 3D view to stage the limb first.")
            return

        stage = self.plotter.stage_result.get("stage") # type: ignore
        if stage is None:
            QMessageBox.warning(self.window, "Not staged", "Press 's' in the 3D view to stage the limb first.")
            return

        try:
            stage = int(stage)
        except (TypeError, ValueError):
            QMessageBox.critical(self.window, "Staging error", f"Server returned an invalid stage value: {stage!r}")
            return

        assert self.experiment is not None
        self.experiment.stage = stage
    
        save_experiment(self.window.db_path, self.experiment)

        self.window.workflow_state["stage_done"] = True
        self.window.workflow_state["selected_stage"] = stage
        self.stage_label.setText(f"Stage: {stage}")

        self.window._refresh_pipeline_actions(current_step="Stage")

        self.window.log_pipeline(f"Stage confirmed: {stage}")

    def _go_next_from_stage(self):
        if not self.window.workflow_state["stage_done"]:
            QMessageBox.warning(self.window, "Stage required", "Please select and confirm a stage before proceeding to Alignment.")
            return
        self.window.navigate_to(lambda: self.window.align.show(self.window.current_experiment))
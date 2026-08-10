from limblab import _stage_limb, check_connection, stage_limb
from PyQt6.QtWidgets import QHBoxLayout, QMessageBox, QWidget, QComboBox
from utils import create_styled_button, create_label



#######################################################UNFINISHED, NOT LINKED TO ANY stage.py functions!!!
class StageController:
    def __init__(self, window):
        self.window = window
        self.experiment = None

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

        menu_bar = self.window._reset_top_menu_bar()
        self.window._build_file_menu(menu_bar)
        self.window._build_view_menu(menu_bar)

    def _build_stage_action_bar(self):
        bar = QWidget()
        bar.setStyleSheet("background-color: #1E1E1E;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        label = create_label("Stage:", "color: #ffffff; font-size: 13px;")
        stage_combo = QComboBox()
        stage_combo.addItems([
            "Stage 20 - E10.5", "Stage 22 - E11.5",
            "Stage 24 - E12.5", "Stage 26 - E13.5",
        ])
        if self.window.workflow_state.get("selected_stage") in [
            stage_combo.itemText(i) for i in range(stage_combo.count())
        ]:
            stage_combo.setCurrentText(self.window.workflow_state["selected_stage"])

        confirm_btn = create_styled_button("Confirm Stage", "#0D7C66", "#41B3A2")
        confirm_btn.clicked.connect(lambda: self._confirm_stage(stage_combo.currentText()))

        layout.addWidget(label)
        layout.addWidget(stage_combo)
        layout.addStretch()
        layout.addWidget(confirm_btn)
        return bar



    def _confirm_stage(self, stage_text):
        self.window.workflow_state["stage_done"] = True
        self.window.workflow_state["selected_stage"] = stage_text
        self.window.log_pipeline(f"Stage confirmed: {stage_text}")

    def _go_next_from_stage(self):
        if not self.window.workflow_state["stage_done"]:
            QMessageBox.warning(self.window, "Stage required", "Please select and confirm a stage before proceeding to Alignment.")
            return
        self.window.navigate_to(lambda: self.window.align.show(self.window.current_experiment))
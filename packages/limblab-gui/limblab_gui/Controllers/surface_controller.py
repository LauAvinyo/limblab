import os

from limblab import (
    extract_surface,
    get_nuclei_channel_path,
    pick_isovalue,
    save_experiment,
)
from limblab.design import theme
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QWidget,
)
from utils import create_label, create_styled_button


class SurfaceExtractionWorker(QThread):
    finished = pyqtSignal(object)   # Path on success
    failed = pyqtSignal(str)

    def __init__(self, experiment, isovalue):
        super().__init__()
        self.experiment = experiment
        self.isovalue = isovalue

    def run(self):
        try:
            path = extract_surface(experiment=self.experiment, isovalue=self.isovalue)
            self.finished.emit(path)
        except Exception as e:
            self.failed.emit(str(e))



class SurfaceController:
    def __init__(self, window):
        self.window = window
    
        self.plotter = None
        self.isovalue = None
        self.experiment = None


    def show(self, experiment):
        self.experiment = experiment

        """Surface screen. Top bar shows the Stage button (the next step)."""
        container = self.window._build_workflow_container(
            next_label="Stage",
            next_callback=self._go_next_from_surface,
            back_guard=lambda: (
                self.window.workflow_state["surface_done"],
                "You haven't extracted a surface yet.",
            ),
            action_widget=self._build_surface_action_bar(),
        )
        self.window.setCentralWidget(container)

        self.window._refresh_pipeline_actions(current_step="Surface")

        print(experiment.channels)
        dapi_channel = next(
            (ch for ch in experiment.channels if ch.channel_name == "DAPI"),
            None,
        )
        print(dapi_channel)

        if dapi_channel is None:
            QMessageBox.critical(self.window, "Surface extraction error", "No DAPI channel found.")
            return
        if not dapi_channel.path.lower().endswith(".vti"):
            QMessageBox.critical(
                self.window, "Surface extraction error",
                "DAPI channel hasn't been cleaned yet. Clean it first to generate the .vti volume."
            )
            return

        nuclei_path = os.path.join(experiment.base, dapi_channel.path)
        self.plotter = pick_isovalue(
            raw_volume_path=nuclei_path,
            renderer="pyqt",
            outside_class=self.window,
        )

    #from main
    def _build_surface_action_bar(self):
        """Execute Surface Extraction button, shown under the viewer on the Surface screen."""
        bar = QWidget()
        bar.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        info = create_label(
                "Select isovalue for surface extraction\nRemember that Surface Extraction is performed on clean DAPI channels",
                f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeBase', 14)}px; font-style: italic;",
            )
        execute_btn = create_styled_button("Execute Surface Extraction")
        execute_btn.clicked.connect(self._execute_surface)

        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(execute_btn)
        return bar

    #from main
    def _execute_surface(self):

        self.window._show_busy('Extracting surface with the selected isovalue...')

        if self.plotter is None:
            QMessageBox.critical(self.window, "Surface extraction error", "No isosurface preview available.")
            self.window._hide_busy()
            return
            #isovalue gets extracted from the vedo renderer se4lected value (slider)
           
        isovalue = float(self.plotter.sliders[0][0].value) # type: ignore
        self._worker = SurfaceExtractionWorker(self.experiment, isovalue)
        self._worker.finished.connect(lambda path: self._on_extraction_done(path, isovalue))
        self._worker.failed.connect(lambda msg: QMessageBox.critical(self.window, "Surface extraction error", msg))
        self._worker.start()


        self.window._hide_busy()


    def _on_extraction_done(self, surface_path, isovalue):
        assert self.experiment is not None
        self.experiment.surface_path = os.path.basename(str(surface_path))
        self.experiment.surface_isovalue = int(isovalue)
        save_experiment(self.window.db_path, self.experiment)

        self.window.workflow_state["surface_done"] = True
        self.window._refresh_pipeline_actions(current_step="Surface")

        self.window.log_pipeline(f"Surface extracted (isovalue={isovalue:.3f}).\nWritten to:\n{surface_path}")
        print('!!!')

        self._go_next_from_surface()


    #from main
    def _go_next_from_surface(self):
        print('!!!!')
        print(self.experiment.surface_path)
        """Guard for Surface -> Stage: must have extracted a surface."""
        if self.experiment.surface_path is None and self.experiment.surface_isovalue is None:

            QMessageBox.warning(
                self.window,
                "Surface required",
                "Please extract a surface before proceeding to Stage.",
            )
            return
        else:
            self.window._show_message("Surface Extraction was performed!\nYou can now stage your limb volume")
            self.window.navigate_to(lambda: self.window.stage.show(self.window.current_experiment))
from limblab import extract_surface, pick_isovalue, get_nuclei_channel_path

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QWidget,
)
from utils import create_styled_button, create_label

from PyQt6.QtCore import QThread, pyqtSignal



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

        menu_bar = self.window._reset_top_menu_bar()
        self.window._build_file_menu(menu_bar)
        self.window._build_view_menu(menu_bar)

        nuclei_path = get_nuclei_channel_path(experiment)
        print("DEBUG raw_volume_path:", nuclei_path, "exists:", nuclei_path.is_file())
        self.plotter = pick_isovalue(
            raw_volume_path=nuclei_path,
            renderer="pyqt",
            outside_class=self.window,
        )

        #interactive plotter through surface.py pick_isovalue function!
        self.plotter = pick_isovalue(
            raw_volume_path=nuclei_path,
            renderer="pyqt",
            outside_class=self.window,
        )


    #from main
    def _build_surface_action_bar(self):
            """Execute Surface Extraction button, shown under the viewer on the Surface screen."""
            bar = QWidget()
            bar.setStyleSheet("background-color: #1E1E1E;")
            layout = QHBoxLayout(bar)
            layout.setContentsMargins(20, 10, 20, 10)

            info = create_label(
                "Select isovalue for surface extraction\nRemember that Surface Extraction is performed on clean DAPI channels",
                "color: #A0A0A0; font-size: 14px; font-style: italic;",
            )
            execute_btn = create_styled_button(
                "Execute Surface Extraction", "#0D7C66", "#41B3A2"
            )
            execute_btn.clicked.connect(self._execute_surface)

            layout.addWidget(info)
            layout.addStretch()
            layout.addWidget(execute_btn)
            return bar

    #from main
    def _execute_surface(self):
        if self.plotter is None:
            QMessageBox.critical(self.window, "Surface extraction error", "No isosurface preview available.")
            return

            #isovalue gets extracted from the vedo renderer se4lected value (slider)
           
        isovalue = float(self.plotter.sliders[0][0].value)
        self._worker = SurfaceExtractionWorker(self.experiment, isovalue)
        self._worker.finished.connect(lambda path: self._on_extraction_done(path, isovalue))
        self._worker.failed.connect(lambda msg: QMessageBox.critical(self.window, "Surface extraction error", msg))
        self._worker.start()


    def _on_extraction_done(self, surface_path, isovalue):
        self.window.workflow_state["surface_done"] = True
        self.window.log_pipeline(f"Surface extracted (isovalue={isovalue:.3f}).\nWritten to:\n{surface_path}")

    #from main
    def _go_next_from_surface(self):
            """Guard for Surface -> Stage: must have extracted a surface."""
            if not self.window.workflow_state["surface_done"]:
                QMessageBox.warning(
                    self,
                    "Surface required",
                    "Please extract a surface before proceeding to Stage.",
                )
                return
            #plt.close()
            self.window.navigate_to(self.show_stage)
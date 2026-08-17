import os
import sys
from pathlib import Path
from types import SimpleNamespace

import vtkmodules
from PyQt6.QtWidgets import QApplication, QMenuBar
from vedo import Mesh, Plotter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from limblab.models import Channel, Experiment
from main import MainWindow

vtkmodules.qt.QVTKRWIBase = "QGLWidget"

BASE = r'C:\\Users\\millan\\Desktop\\HOXA11'

TEST_SURFACE_PATH = BASE + r'\\HCR11_HOXA11_l2_dapi_488_LH_surface.vtk'
TEST_RAW_TIF = BASE + r'\\HCR11_HOXA11_l1_dapi_488_LH.tif'
TEST_CLEANED_VTI = BASE + r'\\HCR11_HOXA11_l2_dapi_488_LH.vti'
TEST_ROTATION_MAT = BASE + r'\\HCR11_HOXA11_l1_dapi_488_LH_rotation.mat'


class VizTest(MainWindow):
    def __init__(self):
        super().__init__()

        self.current_experiment = Experiment(
            experiment_id="manual_test",
            base=BASE,
            spacing_x=1.0,
            spacing_y=1.0,
            spacing_z=1.0,
            side="F",
            position="L",
            species="mouse",
            surface_path=TEST_SURFACE_PATH,
            surface_isovalue=165,
            stage=260,
            channels=[
                Channel(
                    experiment_id="manual_test",
                    channel_name="DAPI",
                    path=TEST_RAW_TIF,
                    clean_isovalue_min=0,
                    clean_isovalue_max=54,
                    clean_path=TEST_CLEANED_VTI,
                ),
            ],
        )

        self.show_viz_test_menu()

    def show_viz_test_menu(self):
        """Test-only entry point: build the viz container, but let us
        pick which preview mode to render via a menu instead of relying
        on real workflow_state / align / clean pipeline state."""
        container = self._build_workflow_container(
            next_label="Clean",
            next_callback=lambda: self.navigate_to(lambda: self.clean.show(self.current_experiment)),
            back_guard=None,
            current_step="Visualize",
        )
        self.setCentralWidget(container)
        self._refresh_pipeline_actions(current_step="Visualize")

        menubar = self.menuBar()
        viz_menu = menubar.addMenu("Test Viz Mode")

        viz_menu.addAction("Raw volume preview", self._test_raw_preview)
        viz_menu.addAction("Cleaned channel preview", self._test_cleaned_preview)
        viz_menu.addAction("Final aligned mesh", self._test_aligned_mesh)

        # default to raw on load
        self._test_raw_preview()


    def _test_raw_preview(self):
        self._show_raw_volume_preview(self.current_experiment)

    def _test_cleaned_preview(self):
        # Fake the workflow_state a real "Clean" step would have set
        self.workflow_state["clean_done"] = True
        self.workflow_state["last_cleaned_channel"] = "DAPI"
        # _show_cleaned_channel_preview reads channel.path — point it at
        # the cleaned file for this test rather than the raw tif
        self.current_experiment.channels[0].path = TEST_CLEANED_VTI
        self._show_cleaned_channel_preview()

    def _test_aligned_mesh(self):
        # Fake the align controller's expected attributes
        self.align.surface_path = TEST_SURFACE_PATH
        self.align.source = SimpleNamespace(transform=None)  # replace None with a real vtkTransform if you have one
        self.workflow_state["align_done"] = True
        self._show_final_aligned_mesh()


app = QApplication(sys.argv)
window = VizTest()
window.show()
sys.exit(app.exec())
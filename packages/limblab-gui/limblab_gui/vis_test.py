import os
import sys
from pathlib import Path
from types import SimpleNamespace

import vtkmodules
from PyQt6.QtWidgets import QApplication, QMenuBar
from vedo import Mesh, Plotter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt6.QtGui import (
    QAction)
from limblab.models import Channel, Experiment
from main import MainWindow

vtkmodules.qt.QVTKRWIBase = "QGLWidget"


###
#VISUALIZATION IMPORTS
###
from limblab.vis.isosurface import one_channel_isosurface
from limblab.vis.isosurface import two_chanel_isosurface
from limblab.vis.probe import probe
from limblab.vis.raycast import raycast
from limblab.vis.slab import dynamic_slab

from vedo import Volume



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

        # This is the call that creates self.vtk_widget / self.plt —
        # required before any preview method can run.
        container = self._build_workflow_container(
            next_label="Clean",
            next_callback=lambda: self.navigate_to(lambda: self.clean.show(self.current_experiment)),
            back_guard=None,
            current_step="Visualize",
        )
        self.setCentralWidget(container)
        self._refresh_pipeline_actions(current_step="Visualize")

        menubar = self.menuBar()
        view_menu = menubar.addMenu("&View")

        volume_action = QAction('Volume (default)',self)
        volume_action.triggered.connect(lambda checked=False, m='volume': self.click_menu())
        view_menu.addAction(volume_action)

        iso_action = QAction('Isosurfaces', self)
        iso_action.triggered.connect(lambda checked=False, m='isosurfaces': self.click_menu())
        view_menu.addAction(iso_action)

        slices_action = QAction('Slices', self)
        slices_action.triggered.connect(lambda checked=False, m='slices': self.click_menu())
        view_menu.addAction(slices_action)

        ray_action = QAction('Raycast', self)
        ray_action.triggered.connect(lambda checked=False, m='raycast': self.raycast_show())
        view_menu.addAction(ray_action)

        probe_action = QAction('Probe', self)
        probe_action.triggered.connect(lambda checked=False, m='probe': self.click_menu())
        view_menu.addAction(probe_action)

        slab_action = QAction('2D Projection Slab', self)
        slab_action.triggered.connect(lambda checked=False, m='slab': self.click_menu())
        view_menu.addAction(slab_action)

        # default to raw on load
        self._test_raw_preview()

    def _test_raw_preview(self):
        self._show_raw_volume_preview(self.current_experiment)

   

app = QApplication(sys.argv)
window = VizTest()
window.show()
sys.exit(app.exec())
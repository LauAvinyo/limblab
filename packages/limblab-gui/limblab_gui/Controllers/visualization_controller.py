import os

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from vedo import Plotter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from limblab.design import theme
from limblab.vis.isosurface import one_channel_isosurface
from limblab.vis.probe import probe
from limblab.vis.raycast import raycast
from limblab.vis.slab import dynamic_slab
from utils import create_label, create_styled_button


class VisualizationController:

    MODES = {
        "Raycast": "raycast",
        "Isosurface": "isosurface",
        "Slab (2D projection)": "slab",
        "Probe": "probe",
    }

    def __init__(self, window):
        self.window = window
        self.experiment = None
        self.channel_combo = None
        self.mode_combo = None
        self._popups = []  # keep references alive so Qt doesn't GC/close them

    # ------------------------------------------------------------------
    def build_action_bar(self, experiment):
        """Call this from show_viz() and pass the result as `action_widget`
        to `_build_workflow_container`, same as StageController does for
        its Confirm Stage bar."""
        self.experiment = experiment

        bar = QWidget()
        bar.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        layout.addWidget(create_label(
            "Channel:", f"color: {theme('palette.textPrimary', '#FFFFFF')};"
        ))
        self.channel_combo = QComboBox()
        for ch in (experiment.channels or []):
            self.channel_combo.addItem(ch.channel_name)
        layout.addWidget(self.channel_combo)

        layout.addSpacing(12)
        layout.addWidget(create_label(
            "Mode:", f"color: {theme('palette.textPrimary', '#FFFFFF')};"
        ))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(list(self.MODES.keys()))
        layout.addWidget(self.mode_combo)

        show_btn = create_styled_button("Show")
        show_btn.clicked.connect(self._on_show_clicked)
        layout.addWidget(show_btn)

        layout.addStretch()
        return bar

    # ------------------------------------------------------------------
    def show(self,experiment):
        self.experiment = experiment

        container = self.window._build_workflow_container(
                        next_label="Clean",
                        next_callback=self._go_next_from_viz,
                        back_guard=None,
                        current_step="Visualize",
                        action_widget=self.build_action_bar(self.experiment)
                    )

        
        self.window.setCentralWidget(container)
        self.window._refresh_pipeline_actions(current_step="Visualize")
        


    def _on_show_clicked(self):                
        if not self.experiment or not self.experiment.channels:
            QMessageBox.warning(
                self.window, "No channels",
                "This experiment has no channels to visualize."
            )
            return

        channel_name = self.channel_combo.currentText()
        channel = next(
            (ch for ch in self.experiment.channels if ch.channel_name == channel_name),
            None,
        )
        if channel is None:
            QMessageBox.warning(self.window, "Channel not found", f"Couldn't find channel '{channel_name}'.")
            return

        ok, message = self._validate_channel(channel)
        if not ok:
            QMessageBox.warning(self.window, "Not ready for visualization", message)
            return

        mode_label = self.mode_combo.currentText()
        self._open_popup(self.MODES[mode_label], mode_label, channel)

    # ------------------------------------------------------------------
    def _validate_channel(self, channel):
        """Gate visualization on the channel actually being cleaned/processed.
        Same rule for DAPI and gene channels: no clean_path, no viz."""
        is_dapi = channel.channel_name.upper() == "DAPI"
        clean_path = getattr(channel, "clean_path", None)

        if not clean_path:
            if is_dapi:
                return False, (
                    "This DAPI channel hasn't been processed yet.\n"
                    "Run it through Clean before visualizing it."
                )
            return False, (
                f"'{channel.channel_name}' hasn't been cleaned yet.\n"
                "Gene channels must be cleaned before they can be visualized."
            )

        full_path = os.path.join(self.experiment.base, clean_path)
        if not os.path.exists(full_path):
            return False, (
                f"The cleaned file for '{channel.channel_name}' is missing on disk:\n{full_path}"
            )

        return True, ""

    # ------------------------------------------------------------------
    def _open_popup(self, mode, mode_label, channel):
        """Standalone window, its own VTK widget + plotter, dispatch to the
        matching vis function."""
        popup = QDialog(self.window)
        popup.setWindowTitle(f"{mode_label} — {channel.channel_name}")
        popup.resize(900, 700)

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        vtk_widget = QVTKRenderWindowInteractor(frame)
        layout.addWidget(vtk_widget)
 
        plotter = Plotter(qt_widget=vtk_widget)

        try:
            if mode == "raycast":
                raycast(self.experiment, channel_name=channel.channel_name, plotter=plotter)
            elif mode == "isosurface":
                one_channel_isosurface(self.experiment, channel_name=channel.channel_name, plotter=plotter)
            elif mode == "slab":
                dynamic_slab(self.experiment, channel_name=channel.channel_name, plotter=plotter)
            elif mode == "probe":
                probe(self.experiment, channel_name=channel.channel_name, plotter=plotter)
            else:
                QMessageBox.warning(self.window, "Not implemented", f"Mode '{mode_label}' isn't wired up yet.")
                popup.close()
                return
        except Exception as e:
            QMessageBox.critical(
                self.window, "Visualization error",
                f"Failed to render {channel.channel_name}: {e}"
            )
            popup.close()
            return

        # Keep a ref so Qt doesn't garbage-collect the dialog out from under
        # the plotter, and drop it once the user closes the window.
        self._popups.append(popup)
        popup.finished.connect(
            lambda _=None, p=popup: self._popups.remove(p) if p in self._popups else None
        )
        popup.show()


    def _go_next_from_viz(self):
    #the user will always be abele to clean and process any channel from the current experimetn!
            self.window.navigate_to(lambda: self.window.surface.show(self.window.current_experiment))

import os
from pathlib import Path
from typing import Any

from limblab.design import theme
from limblab.models import Channel
from limblab.utils import generate_kwargs
from limblab.vis.isosurface import one_channel_isosurface
from limblab.vis.probe import probe
from limblab.vis.raycast import raycast
from limblab.vis.slab import dynamic_slab
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from utils import create_back_button, create_label, create_styled_button
from vedo import Mesh, Plotter, Volume, printc
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from limblab import preview_volume

CURRENT_STAGE = 'Visualize'

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
        self.status_label = None
        self.show_btn = None

    # ------------------------------------------------------------------
    def build_action_bar(self, experiment):
        """Call this from show_viz() and pass the result as `action_widget`
        to `_build_workflow_container`, same as StageController does for
        its Confirm Stage bar."""
        

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

        layout.addSpacing(12)
        self.status_label = create_label(
            "", f"color: {theme('palette.textSecondary', '#A0A0A0')};"
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label, stretch=1)
 
        layout.addStretch()
 
        # Keep the "Show" button / status text in sync with whichever
        # channel is selected in the dropdown.
        self.channel_combo.currentTextChanged.connect(self._update_channel_status)
 
        # If a channel was picked from the side panel, land on it here too.
        preselected = getattr(self.window, "current_channel", None)
        if preselected is not None:
            idx = self.channel_combo.findText(preselected.channel_name)
            if idx != -1:
                self.channel_combo.setCurrentIndex(idx)
 
        self._update_channel_status(self.channel_combo.currentText())
 
        return bar

    def _update_channel_status(self, channel_name=None):
        """Reflect, right on the action bar, whether the currently selected
        channel is ready to be visualized (processing options enabled) or
        not (options disabled + reason shown)."""
        if not self.experiment or self.status_label is None:
            return
 
        if channel_name is None:
            channel_name = self.channel_combo.currentText() if self.channel_combo else ""
 
        channel = next(
            (ch for ch in (self.experiment.channels or []) if ch.channel_name == channel_name),
            None,
        )
 
        if channel is None:
            self.status_label.setText("")
            if self.mode_combo is not None:
                self.mode_combo.setEnabled(False)
            if self.show_btn is not None:
                self.show_btn.setEnabled(False)
            return
 
        ready, message = self.channel_readiness(self.experiment, channel)
 
        if self.mode_combo is not None:
            self.mode_combo.setEnabled(ready)
        if self.show_btn is not None:
            self.show_btn.setEnabled(ready)
 
        if ready:
            self.status_label.setText(f"✓ '{channel.channel_name}' is ready to visualize.")
            self.status_label.setStyleSheet(f"color: {theme('palette.primary', '#0D7C66')};")
        else:
            self.status_label.setText(message.replace("\n", " "))
            self.status_label.setStyleSheet(f"color: {theme('palette.error', '#A6284F')};")

    # ------------------------------------------------------------------

    def show_experiment(self, experiment):
        self.window.action_bar.setVisible(False)
        self.window._show_busy('Loading volume...')

        self.experiment = experiment#passed from window (self.current_Experiment)

      
        workflow_container = self.window._build_workflow_container(
            next_label="Clean",
            back_guard=None,
            current_step="Visualize",
            action_widget=self.build_action_bar(experiment),
        )

        
        self._current_frame = self.window.frame
        self._current_vtk_widget = self.window.vtkWidget
        self.vtk_widget = self.window.vtkWidget  # kept for the helpers below
        #this is not the same as the vis window vtk widget, is just to go back for visualizer.show vtk widget, where the volumes are shown
        #back to hte selecting which kind of visualization we want of the cleaned channel'!

        self.window.setCentralWidget(None)
        
        self.window.navigation._refresh_pipeline_actions(current_step="Visualize")
        QApplication.processEvents()
        self.window.show()

        self.window.setCentralWidget(workflow_container)

    
        if experiment.surface_path is not None:
            surface_path = os.path.join(experiment.base, experiment.surface_path) #.replace('/','\\')

            mesh = Mesh(surface_path).c(theme("limblab.surface"))

            params: dict[str, Any] = {"bg": theme("palette.background")}
            kwargs = generate_kwargs(params=params, renderer='pyqt', outside_class=self.window)
            plt = Plotter(**kwargs)
            plt.add(mesh)
            plt.show(interactive=False)

            self.window._hide_busy()

        else:
            channel = None
            for c in experiment.channels:
                if c.channel_name == "DAPI":
                    channel : Channel = c
                    break
            if channel is None:
                QMessageBox.warning(
                    self.window, 
                    "There is no nucleous channel!!!",
                    "Think again."
                )
                return

            # Show clean DAPI
            if channel.clean_path is not None: 
    
                params: dict[str, Any] = {"bg": theme("palette.background")}
                kwargs = generate_kwargs(params=params, renderer='pyqt', outside_class=self.window)
                plt = Plotter(**kwargs)
                clean_path = os.path.join(experiment.base, channel.clean_path)
                print(clean_path)
                volume = Volume(clean_path)
                plt += volume
                plt.show(interactive=True)

            # Show unclean DAPI
            else:
                
                volume_path = Path(os.path.join(experiment.base, channel.path))
                preview_volume(volume_path, "pyqt", self.window)


        self.window._hide_busy()
                

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
        printc(ok, message, c='blue')
 
        if not ok:
            QMessageBox.warning(self.window, "Not ready for visualization", message)
            return
 
        mode_label = self.mode_combo.currentText()
        self._open_popup(self.MODES[mode_label], mode_label, channel)


    @staticmethod
    def channel_readiness(experiment, channel):
        """Gate visualization on the channel actually being cleaned/processed.
        Same rule for DAPI and gene channels: no clean_path, no viz.
 
        Shared between the action-bar picker (self._validate_channel) and
        anything outside this controller (e.g. the side-panel channel list)
        that needs to know, for a given channel, whether visualization is
        currently available and why not.
 
        Returns (ready: bool, message: str). ``message`` is a short reason
        when not ready, and an empty string when ready.
        """
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
 
        full_path = os.path.join(experiment.base, clean_path)
        if not os.path.exists(full_path):
            return False, (
                f"The cleaned file {full_path}\n for '{channel.channel_name}' is missing :"
            )
 
        return True, ""
 

    # ------------------------------------------------------------------
    def _open_popup(self, mode, mode_label, channel):
        container = QWidget()
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        top_bar = QWidget()
        top_bar.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        back_btn = create_back_button(self._back_to_picker)
    
        top_layout.addWidget(back_btn)
        top_layout.addWidget(create_label(
            f"{mode_label} — {channel.channel_name}",
            f"color: {theme('palette.textPrimary', '#FFFFFF')};"
        ))
        top_layout.addStretch()
        outer_layout.addWidget(top_bar)


        QApplication.processEvents()   # force layout/geometry + native window creation

        frame = QFrame()
        vtk_widget = QVTKRenderWindowInteractor(frame)
        outer_layout.addWidget(vtk_widget)

        self.window.setCentralWidget(container)
        self.window.show()

        self.vtk_widget = vtk_widget
        self._current_frame = frame

        #try:
        if mode == "raycast":
            rc_plotter = raycast(
                    self.window.current_experiment,
                    channel_name=channel.channel_name,
                    renderer='pyqt',
                    outside_class=self,)
            self._current_plotter = rc_plotter

        elif mode == 'isosurface':
            iso_plotter = one_channel_isosurface(
                    self.window.current_experiment,
                        channel_name=channel.channel_name,
                        renderer='pyqt',
                        outside_class=self,
                        )
            self._current_plotter = iso_plotter

        elif mode == "slab":
            slab_plotter = dynamic_slab(self.window.current_experiment, 
                    channel_name=channel.channel_name,
                    renderer='pyqt',
                    outside_class=self,
                    )
            self._current_plotter = slab_plotter

        elif mode == "probe":
            probe_plotter = probe(self.window.current_experiment,
                    channel_names=[channel.channel_name],
                    renderer='pyqt',
                    outside_class=self,
                    )
            self._current_plotter = probe_plotter

        return


    def _back_to_picker(self):
        """Tear down the current render widget/plotter and return to the
        channel/mode picker."""
        
        plotter = getattr(self, "_current_plotter", None)
        if plotter is not None:
            try:
                plotter.close()
            except Exception:
                pass

        # vtk_widget = getattr(self, "_current_vtk_widget", None)
        # if vtk_widget is not None:
        #     vtk_widget.close()
      
        self._current_plotter = None
        self._current_vtk_widget = None
        self._current_frame = None

        self.show_experiment(self.experiment)

    

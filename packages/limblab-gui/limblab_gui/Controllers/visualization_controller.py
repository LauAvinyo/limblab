import os
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

from controllers.navigate_controller import NavigationController

from pathlib import Path

#from controllers.navigate_controller import navigate_to_clean

CURRENT_STAGE = 'Visualize'

import inspect
from PyQt6.QtWidgets import QCheckBox, QMenu, QToolButton, QWidgetAction

class MultiChannelSelector(QToolButton):
    """Drop-down with one checkbox per ready channel (menu stays open while ticking)."""
    def __init__(self, names, preselected=(), parent=None):
        super().__init__(parent)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._menu = QMenu(self)
        self._boxes = {}
        for name in names:
            box = QCheckBox(name)
            box.setChecked(name in preselected)
            box.setStyleSheet("padding: 4px 10px;")
            box.toggled.connect(self._update_text)
            act = QWidgetAction(self._menu)
            act.setDefaultWidget(box)
            self._menu.addAction(act)
            self._boxes[name] = box
        self.setMenu(self._menu)
        self.setEnabled(bool(names))
        self._update_text()

    def selected(self):
        return [n for n, b in self._boxes.items() if b.isChecked()]

    def _update_text(self, *_):
        sel = self.selected()
        if not self._boxes:
            text = "No channels ready"
        elif not sel:
            text = "Select channels…"
        elif len(sel) <= 2:
            text = ", ".join(sel)
        else:
            text = f"{len(sel)} channels"
        self.setText(text + " ▾")


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
        self.channel_selector = None
        self._selected_names = []
        self.mode_combo = None
        self.status_label = None
        self.show_btn = None
        self.clean_channels = []

    def build_action_bar(self, experiment):
        bar = QWidget()
        bar.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        layout.addWidget(create_label(
            "Channels:", f"color: {theme('palette.textPrimary', '#FFFFFF')};"
        ))
        ready_names = [
            ch.channel_name for ch in experiment.channels
            if self.channel_readiness(experiment, ch)[0]
        ]
        keep = [n for n in self._selected_names if n in ready_names] or ready_names[:1]
        self.channel_selector = MultiChannelSelector(ready_names, preselected=keep)
        layout.addWidget(self.channel_selector)

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

        return bar


    def show_experiment(self, experiment):
        self.experiment = experiment
        self.window.experiment_metadata[experiment.experiment_id] = experiment  # <-- add
        self.window.action_bar.setVisible(False)
        self.window._show_busy('Loading volume...')
      
        workflow_container = self.window._build_workflow_container(
            experiment=self.experiment,
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

        self._channel_actors = {}  # (exp_id, channel_name) -> actor

        if experiment.surface_path is not None:
            surface_path = os.path.join(experiment.base, experiment.surface_path)
            mesh = Mesh(surface_path).c(theme("limblab.surface"))

            params: dict[str, Any] = {"bg": theme("palette.background")}
            kwargs = generate_kwargs(params=params, renderer='pyqt', outside_class=self.window)
            plt = Plotter(**kwargs)
            plt.add(mesh)
            plt.show(interactive=False)

            self.plt = plt
            self._channel_actors[(experiment.experiment_id, "DAPI")] = mesh

        else:
            dapi_channel = next(
                (ch for ch in experiment.channels if ch.channel_name.upper() == "DAPI"),
                None,
            )
            if dapi_channel is None or not getattr(dapi_channel, "path", None):
                QMessageBox.warning(
                    self.window, "DAPI file missing",
                    "No DAPI channel file is recorded for this experiment."
                )
                self.window._hide_busy()
                return

            volume_path = os.path.join(experiment.base, dapi_channel.path)
            vol, plt = preview_volume(volume_path, "pyqt", self.window)
            self.plt = plt
            self._channel_actors[(experiment.experiment_id, "DAPI")] = vol
       
        self.window._hide_busy()       


    def _build_channel_actor(self, channel):
        """Lazily render a gene channel's cleaned volume in the final Visualize view."""
        ready, message = self.channel_readiness(self.experiment, channel)
        if not ready:
            QMessageBox.warning(self.window, "Can't visualize", message)
            return None

        clean_path = os.path.join(self.experiment.base, channel.clean_path)
        vol = Volume(clean_path)
        # placeholder: pick a real per-channel color/rendering mode here
        vol.color(theme("limblab.surface"))
        return vol


    def _on_show_clicked(self):                
        if not self.experiment or not self.experiment.channels:
            QMessageBox.warning(self.window, "No channels",
                                "This experiment has no channels to visualize.")
            return

        names = self.channel_selector.selected()
        if not names:
            QMessageBox.warning(self.window, "No channel selected",
                                "Select at least one channel to visualize.")
            return

        channels = [ch for ch in self.experiment.channels if ch.channel_name in names]
        self._selected_names = names          # survives the action-bar rebuild below

        mode_label = self.mode_combo.currentText()   # capture BEFORE rebuild
        mode = self.MODES[mode_label]

        for ch in channels:
            ready, message = self.channel_readiness(self.experiment, ch)
            if not ready:
                QMessageBox.warning(self.window, "Can't visualize", message)
                return

        self.show_experiment(self.experiment)
        self._open_popup(mode, mode_label, channels)

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
            if is_dapi and not getattr(experiment, "transformation_matrix_path", None):
                return False, (
                "The DAPI channel hasn't been fully processed yet.\n"
                "Finish Clean → Surface → Stage → Align before visualizing it."
            )
 
        full_path = os.path.join(experiment.base, clean_path)
        if not os.path.exists(full_path):
            return False, (
                f"The cleaned file {full_path}\n for '{channel.channel_name}' is missing :"
            )
 
        return True, ""
 
    # ------------------------------------------------------------------
    def _open_popup(self, mode, mode_label, channels):
        names = [c.channel_name for c in channels]

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
            f"{mode_label} — {', '.join(names)}",
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

        fns = {"raycast": raycast, "isosurface": one_channel_isosurface,
               "slab": dynamic_slab, "probe": probe}
        self._current_plotter = self._run_vis(fns[mode], names)
        return


    def _run_vis(self, fn, names):
        """Call a limblab vis function with all channels if it supports it,
        otherwise fall back to the first channel and tell the user."""
        params = inspect.signature(fn).parameters
        common = dict(renderer='pyqt', outside_class=self)
        if "channel_names" in params:
            return fn(self.window.experiment, channel_names=names, **common)
        if len(names) > 1:
            QMessageBox.information(
                self.window, "Single channel only",
                f"This mode only supports one channel at a time. "
                f"Showing '{names[0]}'."
            )
        return fn(self.window.experiment, channel_name=names[0], **common)


    def _back_to_picker(self):
            """Tear down the current render widget/plotter and return to the
            channel/mode picker."""

            plotter = getattr(self, "_current_plotter", None)
            if plotter is not None:
                try:
                    plotter.close()
                except Exception:
                    pass

            self._current_plotter = None
            self._current_vtk_widget = None
            self._current_frame = None

            self.show_experiment(self.experiment)

    

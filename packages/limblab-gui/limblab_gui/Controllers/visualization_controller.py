import os

from pathlib import Path

from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from utils import create_back_button
from vedo import Plotter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from limblab.design import theme
from limblab.vis.isosurface import one_channel_isosurface
from limblab.vis.probe import probe
from limblab.vis.raycast import raycast
from limblab.vis.slab import dynamic_slab
from utils import create_label, create_styled_button

from PyQt6.QtWidgets import QApplication

from limblab import preview_volume

from vedo import Mesh
from pathlib import Path
import numpy as np

class VisualizationController:
    MODES = {
        "Raycast": "raycast",
        "Isosurface": "isosurface",
        "Slab (2D projection)": "slab",
        "Probe": "probe",
    }

    def __init__(self, window):
        self.window = window
        self.current_experiment = None
        self.channel_combo = None
        self.mode_combo = None

    # ------------------------------------------------------------------
    def build_action_bar(self, experiment):
        """Call this from show_viz() and pass the result as `action_widget`
        to `_build_workflow_container`, same as StageController does for
        its Confirm Stage bar."""
        self.current_experiment = experiment

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
        self.window.action_bar.setVisible(False)

        self.window._show_busy('Loading volume...')
        
        #already called from show_viz window
        self.current_experiment = experiment

        # _build_workflow_container() already creates and embeds the render
      
        workflow_container = self.window._build_workflow_container(
            next_label="Clean",
            next_callback=self._go_next_from_viz,
            back_guard=None,
            current_step="Visualize",
            action_widget=self.build_action_bar(self.current_experiment),
        )

        self._current_frame = self.window.frame
        self._current_vtk_widget = self.window.vtkWidget
        self.vtk_widget = self.window.vtkWidget  # kept for the helpers below

        

        # --- realize the widget before any Plotter is built around it ---

        old_central = self.window.centralWidget()
        self.window.setCentralWidget(workflow_container)
        if old_central is not None and old_central is not workflow_container:
            # Qt detaches the outgoing central widget but doesn't delete it,
            # so without this it can keep rendering in its old spot (this is
            # what showed show_exp underneath the visualizer).
            old_central.setParent(None)
            old_central.deleteLater()

        exp = self.current_experiment

        if exp.surface_path and os.path.exists(exp.surface_path):
            #the channel has been cleaned and it ssurface has been extracted (DAPI)
            T = None
            if exp.transformation_matrix_path and os.path.exists(exp.transformation_matrix_path):
                #align has been also done!

                T = np.load(exp.transformation_matrix_path)
                print(T)

                self._show_preview(exp.surface_path, transform=T)


            else: #the channel has only been cleaned and extracted 
                self._show_preview(exp.surface_path)
            

        else:#the channel has only been cleaned or its the raw volume (vti / tiff)
            channels = exp.channels or []
            if channels:
                dapi = next((ch for ch in channels if ch.channel_name.upper() == "DAPI"), None)
                channel = dapi or channels[0]
                        # Use cleaned path if available, else raw path
                path_attr = "clean_path" if getattr(channel, "clean_path", None) else "path"
                full_path = Path(exp.base) / getattr(channel, path_attr)
                if full_path.exists():
                    self._show_preview(full_path)

#once tthe limb visualization is loaded we can show the window!
        
        self.window._hide_busy()
        self.window.show()
        
        QApplication.processEvents()
        self.window._refresh_pipeline_actions(current_step="Visualize")

    def _on_show_clicked(self):                
        if not self.current_experiment or not self.current_experiment.channels:
            QMessageBox.warning(
                self.window, "No channels",
                "This experiment has no channels to visualize."
            )
            return

        channel_name = self.channel_combo.currentText()
        channel = next(
            (ch for ch in self.current_experiment.channels if ch.channel_name == channel_name),
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

        full_path = os.path.join(self.current_experiment.base, clean_path)
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

        # --- realize the widget BEFORE building any Plotter around it ---
        self.window.setCentralWidget(container)
        self.window.show()

        self._current_vtk_widget = vtk_widget
        self._current_frame = frame

        try:
            if mode == "raycast":
                rc_plotter = raycast(
                    self.current_experiment,
                    channel_name=channel.channel_name,
                    qt_widget=vtk_widget,
                )
                self._current_plotter = rc_plotter
            else:
                plotter = Plotter(qt_widget=vtk_widget)
                self._current_plotter = plotter
                if mode == "isosurface":
                    one_channel_isosurface(self.current_experiment, channel_name=channel.channel_name, plotter=plotter)
                elif mode == "slab":
                    dynamic_slab(self.current_experiment, channel_name=channel.channel_name, plotter=plotter)
                elif mode == "probe":
                    probe(self.current_experiment, channel_name=channel.channel_name, plotter=plotter)
                else:
                    QMessageBox.warning(self.window, "Not implemented", f"Mode '{mode_label}' isn't wired up yet.")
                    return
        except Exception as e:
            QMessageBox.critical(
                self.window, "Visualization error",
                f"Failed to render {channel.channel_name}: {e}"
            )
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

        vtk_widget = getattr(self, "_current_vtk_widget", None)
        if vtk_widget is not None:
            vtk_widget.close()
      
        self._current_plotter = None
        self._current_vtk_widget = None
        self._current_frame = None

        self.window.navigate_to(lambda: self.show(self.current_experiment))


            # Keep a ref so Qt doesn't garbage-collect the dialog out from under
            # the plotter, and drop it once the user closes the window.
       

    def _go_next_from_viz(self):
        #visualization has been done and we get back to the initial visualization page!

        # Navigate to Clean stage (you already do this)
        self.window.navigate_to(lambda: self.window.clean.show(self.window.current_experiment))

        # Now decide what to preview:
        exp = self.current_experiment
        if exp.surface_path and os.path.exists(exp.surface_path):
            # Show aligned mesh if surface exists and has a transform
            T = None
            if exp.transformation_matrix_path and os.path.exists(exp.transformation_matrix_path):
                import numpy as np
                T = np.load(exp.transformation_matrix_path)
            self._show_preview(exp.surface_path, transform=T)

        else:
            # Fallback: show a volume (raw or cleaned)
            # Pick a channel – preferably the last cleaned, else DAPI, else first
            last_cleaned = self.window.workflow_state.get("last_cleaned_channel")
            channel = None
            if last_cleaned:
                channel = next((ch for ch in exp.channels if ch.channel_name.upper() == last_cleaned.upper()), None)
            if not channel:
                channel = next((ch for ch in exp.channels if ch.channel_name.upper() == "DAPI"), None) or (exp.channels[0] if exp.channels else None)
            if channel:
                # Use the cleaned path if available, else raw path
                path_attr = "clean_path" if getattr(channel, "clean_path", None) else "path"
                full_path = Path(exp.base) / getattr(channel, path_attr)
                if full_path.exists():
                    self._show_preview(full_path)

        
        if any(
            getattr(ch, "clean_isovalue_min", None) is not None
            for ch in (self.current_experiment.channels or [])
        ):
            self._show_cleaned_channel_preview()
        else:
            self._show_raw_volume_preview(self.current_experiment)



    def _show_preview(self, file_path, transform=None):
        
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        #ext = file_path.suffix.lower()

        # Ensure we have a valid VTK widget (use the one from the main view)
        vtk_widget = getattr(self, "vtk_widget", None)
        if vtk_widget is None:
            print("No VTK widget available – cannot show preview.")
            return

        ext = file_path.suffix.lower()

        try:
            if ext == ".vtk":#already cleaned volume -> showing extracted surface!
                # Surface mesh preview
                mesh = Mesh(str(file_path))
                if transform is not None:
                    mesh.apply_transform(transform)

                self.viz_plotter = Plotter(qt_widget=vtk_widget)
                self.viz_plotter.show(mesh)

        
            #raw preview!
            else:
                self.viz_plotter = preview_volume(
                            raw_volume_path=file_path,
                            renderer="pyqt",
                            outside_class=self
                )
        except Exception as e:
            print(f"Error showing preview: {e}")
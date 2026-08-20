import os
from pathlib import Path
from typing import Any

import numpy as np
from limblab import preview_volume
from limblab.design import theme
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
from vedo import LinearTransform, Mesh, Plotter, Volume
from vedo.applications import IsosurfaceBrowser
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


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

    def show_experiment(self, experiment):
        self.window.action_bar.setVisible(False)
        self.window._show_busy('Loading volume...')

      
        workflow_container = self.window._build_workflow_container(
            next_label="Clean",
            next_callback=self._go_next_from_viz,
            back_guard=None,
            current_step="Visualize",
            action_widget=self.build_action_bar(experiment),
        )

        self._current_frame = self.window.frame
        self._current_vtk_widget = self.window.vtkWidget
        self.vtk_widget = self.window.vtkWidget  # kept for the helpers below

        self.window.setCentralWidget(None)
        
        self.window._refresh_pipeline_actions(current_step="Visualize")
        QApplication.processEvents()
        self.window.show()

        self.window.setCentralWidget(workflow_container)

    
        surface_path = os.path.join(experiment.base, experiment.surface_path) #.replace('/','\\')

        mesh = Mesh(surface_path).c(theme("limblab.surface"))

        params: dict[str, Any] = dict(bg = theme("palette.background"))
        kwargs = generate_kwargs(params=params, renderer='pyqt', outside_class=self.window)
        
        plt = Plotter(**kwargs)

        plt.add(mesh)
        
        plt.show(interactive=False)
    
        plt.close()

        self.window._hide_busy()


#channel specific visualization!
    def show_channel(self, experiment, channel):

        self.window.action_bar.setVisible(False)
        
        self.window._show_busy('Loading volume...')
        
        workflow_container = self.window._build_workflow_container(
                    next_label="Clean",
                    next_callback=self._go_next_from_viz,
                    back_guard=None,
                    current_step="Visualize",
                    action_widget=self.build_action_bar(experiment),
                )
        
        self._current_frame = self.window.frame
        self._current_vtk_widget = self.window.vtkWidget
        self.vtk_widget = self.window.vtkWidget  # kept for the helpers below
        
                


        
        # path_attr = "clean_path" if getattr(channel, "clean_path", None) else "path"
        # full_path = Path(experiment.base) / getattr(channel, path_attr)
        # print(full_path)
        # if full_path.exists():
        #     print('HERE')
        #     self._show_preview(full_path)

        # self.window._hide_busy()
        # self.window.show()
                
        # QApplication.processEvents()
        # self.window._refresh_pipeline_actions(current_step="Visualize")



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

        self._current_vtk_widget = vtk_widget
        self._current_frame = frame

        try:
            if mode == "raycast":
                rc_plotter = raycast(
                    self.experiment,
                    channel_name=channel.channel_name,
                    qt_widget=vtk_widget,
                )
                self._current_plotter = rc_plotter

            elif mode == 'isosurface':
                iso_plotter = one_channel_isosurface(
                                        self.experiment,
                                        channel_name=channel.channel_name,
                                        qt_widget = vtk_widget
                                        
                                    )
                self._current_plotter = iso_plotter

            elif mode == "slab":
                dynamic_slab(self.experiment, channel_name=channel.channel_name)

            elif mode == "probe":
                probe(self.experiment, channel_name=channel.channel_name)

   

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

        self.show_experiment(self.experiment)

    
    def _go_next_from_viz(self):
        print('dead end')
        #visualization has been done and we get back to the initial visualization page!

        # # Navigate to Clean stage (you already do this)
        # self.window.navigate_to(lambda: self.window.clean.show(self.window.experiment))

        # # Now decide what to preview:
        # exp = self.experiment
        # if exp.surface_path and os.path.exists(exp.surface_path):
        #     # Show aligned mesh if surface exists and has a transform
        #     T = None
        #     if exp.transformation_matrix_path and os.path.exists(exp.transformation_matrix_path):
        #         import numpy as np
        #         T = np.load(exp.transformation_matrix_path)
        #     self._show_preview(exp.surface_path, transform=T)

        # else:
        #     # Fallback: show a volume (raw or cleaned)
        #     # Pick a channel – preferably the last cleaned, else DAPI, else first
        #     last_cleaned = self.window.workflow_state.get("last_cleaned_channel")
        #     channel = None
        #     if last_cleaned:
        #         channel = next((ch for ch in exp.channels if ch.channel_name.upper() == last_cleaned.upper()), None)
        #     if not channel:
        #         channel = next((ch for ch in exp.channels if ch.channel_name.upper() == "DAPI"), None) or (exp.channels[0] if exp.channels else None)
        #     if channel:
        #         # Use the cleaned path if available, else raw path
        #         path_attr = "clean_path" if getattr(channel, "clean_path", None) else "path"
        #         full_path = Path(exp.base) / getattr(channel, path_attr)
        #         if full_path.exists():
        #             self._show_preview(full_path)

        
        # if any(
        #     getattr(ch, "clean_isovalue_min", None) is not None
        #     for ch in (self.current_experiment.channels or [])
        # ):
        #     self._show_cleaned_channel_preview()
        # else:
        #     self._show_raw_volume_preview(self.current_experiment)



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

            #TEMPORAL FIX!!!


            if ext == ".vtk":#already cleaned volume -> showing extracted surface!
                # Surface mesh preview
                print('this doestn work yet')
                ''''
                vol = Volume(str(file_path))
                
                
                params: dict[str, Any] = dict(use_gpu=True, bg = theme("palette.background"), c=theme("limblab.surface"), alpha=0.6)
                kwargs = generate_kwargs(
                        params=params, renderer='pyqt', outside_class=self.window
                    )
                
                plt = IsosurfaceBrowser(vol.color((255, 127, 17, 0)), **kwargs)
                
                    #allows to extracte the selected isovalue through the vedo slider
                   
                plt.show(axes=7, interactive=False)
                plt.close()
                '''

            if ext == '.vti':
                vol = Volume(str(file_path))
                
                params: dict[str, Any] = dict(use_gpu=True, bg = theme("palette.background"), c=theme("limblab.surface"))
                kwargs = generate_kwargs(
                        params=params, renderer='pyqt', outside_class=self.window
                    )
                
                plt = IsosurfaceBrowser(vol, **kwargs)
                plt.show(interactive=False)
                plt.close()

            
            #raw preview!
            else:
                self.viz_plotter = preview_volume(
                                raw_volume_path=file_path,
                                renderer="pyqt",
                                outside_class=self.window
                )
        except Exception as e:
            print(f"Error showing preview: {e}")


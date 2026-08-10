# pyright: reportOptionalMemberAccess=false
# pyright: ignore[reportAttributeAccessIssue]

import os
import webbrowser
from pathlib import Path

import numpy as np
import pyqtgraph as pg
import vtk

# from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules
from config import *
from limblab.database import (
    delete_experiment,
    get_experiment,
    init_db,
    list_experiments,
    save_experiment,
)
from limblab.models import Channel, Experiment
from limblab.params import CleanParams
from Mixin.NavigationMixin import NavigationMixin
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from utils import (
    create_back_button,
    create_collapsible_section,
    create_label,
    create_styled_button,
)
from vedo import Mesh, Plotter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

vtkmodules.qt.QVTKRWIBase = "QGLWidget"

import traceback
from types import SimpleNamespace

from Controllers.align_controller import AlignController

from Controllers.surface_controller import SurfaceController

from limblab import clean


#laura
#TEST_BASE_PATH = "/Users/laura/Desktop/Desktop-2026/sox9-fig-thesis"
#TEST_SURFACE_PATH = "HCR11_MEIS2_l1_dapi_488_LF_surface.vtk"

#gemma
TEST_BASE_PATH = "C:\\Users\\millan\\Desktop\\test"
TEST_SURFACE_PATH = "HCR12_HOXA11_l1_dapi_405_LF_surface.vtk"

#this is for the SURFACE test! the direct .tiff is required (DAPI)
TEST_DAPI_FILENAME = "HCR12_HOXA11_l1_dapi_405_LF.tif" 

#for the test experiment i added the channels manually 
experiment = Experiment(
    experiment_id="manual_test",
    base=TEST_BASE_PATH,
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="F",
    position="L",
    species="mouse",
    surface=TEST_SURFACE_PATH,
    stage=260,
    channels=[
        Channel(
            experiment_id="manual_test",
            channel_name="DAPI",
            path=TEST_DAPI_FILENAME,
            v0=238.0,
            v1=463.0,
        )
    ],
)



class MainWindow(QMainWindow, NavigationMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LimbLab")
        self.setStyleSheet("QMainWindow, QWidget { background-color: #141414; }")
        self.setStatusBar(QStatusBar(self))

        ##########
        # DATABASE
        self.db_path = Path("experiments.db")

        if not self.db_path.exists():
            init_db(self.db_path)  # Creates empty database with schema only
            print(f"Created empty database: {self.db_path}")

        else:
            print(f"Using existing database: {self.db_path}")

        self._load_experiments_from_db()
        # DATABASE END
        ##############

        ############
        # NAMESPACES
        self.ui = SimpleNamespace()
        self.viewer = SimpleNamespace()
        # NAMESPACES END
        ################

        self.experiments = []
        self.experiment_names = {}
        self.pipeline_log = []
        self.param_values = {}
        self.nav_stack = []
        self.current_screen = None
        self.active_categories = []
        self.active_viz_sections = []
        self.check_genes_viz = ["Hoxa11", "Sox9", "BMP2"]
        self.filepath = None

        # ---- Workflow state ----
        # Tracks whether the required action for each step of the
        # Viz -> Clean -> Surface -> Stage -> Align pipeline has been
        # completed. This drives both forward-navigation guards (can't
        # jump ahead without finishing the current step) and back
        # navigation warnings (you're about to lose unsaved progress).
        self.workflow_state = {
            "clean_done": False,
            "last_cleaned_channel": None,
            "surface_done": False,
            "stage_done": False,
            "selected_stage": None,
            "align_done": False,
            "alignment_method": None,
        }

        self.align = AlignController(self)
        self.current_experiment = experiment

        # Initial
        #self.navigate_to(lambda: self.align.show(experiment))


        self.surface = SurfaceController(self)
        self.navigate_to(lambda: self.surface.show(experiment))


        #TODO : self navigate home as initial home screen
       #self.navigate_to(lambda: self.show_home())


    # ------------------------------------------------------------------
    # Menu Building Methods
    # ------------------------------------------------------------------
    def _build_resources_menu(self, menu):
        """Build the Resources submenu."""
        resources = menu.addMenu("Resources")
        paper = QAction("Paper", self)
        paper.triggered.connect(
            lambda: webbrowser.open(
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC12794269/"
            )
        )
        resources.addAction(paper)

        github = QAction("GitHub", self)
        github.triggered.connect(
            lambda: webbrowser.open("https://limblab.embl.es/docs/")
        )
        resources.addAction(github)
        return resources

    def _build_contact_menu(self, menu):
        """Build the Contact us submenu."""
        contact = menu.addMenu("Contact us")

        # contact.addAction(QLabel("EMBL, Barcelona", self))
        # contact.addAction(QLabel("info@embl.es", self))
        return contact

    def _build_file_menu(self, menu_bar):
        """Build the File menu."""
        file_menu = menu_bar.addMenu("&File")
        actions = [
            ("New experiment", "Ctrl+N"),
            ("Open experiment", "Ctrl+O"),
            ("Duplicate experiment", None),
            (None, None),  # Separator
            ("Import Limb", None),
            ("Add Channel to experiment", None),
            ("Import Reference Model", None),
            (None, None),  # Separator
            ("Export Cleaned Volume", None),
            ("Export Surface Mesh", None),
            ("Export Transformation Matrix", None),
            ("Export Figure/Snapshot", None),
            ("View pipe.log", None),
            ("Save Current Experiment State", "Ctrl+S"),
            (None, None),  # Separator
            ("Delete experiment", None),
        ]

        for text, shortcut in actions:
            if text is None:
                file_menu.addSeparator()
            else:
                action = QAction(text, self)
                if shortcut:
                    action.setShortcut(shortcut)
                action.triggered.connect(self.menu_button_clicked)
                file_menu.addAction(action)
        return file_menu

    def _build_view_menu(self, menu_bar):
        """Build the View menu."""
        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(QAction("Visualization Mode", self))

        viz_modes = ["Isosurface", "Slices", "Raycast", "Probe", "2D Projection Slab"]
        for mode in viz_modes:
            action = QAction(mode, self)  # , checkable=True
            action.triggered.connect(lambda checked, m=mode: self.add_viz_section(m))
            view_menu.addAction(action)
        return view_menu

    # ------------------------------------------------------------------
    # Shared workflow-screen layout
    #
    # Every step of the pipeline (Viz, Clean, Surface, Stage, Align)
    # uses the exact same shell:
    #   - top row: Back button | Left menu | ...stretch... | Next-step button
    #   - the live 3D viewer
    #   - an optional per-step action bar just below the viewer
    #   - the same right-hand side panel (Visualizer / Pipeline / params)
    # This is what keeps the layout visually identical as the user moves
    # through the pipeline.
    # ------------------------------------------------------------------
    def _build_workflow_top_row(
        self, next_label=None, next_callback=None, back_guard=None
    ):
        """Build the Back | Left-menu | ...stretch... | Next-step-button row.

        back_guard, if given, is a zero-arg callable returning
        (is_done: bool, message: str). If is_done is False when the user
        presses Back, they get a confirmation popup telling them what
        they haven't done yet before letting them leave the screen.
        """
        top_row = QHBoxLayout()

        back_btn = create_back_button(lambda: self._handle_back(back_guard))
        top_row.addWidget(back_btn)
        top_row.addWidget(self._create_left_button())
        top_row.addStretch()

        if next_label and next_callback:
            next_btn = create_styled_button(next_label, "#0D7C66", "#41B3A2")
            next_btn.clicked.connect(next_callback)
            top_row.addWidget(next_btn)

        return top_row

    def _handle_back(self, guard=None):
        """Go back, warning the user first if the current step isn't finished."""
        if guard is not None:
            done, message = guard()
            if not done:
                reply = QMessageBox.question(
                    self,
                    "Step not completed",
                    f"{message}\n\nGo back anyway? Progress on this step will be lost.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        self.go_back()

    def _reset_top_menu_bar(self):
        """Clear the QMainWindow menu bar back to its plain (non-home) state."""
        menu_bar = self.menuBar()
        menu_bar.setVisible(True)
        menu_bar.setStyleSheet("")
        old_corner = menu_bar.cornerWidget(Qt.Corner.TopRightCorner)
        menu_bar.setCornerWidget(None)
        if old_corner is not None:
            old_corner.deleteLater()
        menu_bar.clear()
        return menu_bar

    def _build_workflow_container(
        self,
        next_label=None,
        next_callback=None,
        back_guard=None,
        action_widget=None,
    ):
        """Build the shared viewer + side-panel container used by every step screen."""

        top_row = self._build_workflow_top_row(
            next_label,
            next_callback,
            back_guard,
        )

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addLayout(top_row)

        if action_widget is not None:
            left_layout.addWidget(action_widget)

        # ------------------------------------------------------------------
        # Create the VTK widget that vedo will render into
        # ------------------------------------------------------------------
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        left_layout.addWidget(self.vtk_widget, stretch=1)

        side_panel = self._build_side_panel()

        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(left_container, stretch=1)
        main_layout.addWidget(side_panel, stretch=0)

        return container

    # ------------------------------------------------------------------
    # Screen Methods
    # ------------------------------------------------------------------
    def show_home(self):
        self.reset_menu_bar()

        menu_bar = self.menuBar()
        lb_action = QAction("LimbLab", self)
        lb_action.triggered.connect(
            lambda: webbrowser.open("https://limblab.embl.es/docs/")
        )
        menu_bar.addAction(lb_action)

        right_menu = QMenuBar(menu_bar)
        menu_bar.setCornerWidget(right_menu, Qt.Corner.TopRightCorner)

        self._build_resources_menu(right_menu)

        aboutus_action = QAction("About us", self)
        aboutus_action.triggered.connect(
            lambda: webbrowser.open("https://www.embl.org/groups/sharpe/")
        )
        right_menu.addAction(aboutus_action)

        self._build_contact_menu(right_menu)

        menu_bar.setStyleSheet("""
            QMenuBar { background-color: #0D7C66; color: white; }
            QMenuBar::item { background-color: transparent; color: white; padding: 20px 30px; }
            QMenuBar::item:selected { background-color: #41B3A2; }
        """)

        left_panel = QWidget()
        get_started_btn = create_styled_button("Get Started", size=50)
        get_started_btn.clicked.connect(
            lambda: self.navigate_to(self.show_first_screen)
        )

        label_main = QLabel(
            '<span style="font-size:100px; font-weight:bold; color:#5FBF9F;">Limb</span>'
            '<span style="font-size:100px; font-weight:bold; color:#8E7FD6;">Lab</span>'
        )
        label_main.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sublabel_main = create_label(
            "Analyze your 3D limb data with unprecedented ease.",
            "color: #A0A0A0; font-size: 20px;",
        )

        left_layout = QVBoxLayout(left_panel)
        left_layout.addStretch(1)
        left_layout.addWidget(label_main, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addWidget(sublabel_main, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addSpacing(20)
        left_layout.addWidget(get_started_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch(2)
        left_layout.setContentsMargins(40, 0, 40, 0)

        self.frame = QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        self.plt = Plotter(qt_widget=self.vtkWidget)
        # Create vedo renderer and add objects and callbacks
        self.limb_home = Mesh("Limb-rec_281.vtk")

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(left_panel, stretch=3)
        layout.addWidget(self.vtkWidget, stretch=2)
        self.setCentralWidget(container)

        self.plt.show(self.limb_home)  # build the vedo rendering

    def show_first_screen(self):
        self.reset_menu_bar()

        top_row = QHBoxLayout()
        top_row.addWidget(create_back_button(self.go_back))
        top_row.addWidget(self._create_left_button())
        top_row.addStretch()

        # ---- Create New Experiment ----
        self.label_upload = create_label("Create New Experiment", "color: #ffffff; font-size: 40px;")
        self.button_upload = create_styled_button("Upload TIF Volume", "#0D7C66", "#41B3A2")
        self.button_upload.clicked.connect(self.create_new_experiment)

        upload_desc = create_label(
            "Upload a TIF volume to start a new experiment.\n"
            "You can add more channels later.",
            "color: #A0A0A0; font-size: 14px; text-align: center;"
        )
        upload_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_desc.setWordWrap(True)

        
        # ---- Library Access ----
        self.label_library = create_label("Access Limb Library", "color: #ffffff; font-size: 40px;")
        self.button_library = create_styled_button("View Experiments", "#41B3A2", "#5FBF9F")
        self.button_library.clicked.connect(lambda: self.navigate_to(self.show_exp))

        library_desc = create_label(
            "View and manage your existing experiments\n"
            "or load them for visualization.",
            "color: #A0A0A0; font-size: 14px; text-align: center;"
        )
        library_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        library_desc.setWordWrap(True)

        # ---- Layout ----
        upload_column = QVBoxLayout()
        upload_column.addWidget(self.label_upload, alignment=Qt.AlignmentFlag.AlignHCenter)
        upload_column.addWidget(self.button_upload, alignment=Qt.AlignmentFlag.AlignHCenter)
        upload_column.addWidget(upload_desc, alignment=Qt.AlignmentFlag.AlignHCenter)

        library_column = QVBoxLayout()
        library_column.addWidget(self.label_library, alignment=Qt.AlignmentFlag.AlignHCenter)
        library_column.addWidget(self.button_library, alignment=Qt.AlignmentFlag.AlignHCenter)
        library_column.addWidget(library_desc, alignment=Qt.AlignmentFlag.AlignHCenter)

        buttons_row = QHBoxLayout()
        buttons_row.addLayout(upload_column)
        buttons_row.addSpacing(40)
        buttons_row.addLayout(library_column)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addLayout(top_row)
        layout.addStretch(1)
        layout.addLayout(buttons_row, stretch=0)
        layout.addStretch(2)
        self.setCentralWidget(container)


    def show_exp(self):
        self.reset_menu_bar()

        if not self.db_path.exists():
            # Database doesn't exist, create it with test data
            init_db(self.db_path)

            print("Created new database with data")

        else:
            # Database exists, check if it has any experiments
            experiments = list_experiments(self.db_path)
            if not experiments:
                # Database exists but empty, generate test data
                init_db(self.db_path)
                print("Generated test data in existing database")
            else:
                print(f"Found {experiments} existing experiments")

        self._load_experiments_from_db()
        # load database! TESTING

        top_row = QHBoxLayout()
        top_row.addWidget(create_back_button(self.go_back))
        top_row.addWidget(self._create_left_button())
        top_row.addStretch()

        card_layout = QVBoxLayout()
        self.experiment_checkboxes = []

        for path in self.experiments:
            display_name = self.experiment_names.get(path, os.path.basename(path))



            exp_data = self.experiment_metadata.get(path, {})
            channels = exp_data.get('channels', [])
            channel_names = [ch.get('channel_name', '') for ch in channels]
        
            # Check if experiment is complete (has DAPI + gene)
            is_valid, status_message = self._validate_experiment_channels(path)
            status_icon = "✅" if is_valid else "⚠️"
            status_color = "#41B3A2" if is_valid else "#FF6B6B"


            # Show channel info
            channel_display = ""
            if channels:
                channel_display = f"[{', '.join(channel_names)}]"
            else:
                channel_display = "[No channels]"
            
            # Create row with status indicator
            row = QHBoxLayout()
            
            # Experiment name with status
            name_label = QLabel(f"{status_icon} {display_name}")
            name_label.setStyleSheet(f"color: {status_color}; font-size: 18px;")
            name_label.setToolTip(status_message if not is_valid else "Experiment is complete")
            
            # Show channel count
            exp_data = self.experiment_metadata.get(path, {})
            channels = exp_data.get('channels', [])
            channel_count = len(channels)
            channel_info = QLabel(f"({channel_count} channels)")
            channel_info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
            
            threebutton = QToolButton()
            threebutton.setIcon(QIcon("threedots.png"))
            threebutton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            threebutton.clicked.connect(lambda checked, p=path, b=threebutton: self._click_threebuttons(p, b))

            checkbox = QCheckBox()
            checkbox.setEnabled(is_valid)  # Only enable checkbox for complete experiments
            if not is_valid:
                checkbox.setToolTip("Incomplete experiment - needs DAPI and at least one gene channel")
            
            row.addWidget(name_label)
            row.addWidget(channel_info)
            row.addWidget(checkbox)
            row.addWidget(threebutton)
            row.addStretch()
            card_layout.addLayout(row)
            self.experiment_checkboxes.append((path, checkbox))

        card_layout.addStretch()

        experiments_card = QWidget()
        experiments_card.setStyleSheet(
            "background-color: #2A2A2A; border-radius: 12px;"
        )
        experiments_card.setLayout(card_layout)
        experiments_card.setMinimumHeight(250)

        self.add_btn = create_styled_button('+ Add Experiment', "#7C6FD6", "#8E7FD6")
        self.save_btn = create_styled_button('Save Experiment', "#4B2E83", "#5C3A9E")
        self.view_btn = create_styled_button('View Experiment', "#41B3A2", "#5FBF9F")
        self.refresh_btn = create_styled_button('↻ Refresh', "#4B2E83", "#5C3A9E")

        self.view_btn.clicked.connect(self.viewexp_button_clicked)
        self.refresh_btn.clicked.connect(self._refresh_experiments)

        buttons_row = QVBoxLayout()
        buttons_row.setContentsMargins(0, 20, 0, 20)

        self.add_btn.clicked.connect(self.addexp_button_clicked)
        self.save_btn.clicked.connect(self.saveexp_button_clicked)
        self.view_btn.clicked.connect(self.viewexp_button_clicked)

        buttons_row = QVBoxLayout()
        buttons_row.setContentsMargins(0, 20, 0, 20)  # Add vertical padding

        # Add stretch before and after to center the group, but with big spacing
        buttons_row.addStretch(1)  # Big stretch on left
        buttons_row.addWidget(self.add_btn)
        buttons_row.addSpacing(10)  # Space between buttons
        buttons_row.addWidget(self.save_btn)
        buttons_row.addSpacing(10)  # Space between buttons
        buttons_row.addStretch(1)
        buttons_row.addWidget(self.view_btn)
        buttons_row.addSpacing(10)
        buttons_row.addWidget(self.refresh_btn)
        buttons_row.addStretch(1)

        # Assemble everything
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.addLayout(top_row)
        main_layout.addWidget(experiments_card, stretch=1)

        # Add the buttons row with some spacing
        main_layout.addSpacing(10)
        main_layout.addLayout(buttons_row)
        main_layout.addStretch(1)  # Extra stretch at bottom
        main_layout.setContentsMargins(30, 20, 30, 5)

        self.setCentralWidget(container)

    # ---- Pipeline step screens (Viz -> Clean -> Surface -> Stage -> Align -> Viz) ----

    def _refresh_experiments(self):
        """Refresh the experiments list."""
        self._load_experiments_from_db()
        self.show_exp()
        QMessageBox.information(self, "Refreshed", "Experiment list updated.")



    def show_viz(self):
        """Visualization screen. Top bar just shows the Clean button (the next step)."""
        container = self._build_workflow_container(
            next_label="Clean",
            next_callback=lambda: self.navigate_to(self.show_clean),
            back_guard=None,  # nothing to lose by leaving the visualizer
        )
        self.setCentralWidget(container)

        menu_bar = self._reset_top_menu_bar()
        self._build_file_menu(menu_bar)
        self._build_view_menu(menu_bar)

        if self.filepath:
            self.update_viewer(self.filepath)

    def update_viewer(self, filepath):
        """Load REAL limb object from database and display"""
        if not filepath:
            return

        # Get experiment data from database
        exp_data = self.experiment_metadata.get(filepath)
        if not exp_data:
            print(f"Experiment not found in database: {filepath}")
            return

        # Get the volume file path
        if exp_data.get("channels") and len(exp_data["channels"]) > 0:
            # Use first channel
            channel = exp_data["channels"][0]
            channel_path = channel.get("path")

            if channel_path:
                full_path = os.path.join(exp_data["base"], channel_path)

                # Check if file exists
                if os.path.exists(full_path):
                    print(f"Loading volume: {full_path}")

                    self.show_basic_mesh(filepath)

    def show_basic_mesh(self, path):
        """Display a mesh in the vedo viewer"""
        if not path or not os.path.exists(path):
            print(f"File not found: {path}")
            return None

        # Reuse existing widgets or create once
        if not hasattr(self, "frame"):
            self.frame = QFrame()
            self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
            self.plt = Plotter(qt_widget=self.vtkWidget)

        try:
            # Load the mesh
            self.limb_object = Mesh(path)

            # Clear previous objects and add new one
            self.plt.clear()
            self.plt.add(self.limb_object)

            # Render the scene
            self.plt.render()

            return self.plt

        except Exception as e:
            print(f"Error loading mesh: {e}")
            return None

    def show_clean(self):
        """Clean screen. Top bar shows the Extract Surface button (the next step)."""
        container = self._build_workflow_container(
            next_label="Extract Surface",
            next_callback=self._go_next_from_clean,
            back_guard=lambda: (
                self.workflow_state["clean_done"],
                "You haven't cleaned any volume yet.",
            ),
            action_widget=self._build_clean_action_bar(),
        )
        self.setCentralWidget(container)

        menu_bar = self._reset_top_menu_bar()
        self._build_file_menu(menu_bar)
        self._build_view_menu(menu_bar)

    def _build_clean_action_bar(self):
        """Build the clean action bar with all CleanParams widgets."""
        bar = QWidget()
        bar.setStyleSheet("background-color: #1E1E1E;")
        layout = QVBoxLayout(bar)  # Changed to VBox for more widgets
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Store widgets for parameter access
        self.clean_widgets = {}

        # === Channel Selection ===
        channel_row = QHBoxLayout()
        channel_label = create_label(
            "Channel:", "color: #ffffff; font-size: 13px; font-weight: bold;"
        )
        channel_row.addWidget(channel_label)

        channel_combo = QComboBox()
        channel_combo.addItems(["DAPI","BMP2", "Sox9", "Hoxa11"])
        channel_combo.setStyleSheet("""
            QComboBox { 
                color: #ffffff; 
                background-color: #2A2A2A; 
                border: 1px solid #41B3A2;
                border-radius: 6px; 
                padding: 4px 8px; 
                font-size: 12px; 
                min-width: 120px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { 
                background-color: #2A2A2A; 
                color: #ffffff;
                selection-background-color: #41B3A2; 
            }
        """)
        channel_row.addWidget(channel_combo)
        channel_row.addStretch()
        layout.addLayout(channel_row)
        self.clean_widgets["channel"] = channel_combo

        # === Isovalue Parameters (v0 and v1) ===
        isovalue_group = QGroupBox("Isovalue Thresholds")
        isovalue_group.setStyleSheet("""
            QGroupBox {
                color: #A0A0A0;
                border: 1px solid #2A2A2A;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        isovalue_layout = QVBoxLayout(isovalue_group)
        isovalue_layout.setSpacing(8)

        # Lower isovalue (v0)
        v0_row = QHBoxLayout()
        v0_label = create_label("Lower (v0):", "color: #ffffff; font-size: 12px;")
        v0_label.setFixedWidth(100)
        v0_spin = QDoubleSpinBox()
        v0_spin.setRange(0, 1000)
        v0_spin.setSingleStep(10)
        v0_spin.setValue(100)
        v0_spin.setDecimals(1)
        v0_spin.setStyleSheet("""
            QDoubleSpinBox {
                color: #ffffff;
                background-color: #2A2A2A;
                border: 1px solid #41B3A2;
                border-radius: 4px;
                padding: 4px;
                min-width: 80px;
            }
        """)
        v0_row.addWidget(v0_label)
        v0_row.addWidget(v0_spin)
        v0_row.addStretch()
        isovalue_layout.addLayout(v0_row)
        self.clean_widgets["v0"] = v0_spin

        # Upper isovalue (v1)
        v1_row = QHBoxLayout()
        v1_label = create_label("Upper (v1):", "color: #ffffff; font-size: 12px;")
        v1_label.setFixedWidth(100)
        v1_spin = QDoubleSpinBox()
        v1_spin.setRange(0, 1000)
        v1_spin.setSingleStep(10)
        v1_spin.setValue(400)
        v1_spin.setDecimals(1)
        v1_spin.setStyleSheet("""
            QDoubleSpinBox {
                color: #ffffff;
                background-color: #2A2A2A;
                border: 1px solid #41B3A2;
                border-radius: 4px;
                padding: 4px;
                min-width: 80px;
            }
        """)
        v1_row.addWidget(v1_label)
        v1_row.addWidget(v1_spin)
        v1_row.addStretch()
        isovalue_layout.addLayout(v1_row)
        self.clean_widgets["v1"] = v1_spin

        layout.addWidget(isovalue_group)

        # === Gaussian Sigma ===
        sigma_row = QHBoxLayout()
        sigma_label = create_label(
            "Gaussian Sigma:", "color: #ffffff; font-size: 12px;"
        )
        sigma_label.setFixedWidth(120)
        sigma_spin = QDoubleSpinBox()
        sigma_spin.setRange(0.1, 10.0)
        sigma_spin.setSingleStep(0.1)
        sigma_spin.setValue(1.5)
        sigma_spin.setDecimals(1)
        sigma_spin.setStyleSheet("""
            QDoubleSpinBox {
                color: #ffffff;
                background-color: #2A2A2A;
                border: 1px solid #41B3A2;
                border-radius: 4px;
                padding: 4px;
                min-width: 80px;
            }
        """)
        sigma_row.addWidget(sigma_label)
        sigma_row.addWidget(sigma_spin)
        sigma_row.addStretch()
        layout.addLayout(sigma_row)
        self.clean_widgets["gaussian_sigma"] = sigma_spin

        # === Frequency Cutoff ===
        freq_row = QHBoxLayout()
        freq_label = create_label(
            "Frequency Cutoff:", "color: #ffffff; font-size: 12px;"
        )
        freq_label.setFixedWidth(120)
        freq_spin = QDoubleSpinBox()
        freq_spin.setRange(0.01, 1.0)
        freq_spin.setSingleStep(0.05)
        freq_spin.setValue(0.3)
        freq_spin.setDecimals(2)
        freq_spin.setStyleSheet("""
            QDoubleSpinBox {
                color: #ffffff;
                background-color: #2A2A2A;
                border: 1px solid #41B3A2;
                border-radius: 4px;
                padding: 4px;
                min-width: 80px;
            }
        """)
        freq_row.addWidget(freq_label)
        freq_row.addWidget(freq_spin)
        freq_row.addStretch()
        layout.addLayout(freq_row)
        self.clean_widgets["frequency_cutoff"] = freq_spin

        # === Low Res Size ===
        res_row = QHBoxLayout()
        res_label = create_label("Low Res Size:", "color: #ffffff; font-size: 12px;")
        res_label.setFixedWidth(120)
        res_spin = QSpinBox()
        res_spin.setRange(64, 512)
        res_spin.setSingleStep(16)
        res_spin.setValue(256)
        res_spin.setStyleSheet("""
            QSpinBox {
                color: #ffffff;
                background-color: #2A2A2A;
                border: 1px solid #41B3A2;
                border-radius: 4px;
                padding: 4px;
                min-width: 80px;
            }
        """)
        res_row.addWidget(res_label)
        res_row.addWidget(res_spin)
        res_row.addStretch()
        layout.addLayout(res_row)
        self.clean_widgets["low_res_size"] = res_spin

        # === Execute Button ===
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        execute_btn = create_styled_button("Clean Volume", "#0D7C66", "#41B3A2")
        execute_btn.setFixedHeight(40)
        execute_btn.setFixedWidth(200)
        execute_btn.clicked.connect(self._execute_clean)
        btn_row.addWidget(execute_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        return bar




    def _go_next_from_clean(self):

        self.navigate_to(self.show_surface)





        ''''
        """Guard for Clean -> Surface: must have cleaned, and specifically cleaned DAPI."""
        if not self.workflow_state["clean_done"]:
            QMessageBox.warning(
                self, "Clean required",
                "Please clean a channel before extracting the surface."
            )
            return
        if self.workflow_state["last_cleaned_channel"] != "DAPI":
            QMessageBox.information(
                self, "DAPI channel required",
                "Surface extraction can only be performed on DAPI channel data.\n"
                "Please clean the DAPI channel before continuing."
            )
            return
        '''


    ''''
    def show_surface(self):
        """Surface screen. Top bar shows the Stage button (the next step)."""
        container = self._build_workflow_container(
            next_label="Stage",
            next_callback=self._go_next_from_surface,
            back_guard=lambda: (
                self.workflow_state["surface_done"],
                "You haven't extracted a surface yet.",
            ),
            action_widget=self._build_surface_action_bar(),
        )
        self.setCentralWidget(container)

        menu_bar = self._reset_top_menu_bar()
        self._build_file_menu(menu_bar)
        self._build_view_menu(menu_bar)


    '''


    ''''
    def _execute_surface(self):
        """Run surface extraction. DAPI-only, same restriction shown again defensively."""
        if self.workflow_state.get("last_cleaned_channel") != "DAPI":
            QMessageBox.information(
                self,
                "DAPI channel required",
                "Surface extraction can only be performed on DAPI channel data.",
            )
            return

        try:
            # TODO: replace this with your real surface-extraction call, e.g.:
            #   result = extract_surface(experiment=exp_data, channel_name="DAPI", params=...)
            self.workflow_state["surface_done"] = True
            self.log_pipeline("Surface extracted from DAPI channel.")
            QMessageBox.information(self, "Success", "Surface extraction completed.")
        except Exception as e:
            QMessageBox.critical(
                self, "Surface Error", f"Failed to extract surface: {str(e)}"
            )
            self.log_pipeline(f"Surface extraction error: {str(e)}")

    def _go_next_from_surface(self):
        """Guard for Surface -> Stage: must have extracted a surface."""
        if not self.workflow_state["surface_done"]:
            QMessageBox.warning(
                self,
                "Surface required",
                "Please extract a surface before proceeding to Stage.",
            )
            return
        self.navigate_to(self.show_stage)



    '''
    ######################################################################################################
    ''''
    def show_stage(self):
        """Stage screen. Top bar shows the Align button (the next step)."""
        container = self._build_workflow_container(
            next_label="Align",
            next_callback=self._go_next_from_stage,
            back_guard=lambda: (
                self.workflow_state["stage_done"],
                "You haven't selected and confirmed a stage yet.",
            ),
            action_widget=self._build_stage_action_bar(),
        )
        self.setCentralWidget(container)

        menu_bar = self._reset_top_menu_bar()

        self._build_file_menu(menu_bar)
        self._build_view_menu(menu_bar)



    def _build_stage_action_bar(self):
        """Stage picker + Confirm Stage button, shown under the viewer on the Stage screen."""
        bar = QWidget()
        bar.setStyleSheet("background-color: #1E1E1E;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        label = create_label("Stage:", "color: #ffffff; font-size: 13px;")

        stage_combo = QComboBox()
        stage_combo.addItems(
            [
                "Stage 20 - E10.5",
                "Stage 22 - E11.5",
                "Stage 24 - E12.5",
                "Stage 26 - E13.5",
            ]
        )
        if self.workflow_state.get("selected_stage") in [
            stage_combo.itemText(i) for i in range(stage_combo.count())
        ]:
            stage_combo.setCurrentText(self.workflow_state["selected_stage"])
        stage_combo.setStyleSheet("""
            QComboBox { color: #ffffff; background-color: #2A2A2A; border: 1px solid #41B3A2;
                        border-radius: 6px; padding: 4px 8px; font-size: 12px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #2A2A2A; color: #ffffff;
                        selection-background-color: #41B3A2; }
        """)

        confirm_btn = create_styled_button("Confirm Stage", "#0D7C66", "#41B3A2")
        confirm_btn.clicked.connect(
            lambda: self._confirm_stage(stage_combo.currentText())
        )

        layout.addWidget(label)
        layout.addWidget(stage_combo)
        layout.addStretch()
        layout.addWidget(confirm_btn)
        return bar

    def _confirm_stage(self, stage_text):
        self.workflow_state["stage_done"] = True
        self.workflow_state["selected_stage"] = stage_text
        self.log_pipeline(f"Stage confirmed: {stage_text}")
        QMessageBox.information(self, "Stage confirmed", f"Stage set to {stage_text}.")

    def _go_next_from_stage(self):
        """Guard for Stage -> Align: must have confirmed a stage."""
        if not self.workflow_state["stage_done"]:
            QMessageBox.warning(
                self,
                "Stage required",
                "Please select and confirm a stage before proceeding to Alignment.",
            )
            return
        self.navigate_to(self.align)

        '''

    # ------------------------------------------------------------------
    # Side Panel Methods
    # ------------------------------------------------------------------
    def _build_side_panel(self):
        """Build the collapsible right-side panel."""
        panel = QWidget()
        panel.setFixedWidth(260)
        panel.setStyleSheet("background-color: #1E1E1E;")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #1E1E1E; }
            QScrollBar:vertical { border: none; background: #2A2A2A; width: 10px; margin: 0px; }
            QScrollBar::handle:vertical { background: #41B3A2; border-radius: 5px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #5FBF9F; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)

        # Visualizer section
        self.visualizer_content = QWidget()
        outer_viz_layout = QVBoxLayout(self.visualizer_content)
        outer_viz_layout.setContentsMargins(10, 6, 10, 10)
        outer_viz_layout.setSpacing(6)

        self.visualizer_list = QVBoxLayout()
        outer_viz_layout.addLayout(self.visualizer_list)

        viz_dynamic_container = QWidget()
        self.viz_sections_layout = QVBoxLayout(viz_dynamic_container)
        self.viz_sections_layout.setContentsMargins(0, 0, 0, 0)
        self.viz_sections_layout.setSpacing(2)
        outer_viz_layout.addWidget(viz_dynamic_container)

        scroll_layout.addWidget(
            create_collapsible_section(
                "Visualizer", self.visualizer_content, expanded=True
            )
        )

        self._current_viz_section_widgets = {}
        for viz_name in self.active_viz_sections:
            vsection = self._build_viz_section(viz_name)
            self.viz_sections_layout.addWidget(vsection)
            self._current_viz_section_widgets[viz_name] = vsection

        # Pipeline section
        pipeline_content = QWidget()
        pipeline_layout = QVBoxLayout(pipeline_content)
        pipeline_layout.setContentsMargins(10, 6, 10, 10)

        self.pipeline_log_widget = QLabel(
            "\n".join(self.pipeline_log[-10:])
            if self.pipeline_log
            else "pipeline.log was automatically generated. \nNo actions yet."
        )
        self.pipeline_log_widget.setWordWrap(True)
        self.pipeline_log_widget.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        pipeline_layout.addWidget(self.pipeline_log_widget)

        scroll_layout.addWidget(
            create_collapsible_section("Pipeline", pipeline_content, expanded=True)
        )

        # Dynamic sections
        dynamic_container = QWidget()
        self.dynamic_sections_layout = QVBoxLayout(dynamic_container)
        self.dynamic_sections_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_sections_layout.setSpacing(2)
        scroll_layout.addWidget(dynamic_container)

        self._current_section_widgets = {}
        for category in self.active_categories:
            section = self._build_category_section(category)
            self.dynamic_sections_layout.addWidget(section)
            self._current_section_widgets[category] = section

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

        self._refresh_visualizer_list()
        return panel

    def _execute_clean(self, channel_name):
        """Simulate the clean step for screen-navigation testing."""

        QMessageBox.information(
            self,
            "Clean (simulated)",
            f"Clean step simulated for channel '{channel_name}'. No file was modified.",
        )
        self.log_pipeline(f"[simulated] Clean run on channel {channel_name}")

        self.workflow_state["clean_done"] = True
        self.workflow_state["last_cleaned_channel"] = channel_name

        # Real implementation (needs real experiment volume files) ----
        if not hasattr(self, "filepath") or not self.filepath:
            QMessageBox.warning(
                self, "No experiment", "Please select an experiment first."
            )
            return
        try:
            exp_data = self.experiment_metadata.get(self.filepath)
            if not exp_data:
                QMessageBox.warning(self, "Error", "Experiment data not found.")
                return
            clean_params_ui = self.param_values.get("Clean", {})
            params = CleanParams(
                v0=clean_params_ui.get("v0", 100),
                v1=clean_params_ui.get("v1", 400),
                low_res_size=clean_params_ui.get("low_res_size", 256),
                gaussian_sigma=clean_params_ui.get("gaussian_sigma", 1.5),
                frequency_cutoff=clean_params_ui.get("frequency_cutoff", 0.3),
            )
            raw_volume_path = Path(exp_data.get("path", ""))
            if not raw_volume_path.exists():
                file_path, _ = QFileDialog.getOpenFileName(
                    parent=self,
                    caption="Select raw volume file",
                    directory=os.getcwd(),
                    filter="Volume files (*.vti *.nii *.nii.gz *.tif *.tiff)",
                )
                if not file_path:
                    return
            raw_volume_path = Path(file_path)
            result_channel = clean(
                experiment=exp_data,
                raw_volume_path=raw_volume_path,
                channel_name=channel_name,
                params=params,
            )
            QMessageBox.information(
                self,
                "Success",
                f"Cleaned volume saved for channel {channel_name}\nPath: {result_channel.path}",
            )
            self.log_pipeline(f"Volume cleaned successfully for channel {channel_name}")
            self.workflow_state["clean_done"] = True
            self.workflow_state["last_cleaned_channel"] = channel_name
        except Exception as e:
            QMessageBox.critical(
                self, "Clean Error", f"Failed to clean volume: {str(e)}"
            )
            self.log_pipeline(f"Clean error: {str(e)}")

    def _refresh_visualizer_list(self):
        """Refresh the visualizer experiment list."""
        while self.visualizer_list.count():
            item = self.visualizer_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        if not self.experiments:
            empty_label = QLabel("No experiments loaded")
            empty_label.setStyleSheet("color: #666666; font-size: 12px;")
            self.visualizer_list.addWidget(empty_label)
            return

        for path in self.experiments:
            name = self.experiment_names.get(path, os.path.basename(path))
            row = QLabel(f"• {name}")
            row.setStyleSheet("color: #ffffff; font-size: 13px; padding: 2px 0px;")
            self.visualizer_list.addWidget(row)

    def _clear_layout(self, layout):
        """Recursively clear a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # ------------------------------------------------------------------
    # Category and Viz Section Builders
    # ------------------------------------------------------------------
    def add_category_section(self, category):
        """Add a category section to the side panel."""
        if category not in self.active_categories:
            self.active_categories.append(category)
            self.log_pipeline(f"{category} parameters added.")

        if not hasattr(self, "dynamic_sections_layout"):
            return

        if category in getattr(self, "_current_section_widgets", {}):
            return

        section = self._build_category_section(category)
        self.dynamic_sections_layout.addWidget(section)
        self._current_section_widgets[category] = section

    def _build_category_section(self, category):
        """Build a category section from CATEGORY_PARAMS."""
        params = CATEGORY_PARAMS.get(category, [])
        stored = self.param_values.setdefault(category, {})

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 8, 12, 12)
        content_layout.setSpacing(8)

        param_builders = {
            "slider": self._add_slider_param,
            "spinbox": self._add_spinbox_param,
            "aer_line": self._add_aer_line_param,
            "limb_reference": self._add_limb_reference_param,
        }

        text_index = 0
        for param in params:
            if param.get("type") == "text":
                label_text = param.get("default", "")
                is_bold = category == "Stage" and text_index > 0
                style = (
                    "color: #ffffff; font-size: 13px; font-weight: bold; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
                    if is_bold
                    else "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
                )
                info_label = create_label(label_text, style, Qt.AlignmentFlag.AlignLeft)
                info_label.setWordWrap(True)
                content_layout.addWidget(info_label)
                text_index += 1
            else:
                builder = param_builders.get(param.get("type", "slider"))
                if builder:
                    builder(content_layout, category, param, stored)

        return create_collapsible_section(category, content, expanded=True)

    def add_viz_section(self, viz_name):
        """Add a visualization section to the side panel."""
        if viz_name not in self.active_viz_sections:
            self.active_viz_sections.append(viz_name)
            self.log_pipeline(f"{viz_name} visualization parameters added.")

        if not hasattr(self, "viz_sections_layout"):
            return

        if viz_name in getattr(self, "_current_viz_section_widgets", {}):
            return

        section = self._build_viz_section(viz_name)
        self.viz_sections_layout.addWidget(section)
        self._current_viz_section_widgets[viz_name] = section

    def _build_viz_section(self, viz_name):
        """Build a visualization section from VIZ_PARAMS."""
        params = VIZ_PARAMS.get(viz_name, [])
        stored = self.param_values.setdefault(viz_name, {})

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 8, 12, 12)
        content_layout.setSpacing(8)

        param_builders = {
            "slider": self._add_slider_param,
            "spinbox": self._add_spinbox_param,
            "probe_line": self._add_probe_line_param, # type: ignore
        }

        for param in params:
            if param.get("type") == "text":
                is_bold = viz_name == "2D Projection Slab"
                style = (
                    "color: #ffffff; font-size: 13px; font-weight: bold; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
                    if is_bold
                    else "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
                )
                info_label = create_label(
                    param.get("default", ""), style, Qt.AlignmentFlag.AlignLeft
                )
                info_label.setWordWrap(True)
                content_layout.addWidget(info_label)
            else:
                builder = param_builders.get(param.get("type", "slider"))
                if builder:
                    builder(content_layout, viz_name, param, stored)

        self._show_genes_viz(content_layout, viz_name)
        return create_collapsible_section(viz_name, content, expanded=False)

    def _show_genes_viz(self, layout, viz_name):
        """Show gene channel checkboxes for a visualization mode."""
        channels_label = create_label(
            "Channels overlaid",
            "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;",
        )
        layout.addWidget(channels_label)

        colors = ["#41B3A2", "#54278F", "#756BB1"]
        stored_channels = self.param_values.setdefault(viz_name, {}).setdefault(
            "channels", {}
        )

        for gene, color in zip(self.check_genes_viz, colors):
            checkbox = QCheckBox(gene)
            checkbox.setChecked(stored_channels.get(gene, False))
            stored_channels[gene] = checkbox.isChecked()

            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: #ffffff; font-size: 12px; spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 16px; height: 16px; border-radius: 4px;
                    border: 1px solid {color}; background-color: #2A2A2A;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color}; border: 1px solid {color};
                }}
                QCheckBox::indicator:hover {{ border: 1px solid #ffffff; }}
            """)

            checkbox.stateChanged.connect(
                lambda state, v=viz_name, g=gene: self._on_gene_channel_changed(
                    v, g, state
                )
            )
            layout.addWidget(checkbox)

    def _on_gene_channel_changed(self, viz_name, gene, state):
        """Handle gene channel checkbox changes."""
        checked = bool(state)
        self.param_values.setdefault(viz_name, {}).setdefault("channels", {})[gene] = (
            checked
        )
        self.log_pipeline(f"{viz_name} - {gene} channel: {'on' if checked else 'off'}")

        refresh_callbacks = getattr(self, "_probe_refresh_callbacks", {})
        if viz_name in refresh_callbacks:
            refresh_callbacks[viz_name]()

    # ------------------------------------------------------------------
    # Parameter Builders
    # ------------------------------------------------------------------
    def _add_slider_param(self, layout, category, param, stored):
        """Add a slider parameter row."""
        name = param["name"]
        current_value = stored.get(name, param["default"])
        stored[name] = current_value

        row_label = create_label(name, "color: #ffffff; font-size: 12px;")
        slider = create_slider(param["min"], param["max"], current_value)

        value_label = QLabel(str(current_value))
        value_label.setStyleSheet("color: #A0A0A0; font-size: 11px;")

        slider.valueChanged.connect(
            lambda val, cat=category, pname=name, vlabel=value_label: (
                self._on_param_changed(cat, pname, val, vlabel)
            )
        )

        layout.addWidget(row_label)
        layout.addWidget(slider)
        layout.addWidget(value_label)

    def _add_spinbox_param(self, layout, category, param, stored):
        """Add a spinbox parameter row."""
        name = param["name"]
        current_value = stored.get(name, param["default"])
        stored[name] = current_value

        row_label = create_label(name, "color: #ffffff; font-size: 12px;")

        spinbox = QSpinBox()
        spinbox.setMinimum(param["min"])
        spinbox.setMaximum(param["max"])
        spinbox.setValue(current_value)
        spinbox.setStyleSheet("""
            QSpinBox {
                color: #ffffff; background-color: #2A2A2A;
                border: 1px solid #41B3A2; border-radius: 4px; padding: 2px 4px;
            }
        """)

        spinbox.valueChanged.connect(
            lambda val, cat=category, pname=name: self._on_param_changed(
                cat, pname, val, None
            )
        )

        layout.addWidget(row_label)
        layout.addWidget(spinbox)

    def _on_param_changed(self, category, param_name, value, value_label):
        """Handle parameter changes."""
        if value_label is not None:
            value_label.setText(str(value))
        self.param_values.setdefault(category, {})[param_name] = value
        self.log_pipeline(f"{category} - {param_name}: {value}")

    def _add_aer_line_param(self, layout, category, param, stored):
        """Add AER selection controls."""
        info = create_label(
            "Click points on the 3D limb to mark the AER line.",
            "color: #A0A0A0; font-size: 11px;",
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        start_btn = create_styled_button("Select AER", "#0D7C66", "#41B3A2")
        clear_btn = create_styled_button("Clear", "#2A2A2A", "#41B3A2")
        confirm_btn = create_styled_button("✓", "#41B3A2", "#5FBF9F")
        confirm_btn.setFixedWidth(36)

        btn_row.addWidget(start_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

        plot = pg.PlotWidget()
        plot.setBackground("#181818")
        plot.setFixedHeight(160)
        plot.showGrid(x=True, y=True, alpha=0.2)
        curve = plot.plot(
            [],
            [],
            pen=pg.mkPen("#F2A93B", width=2),
            symbol="o",
            symbolBrush="#E34A4A",
            symbolSize=6,
        )
        layout.addWidget(plot)

        def update_plot(points):
            if not points:
                curve.setData([], [])
                return
            pts = np.array(points)
            curve.setData(pts[:, 0], pts[:, 2])

        confirm_btn.clicked.connect(self._confirm_aer_selection) # type: ignore

    ''''
    def _confirm_aer_selection(self):
        """Confirm AER selection."""
        
        if not points:
            QMessageBox.warning(self, "No AER selected", "Please click points on the limb first.")
            return

        reply = QMessageBox.question(
            self, "Confirm AER selection",
            f"The following AER will be selected ({len(points)} points).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.viewer.aer_selector.stop()
            self.log_pipeline(f"AER confirmed with {len(points)} points.")

    def _add_probe_line_param(self, layout, viz_name, param, stored):
        """Add probe line selection controls."""
        btn_row = QHBoxLayout()
        draw_btn = create_styled_button("Draw line", "#0D7C66", "#41B3A2")
        clear_btn = create_styled_button("Clear", "#2A2A2A", "#41B3A2")

        btn_row.addWidget(draw_btn)
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)

        plot = pg.PlotWidget()
        plot.setBackground("#181818")
        plot.setFixedHeight(160)
        plot.showGrid(x=True, y=True, alpha=0.2)
        plot.setLabel('bottom', 'Position along line')
        plot.setLabel('left', 'Intensity')
        layout.addWidget(plot)

        empty_msg = create_label("", "color: #E34A4A; font-size: 11px; font-style: italic;")
        empty_msg.setWordWrap(True)
        empty_msg.setVisible(False)
        layout.addWidget(empty_msg)

        gene_colors = {'Hoxa11': '#41B3A2', 'Sox9': '#54278F', 'BMP2': '#756BB1'}

        def refresh_histogram():
            plot.clear()
            points = self.viewer.probe_selector.points
            channels = self.param_values.setdefault(viz_name, {}).setdefault("channels", {})
            active_genes = [g for g, checked in channels.items() if checked]

            if len(points) < 2:
                empty_msg.setVisible(False)
                return

            if not active_genes:
                empty_msg.setText("Display at least one gene channel to see its intensity along this line.")
                empty_msg.setVisible(True)
                return

            empty_msg.setVisible(False)
            n_samples = 50
            x_axis = np.linspace(0, 1, n_samples)
            for gene in active_genes:
                rng = np.random.default_rng(abs(hash((viz_name, gene))) % (2**32))
                profile = np.abs(np.sin(x_axis * np.pi * rng.uniform(0.8, 1.4))) * rng.uniform(0.6, 1.0)
                profile += rng.normal(0, 0.03, n_samples)
                color = gene_colors.get(gene, "#F2A93B")
                plot.plot(x_axis, profile, pen=pg.mkPen(color, width=2), name=gene)

        draw_btn.clicked.connect(self.viewer.probe_selector.start)
        clear_btn.clicked.connect(self.viewer.probe_selector.clear)

        self.viewer.probe_selector.points_changed.connect(lambda pts: refresh_histogram())

        self._probe_refresh_callbacks = getattr(self, '_probe_refresh_callbacks', {})
        self._probe_refresh_callbacks[viz_name] = refresh_histogram
    '''

    def _add_limb_reference_param(self, layout, category, param, stored):
        """Add limb reference alignment controls."""
        stored.setdefault("reference_choice", None)
        stored.setdefault("apply_all_channels", False)
        stored.setdefault("show_reference", False)

        ref_label = create_label(
            "Chosen stage reference",
            "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;",
        )
        layout.addWidget(ref_label)

        reference_combo = QComboBox()
        reference_options = [
            "Stage 20 - E10.5 reference",
            "Stage 22 - E11.5 reference",
            "Stage 24 - E12.5 reference",
            "Stage 26 - E13.5 reference",
        ]
        reference_combo.addItems(reference_options)
        if stored["reference_choice"] in reference_options:
            reference_combo.setCurrentText(stored["reference_choice"])
        else:
            stored["reference_choice"] = reference_combo.currentText()

        reference_combo.setStyleSheet("""
            QComboBox { color: #ffffff; background-color: #2A2A2A; border: 1px solid #41B3A2; border-radius: 6px; padding: 4px 8px; font-size: 12px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #2A2A2A; color: #ffffff; selection-background-color: #41B3A2; }
        """)
        reference_combo.currentTextChanged.connect(
            lambda text, cat=category: self._on_reference_changed(cat, text)
        )
        layout.addWidget(reference_combo)

        apply_all_btn = QPushButton("Apply to all channels")
        apply_all_btn.setCheckable(True)
        apply_all_btn.setChecked(stored["apply_all_channels"])

        def style_apply_btn(checked):
            bg = "#0D7C66" if checked else "#2A2A2A"
            apply_all_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg}; color: white; font-weight: bold; font-size: 12px;
                    border-radius: 10px; padding: 8px 10px;
                }}
                QPushButton:hover {{ background-color: #9CCC65; }}
            """)

        style_apply_btn(apply_all_btn.isChecked())
        apply_all_btn.toggled.connect(
            lambda checked, cat=category: self._on_apply_all_toggled(
                cat, checked, style_apply_btn
            )
        )
        layout.addWidget(apply_all_btn)

        reset_btn = create_styled_button("Reset", "#4B2E83", "#5C3A9E")
        reset_btn.clicked.connect(
            lambda: self._reset_reference_alignment(
                category, reference_combo, apply_all_btn, style_apply_btn
            )
        )
        layout.addWidget(reset_btn)

        bottom_row = QHBoxLayout()
        show_ref_checkbox = QCheckBox("Show reference in limb visualization")
        show_ref_checkbox.setChecked(stored["show_reference"])
        show_ref_checkbox.setStyleSheet("""
            QCheckBox { color: #ffffff; font-size: 12px; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #41B3A2; background-color: #2A2A2A; }
            QCheckBox::indicator:checked { background-color: #41B3A2; border: 1px solid #41B3A2; }
            QCheckBox::indicator:hover { border: 1px solid #ffffff; }
        """)
        show_ref_checkbox.stateChanged.connect(
            lambda state, cat=category: self._on_show_reference_toggled(cat, state)
        )

        confirm_btn = create_styled_button("✓", "#41B3A2", "#5FBF9F")
        confirm_btn.setFixedWidth(36)
        confirm_btn.clicked.connect(lambda: self._confirm_reference_alignment(category))

        bottom_row.addWidget(show_ref_checkbox)
        bottom_row.addWidget(confirm_btn)
        layout.addLayout(bottom_row)

    def _on_reference_changed(self, category, text):
        self.param_values.setdefault(category, {})["reference_choice"] = text
        self.log_pipeline(f"{category} - reference set to: {text}")

    def _on_apply_all_toggled(self, category, checked, style_fn):
        self.param_values.setdefault(category, {})["apply_all_channels"] = checked
        style_fn(checked)
        self.log_pipeline(
            f"{category} - apply to all channels: {'on' if checked else 'off'}"
        )

    def _on_show_reference_toggled(self, category, state):
        checked = bool(state)
        self.param_values.setdefault(category, {})["show_reference"] = checked
        self.log_pipeline(
            f"{category} - show reference in viz: {'on' if checked else 'off'}"
        )

    def _reset_reference_alignment(self, category, combo, apply_btn, style_fn):
        combo.setCurrentIndex(0)
        apply_btn.setChecked(False)
        style_fn(False)
        stored = self.param_values.setdefault(category, {})
        stored["reference_choice"] = combo.currentText()
        stored["apply_all_channels"] = False
        self.log_pipeline(f"{category} - reference alignment reset.")

    def _confirm_reference_alignment(self, category):
        stored = self.param_values.get(category, {})
        reference = stored.get("reference_choice", "None")

        reply = QMessageBox.question(
            self,
            "Confirm alignment",
            f"Confirm manual alignment with reference '{reference}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.log_pipeline(
                f"{category} - alignment confirmed against '{reference}'."
            )
            # If this reference-alignment section happens to live under the
            # Align category, treat it as satisfying the Align step's guard too.
            if category == "Align":
                self.workflow_state["align_done"] = True
                self.workflow_state["alignment_method"] = reference

    def _load_experiments_from_db(self):
        """Load all experiments from the database."""
        try:
            # Get list of experiment IDs from database
            exp_ids = list_experiments(self.db_path)
            self.experiments = exp_ids

            # Load metadata for each experiment
            self.experiment_metadata = {}
            self.experiment_names = {}

            for exp_id in exp_ids:
                exp_data = get_experiment(self.db_path, exp_id)
                if exp_data:
                    # jsut for TESTING
                    print(f"📊 Loaded: {exp_id}")  # DEBUG
                    # Store full experiment data
                    self.experiment_metadata[exp_id] = exp_data
                    # Set display name
                    self.experiment_names[exp_id] = exp_id

            print(f"📂 Loaded {len(self.experiments)} experiments from database")

        except Exception as e:
            print(f"⚠️ Error loading experiments: {e}")
            self.experiments = []
            self.experiment_metadata = {}

    # ------------------------------------------------------------------
    # Button Actions
    # ------------------------------------------------------------------
    def _create_left_button(self):
        """Create the left menu button with dropdown."""
        button = QToolButton()
        button.setIcon(QIcon("left_icon.png"))
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)

        home = QAction("Home", self)
        home.triggered.connect(lambda: self.navigate_to(self.show_home))
        menu.addAction(home)

        menu.addSeparator()
        self._build_resources_menu(menu)

        about = QAction("About us", self)
        about.triggered.connect(
            lambda: webbrowser.open("https://www.embl.org/groups/sharpe/")
        )
        menu.addAction(about)

        self._build_contact_menu(menu)

        button.setMenu(menu)
        return button

    def _click_threebuttons(self, path, button):
        """Handle three-dots button click for experiment actions."""
        menu = QMenu(self)
        menu.setStyleSheet(SECMENU_STYLE)

        # connect with database functions
        delete_act = QAction("Delete")
        # database function
        delete_act.triggered.connect(lambda: self._delete_experiment(path))
        menu.addAction(delete_act)

        rename_act = QAction("Rename")
        rename_act.triggered.connect(lambda: self._rename_experiment(path))
        menu.addAction(rename_act)

        details_act = QAction("Details")
        details_act.triggered.connect(lambda: self.menu_button_clicked)
        menu.addAction(details_act)

        download_act = QAction("Download .tiff")
        download_act.triggered.connect(lambda: self.menu_button_clicked)
        menu.addAction(download_act)

        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    # DETELE, already defined database function

    def _rename_experiment(self, path):
        """Rename an experiment."""
        current_name = self.experiment_names.get(path, os.path.basename(path))
        new_name, ok = QInputDialog.getText(
            self, "Rename experiment", "New name:", text=current_name
        )
        if ok and new_name.strip():
            self.experiment_names[path] = new_name.strip()
            self.show_exp()

    # DELETE FUNCTION CALLS DATABASE DELETE FUNCTION, AUXILIAR UI
    def _delete_experiment(self, experiment_id):
        """Delete an experiment from the database."""
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Delete Experiment",
            f"Are you sure you want to delete experiment '{experiment_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 🔥 Call the imported delete_experiment with correct parameters
            success = delete_experiment(self.db_path, experiment_id)

            if success:
                # Remove from local lists
                if experiment_id in self.experiments:
                    self.experiments.remove(experiment_id)
                if experiment_id in self.experiment_names:
                    del self.experiment_names[experiment_id]
                if experiment_id in self.experiment_metadata:
                    del self.experiment_metadata[experiment_id]

                # Refresh the UI
                self.show_exp()
                QMessageBox.information(
                    self, "Success", f"Deleted experiment: {experiment_id}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Experiment '{experiment_id}' not found in database.",
                )


    def create_new_experiment(self):
        """Create a new experiment from any TIF volume (DAPI or gene channel)."""
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select TIF volume file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti *.nii *.nii.gz)'
        )
        if not filepath:
            return

        if not filepath.lower().endswith((".tif", ".tiff", ".vti", ".nii", ".nii.gz")):
            QMessageBox.warning(self, "Invalid file", "Please select a valid volume file.")
            return

        # Ask for limb info and channel type
        limb_info = self.ask_limbinfo()
        if not limb_info:
            return

        try:
            exp_id = os.path.basename(filepath).split('.')[0]

            # Check if experiment already exists
            if exp_id in self.experiments:
                reply = QMessageBox.question(
                    self,
                    "Experiment Exists",
                    f"Experiment '{exp_id}' already exists.\n"
                    "Do you want to add this channel to it instead?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._add_channel_to_existing(exp_id)
                return

            # Get channel type
            channel_name = limb_info['channel_type']
            
            # Set default isovalues based on channel type
            if channel_name == "DAPI":
                v0, v1 = 238.0, 463.0
            else:  # Gene channels
                v0, v1 = 174.0, 335.0

            # Create experiment
            new_exp = Experiment(
                experiment_id=exp_id,
                base=os.path.dirname(filepath),
                spacing_x=limb_info['spacing'][0], # type: ignore
                spacing_y=limb_info['spacing'][1], # type: ignore
                spacing_z=limb_info['spacing'][2], # type: ignore
                side=limb_info['side'],
                position=limb_info['position'],
                channels=[
                    Channel(
                        experiment_id=exp_id,
                        channel_name=channel_name,
                        path=os.path.basename(filepath),
                        v0=v0,
                        v1=v1
                    )
                ]
            )

            save_experiment(self.db_path, new_exp)
            self._load_experiments_from_db()
            self.navigate_to(self.show_exp)

            # Show success message with next steps
            next_steps = "Add more gene channels using the 'Add Channel' button."
            if channel_name == "DAPI":
                next_steps = "Add gene channels (Hoxa11, Sox9, BMP2, SHH) using the 'Add Channel' button."
            else:
                next_steps = "Add DAPI and other gene channels using the 'Add Channel' button."

            QMessageBox.information(
                self,
                "Success",
                f"✅ Experiment created: {exp_id}\n"
                f"📁 File: {os.path.basename(filepath)}\n"
                f"📊 Channel: {channel_name}\n\n"
                f"💡 {next_steps}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create experiment: {e}")
            import traceback
            traceback.print_exc()




    def add_channel_to_existing(self, specific_exp_id=None):
        """Add a channel to an existing experiment."""
        # If no specific experiment provided, let user choose
        if not specific_exp_id:
            if not self.experiments:
                QMessageBox.warning(
                    self, 
                    "No experiments", 
                    "No existing experiments found.\n\n"
                    "Please create a new experiment first using the 'Upload TIF Volume' button."
                )
                return
            
            # Ask which experiment to add channel to
            exp_id, ok = QInputDialog.getItem(
                self,
                "Select Experiment",
                "Select experiment to add channel to:",
                self.experiments,
                0,
                False
            )
            
            if not ok or not exp_id:
                return
        else:
            exp_id = specific_exp_id
        
        # Get experiment data
        exp_data = self.experiment_metadata.get(exp_id)
        if not exp_data:
            QMessageBox.warning(self, "Error", "Experiment not found.")
            return
        
        # Show current channels
        current_channels = [ch.get('channel_name', '') for ch in exp_data.get('channels', [])]
        channel_info = f"Current channels: {', '.join(current_channels) if current_channels else 'None'}"
        
        # Get the file
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select gene channel TIF file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti *.nii *.nii.gz)'
        )
        if not filepath:
            return
        
        if not filepath.lower().endswith((".tif", ".tiff", ".vti", ".nii", ".nii.gz")):
            QMessageBox.warning(self, "Invalid file", "Please select a valid volume file.")
            return
        
        # Ask for channel type (only gene channels for adding)
        channel_type, ok = QInputDialog.getItem(
            self,
            "Channel Type",
            f"Select channel type to add:\n\n{channel_info}",
            ["Hoxa11", "Sox9", "BMP2", "SHH"],
            0,
            False
        )
        
        if not ok or not channel_type:
            return
        
        try:
            # Check if channel already exists
            for channel in exp_data.get('channels', []):
                if channel.get('channel_name', '').upper() == channel_type.upper():
                    QMessageBox.warning(
                        self,
                        "Duplicate Channel",
                        f"Channel '{channel_type}' already exists in this experiment.\n"
                        f"{channel_info}"
                    )
                    return
            
            # Add new channel (gene channel defaults)
            new_channel = {
                'experiment_id': exp_id,
                'channel_name': channel_type,
                'path': os.path.basename(filepath),
                'v0': 174.0,
                'v1': 335.0
            }
            
            exp_data['channels'].append(new_channel)
            
            # Recreate experiment object
            experiment_obj = Experiment(
                experiment_id=exp_id,
                base=exp_data['base'],
                spacing_x=exp_data.get('spacing_x', 0.65),
                spacing_y=exp_data.get('spacing_y', 0.65),
                spacing_z=exp_data.get('spacing_z', 2.0),
                side=exp_data.get('side', 'L'),
                position=exp_data.get('position', 'H'),
                channels=exp_data['channels']
            )
            
            # Save to database
            save_experiment(self.db_path, experiment_obj)
            
            # Reload and refresh
            self._load_experiments_from_db()
            self.show_exp()
            
            # Check if experiment is now complete
            is_valid, status = self._validate_experiment_channels(exp_id)
            
            if is_valid:
                QMessageBox.information(
                    self,
                    "Success",
                    f"✅ Added {channel_type} channel to experiment: {exp_id}\n"
                    f"📁 File: {os.path.basename(filepath)}\n\n"
                    f"🎉 Experiment is now complete!\n"
                    f"Channels: {', '.join([ch.get('channel_name', '') for ch in exp_data['channels']])}\n\n"
                    f"You can now visualize this experiment."
                )
            else:
                QMessageBox.information(
                    self,
                    "Success",
                    f"✅ Added {channel_type} channel to experiment: {exp_id}\n"
                    f"📁 File: {os.path.basename(filepath)}\n\n"
                    f"⚠️ Experiment is still incomplete:\n{status}\n\n"
                    f"Current channels: {', '.join([ch.get('channel_name', '') for ch in exp_data['channels']])}"
                )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add channel: {e}")
            import traceback
            traceback.print_exc()




    def ask_limbinfo(self, channel_only=False):
        """Popup dialog asking for limb side, position, spacing, and channel type."""
        dialog = QDialog()
        dialog.setWindowTitle("Limb Options" if not channel_only else "Channel Type")
        dialog.setModal(True)
        dialog.setFixedWidth(350)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ---- Limb Side ----
        if not channel_only:
            side_layout = QHBoxLayout()
            side_label = QLabel("Limb Side:")
            side_label.setFixedWidth(100)
            side_combo = QComboBox()
            side_combo.addItems(["L", "R"])
            side_combo.setCurrentIndex(0)
            side_layout.addWidget(side_label)
            side_layout.addWidget(side_combo)
            layout.addLayout(side_layout)


            # ---- Position ----
            position_layout = QHBoxLayout()
            position_label = QLabel("Position:")
            position_label.setFixedWidth(100)
            position_combo = QComboBox()
            position_combo.addItems(["F", "H"])
            position_combo.setCurrentIndex(0)
            position_layout.addWidget(position_label)
            position_layout.addWidget(position_combo)
            layout.addLayout(position_layout)

            # ---- Spacing ----
            spacing_group = QGroupBox("Spacing")
            spacing_layout = QVBoxLayout(spacing_group)

            # X spacing
            x_layout = QHBoxLayout()
            x_label = QLabel("X:")
            x_label.setFixedWidth(30)
            x_spin = QDoubleSpinBox()
            x_spin.setRange(0.01, 10.0)
            x_spin.setSingleStep(0.01)
            x_spin.setValue(0.65)
            x_spin.setDecimals(2)
            x_layout.addWidget(x_label)
            x_layout.addWidget(x_spin)
            spacing_layout.addLayout(x_layout)

            # Y spacing
            y_layout = QHBoxLayout()
            y_label = QLabel("Y:")
            y_label.setFixedWidth(30)
            y_spin = QDoubleSpinBox()
            y_spin.setRange(0.01, 10.0)
            y_spin.setSingleStep(0.01)
            y_spin.setValue(0.65)
            y_spin.setDecimals(2)
            y_layout.addWidget(y_label)
            y_layout.addWidget(y_spin)
            spacing_layout.addLayout(y_layout)

            # Z spacing
            z_layout = QHBoxLayout()
            z_label = QLabel("Z:")
            z_label.setFixedWidth(30)
            z_spin = QDoubleSpinBox()
            z_spin.setRange(0.01, 10.0)
            z_spin.setSingleStep(0.01)
            z_spin.setValue(2.0)
            z_spin.setDecimals(2)
            z_layout.addWidget(z_label)
            z_layout.addWidget(z_spin)
            spacing_layout.addLayout(z_layout)

            layout.addWidget(spacing_group)

        # ---- Channel Type ----
        channel_layout = QHBoxLayout()
        channel_label = QLabel("Channel type:")
        channel_label.setFixedWidth(100)
        channel_combo = QComboBox()


        if channel_only:
            channel_combo.addItems(["Hoxa11", "Sox9", "BMP2"])
            channel_label.setText("Gene channel:")
        else:
            channel_combo.addItems(["DAPI", "Hoxa11", "Sox9", "BMP2"])



        #channel_combo.addItems(["DAPI", "Hoxa11", "Sox9", "BMP2", "SHH"])
        channel_combo.setCurrentIndex(0)
        channel_layout.addWidget(channel_label)  # FIXED: was position_label
        channel_layout.addWidget(channel_combo)  # FIXED: was position_combo
        layout.addLayout(channel_layout)

        # ---- Buttons ----
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancel_button")
        cancel_button.clicked.connect(dialog.reject)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        # Show dialog and get result
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            if channel_only:
                # Only return channel type
                return {
                    'channel_type': channel_combo.currentText()
                }
            else:
                # Return all info
                side = side_combo.currentText()
                position = position_combo.currentText()
                spacing = (x_spin.value(), y_spin.value(), z_spin.value())
                channel_type = channel_combo.currentText()

                return {
                    'side': side,
                    'position': position,
                    'spacing': spacing,
                    'channel_type': channel_type
                }
        else:
            return None


    def addexp_button_clicked(self, checked=False):
        """Add experiment button handler - creates new experiment or adds channel to existing."""
        # First, check if we have existing experiments
        if self.experiments:
            # Ask user if they want to create new experiment or add to existing
            reply = QMessageBox.question(
                self,
                "Add to Existing?",
                "Do you want to add this channel to an existing experiment?\n"
                "• Yes: Add channel to existing experiment\n"
                "• No: Create new experiment",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                # Add to existing experiment
                self._add_channel_to_existing()
                return
            # else: No - create new experiment (continue below)
        
        # Create new experiment (Original flow)
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select .tiff file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti)'
        )
        if not filepath:
            return

        if not filepath.lower().endswith((".tif", ".tiff", ".vti")):
            QMessageBox.warning(
                self, "Invalid file", "Please select a valid volume file."
            )
            return

        limb_info = self.ask_limbinfo()
        if not limb_info:
            return  # User cancelled

        # Create new experiment from file
        try:
            exp_id = os.path.basename(filepath).split(".")[0]

            # Check if experiment already exists
            if exp_id in self.experiments:
                QMessageBox.warning(self, "Duplicate", f"Experiment '{exp_id}' already exists.")
                # Ask if they want to add channel to existing experiment instead
                reply = QMessageBox.question(
                    self,
                    "Add to Existing?",
                    f"Experiment '{exp_id}' already exists.\n"
                    "Do you want to add this channel to it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._add_channel_to_existing(exp_id)
                return

            # Get channel type from dialog
            channel_name = limb_info['channel_type']
            
            # Set default isovalues based on channel type
            if channel_name == "DAPI":
                v0, v1 = 238.0, 463.0
            else:  # Gene channels
                v0, v1 = 174.0, 335.0

            # Create a new experiment
            new_exp = Experiment(
                experiment_id=exp_id,
                base=os.path.dirname(filepath),
                spacing_x=limb_info["spacing"][0], # type: ignore
                spacing_y=limb_info["spacing"][1], # type: ignore
                spacing_z=limb_info["spacing"][2], # type: ignore
                side=limb_info["side"],
                position=limb_info["position"],
                channels=[
                    Channel(
                        experiment_id=exp_id,
                        channel_name=channel_name,
                        path=os.path.basename(filepath),
                        v0=v0,
                        v1=v1
                    )
                ]
            )

            save_experiment(self.db_path, new_exp)
            self._load_experiments_from_db()
            self.show_exp()

            QMessageBox.information(
                self, 
                "Success", 
                f"Successfully created experiment: {exp_id}\n"
                f"File: {os.path.basename(filepath)}\n"
                f"Channel: {channel_name}\n\n"
                f"Add more gene channels using the 'Add Channel' option."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add experiment: {e}")
            
            traceback.print_exc()

    def saveexp_button_clicked(self):
        """Save experiment button handler."""
        print(True)

    def viewexp_button_clicked(self):
        """View experiment button handler."""
        selected = [path for path, cb in self.experiment_checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(
                self,
                "No experiment selected",
                "Please select an experiment to visualize.",
            )
            return

        exp_id = selected[0]

        is_valid, message = self._validate_experiment_channels(exp_id)
    
        if not is_valid:
            QMessageBox.warning(self, "Incomplete Experiment", message)
            return
        
        # If valid, proceed to visualization
        self.filepath = exp_id
        
        # Reset workflow state for new experiment
        self.workflow_state = {
            "clean_done": False,
            "last_cleaned_channel": None,
            "surface_done": False,
            "stage_done": False,
            "selected_stage": None,
            "align_done": False,
            "alignment_method": None,
        }
        self.navigate_to(self.show_viz)


    def _add_channel_to_existing(self, specific_exp_id=None):
        """Add a channel to an existing experiment."""
        # If no specific experiment provided, let user choose
        if not specific_exp_id:
            if not self.experiments:
                QMessageBox.warning(self, "No experiments", "No existing experiments found.")
                return
            
            # Ask which experiment to add channel to
            exp_id, ok = QInputDialog.getItem(
                self,
                "Select Experiment",
                "Select experiment to add channel:",
                self.experiments,
                0,
                False
            )
            
            if not ok or not exp_id:
                return
        else:
            exp_id = specific_exp_id
        
        # Get the file
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select gene channel .tiff file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti)'
        )
        if not filepath:
            return
        
        if not filepath.lower().endswith((".tif", ".tiff", ".vti")):
            QMessageBox.warning(self, "Invalid file", "Please select a valid volume file.")
            return
        
        # Ask for channel type using the same limb info dialog
        limb_info = self.ask_limbinfo(channel_only=True)
        if not limb_info:
            return
        
        channel_name = limb_info['channel_type']
        
        try:
            # Get existing experiment data
            exp_data = self.experiment_metadata.get(exp_id)
            if not exp_data:
                QMessageBox.warning(self, "Error", "Experiment not found.")
                return
            
            # Check if channel already exists
            for channel in exp_data.get('channels', []):
                if channel.get('channel_name', '').upper() == channel_name.upper():
                    QMessageBox.warning(
                        self,
                        "Duplicate Channel",
                        f"Channel '{channel_name}' already exists in this experiment.\n"
                        f"Current channels: {', '.join([ch.get('channel_name', '') for ch in exp_data.get('channels', [])])}"
                    )
                    return
            
            # Set default isovalues based on channel type
            if channel_name == "DAPI":
                v0, v1 = 238.0, 463.0
            else:  # Gene channels
                v0, v1 = 174.0, 335.0
            
            # Add new channel
            new_channel = {
                'experiment_id': exp_id,
                'channel_name': channel_name,
                'path': os.path.basename(filepath),
                'v0': v0,
                'v1': v1
            }
            
            exp_data['channels'].append(new_channel)
            
            # Recreate experiment object
            experiment_obj = Experiment(
                experiment_id=exp_id,
                base=exp_data['base'],
                spacing_x=exp_data.get('spacing_x', 0.65),
                spacing_y=exp_data.get('spacing_y', 0.65),
                spacing_z=exp_data.get('spacing_z', 2.0),
                side=exp_data.get('side', 'L'),
                position=exp_data.get('position', 'H'),
                channels=exp_data['channels']
            )
            
            # Save to database
            save_experiment(self.db_path, experiment_obj)
            
            # Reload and refresh
            self._load_experiments_from_db()
            self.show_exp()
            
            QMessageBox.information(
                self,
                "Success",
                f"✅ Added {channel_name} channel to experiment: {exp_id}\n"
                f"📁 File: {os.path.basename(filepath)}\n\n"
                f"Current channels: {', '.join([ch.get('channel_name', '') for ch in exp_data['channels']])}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add channel: {e}")
            import traceback
            traceback.print_exc()



    def _validate_experiment_channels(self, exp_id):
        """Validate that experiment has DAPI and at least one gene channel."""
        # Get experiment data from database
        exp_data = self.experiment_metadata.get(exp_id)
        if not exp_data:
            return False, f"Experiment '{exp_id}' not found in database."
        
        # Get all channels
        channels = exp_data.get('channels', [])
        if not channels:
            return False, "No channels found in this experiment.\nPlease upload at least DAPI and one gene channel."
        
        # Check for DAPI channel
        has_dapi = False
        gene_channels = []
        
        # Gene channel names (case insensitive)
        gene_names = ['Hoxa11', 'Sox9', 'BMP2', 'SHH']
        
        for channel in channels:
            channel_name = channel.get('channel_name', '').upper()
            if channel_name == 'DAPI':
                has_dapi = True
            elif channel_name in [g.upper() for g in gene_names]:
                gene_channels.append(channel.get('channel_name'))
        
        # Build validation result
        if not has_dapi:
            return False, "Missing required DAPI channel.\n\nPlease upload a DAPI .tiff file first."
        
        if len(gene_channels) == 0:
            return False, "Missing gene channels.\n\nPlease upload at least one gene channel:\n- Hoxa11\n- Sox9\n- BMP2"
        
        # Success - has DAPI and at least one gene channel
        return True, f"Experiment has DAPI and {len(gene_channels)} gene channel(s): {', '.join(gene_channels)}"



    def menu_button_clicked(self, s):
        """Placeholder for menu button clicks."""
        print("click", s)

    def log_pipeline(self, message):
        """Add a message to the pipeline log."""
        self.pipeline_log.append(message)
        if hasattr(self, "pipeline_log_widget"):
            self.pipeline_log_widget.setText("\n".join(self.pipeline_log[-10:]))

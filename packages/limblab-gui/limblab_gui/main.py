# pyright: reportOptionalMemberAccess=false
# pyright: ignore[reportAttributeAccessIssue]

import math
import os
import traceback
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
from limblab.design_tokens import theme
from limblab.models import Channel, Experiment
from limblab.params import CleanParams
from Mixin.NavigationMixin import NavigationMixin
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPen,
)
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
from Controllers.clean_controller import CleanController
from Controllers.stage_controller import StageController
from Controllers.surface_controller import SurfaceController
from limblab import pick_isovalues, preview_volume


class AnimatedGradientWidget(QWidget):
    """A QWidget that paints an animated linear gradient background."""

    def __init__(self, parent=None, speed: float = 0.03):
        super().__init__(parent)
        self.phase = 0.0
        self.speed = speed
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(30)

    def _on_timer(self):
        self.phase += self.speed
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        cx = r.center().x()
        cy = r.center().y()
        dx = math.cos(self.phase) * r.width() / 2
        dy = math.sin(self.phase) * r.height() / 2

        grad = QLinearGradient(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
        c1 = QColor(theme("palette.primary", "#0D7C66"))
        c2 = QColor(theme("palette.secondary", "#8E7FD6"))
        c3 = QColor(theme("palette.accent", "#5FBF9F"))

        grad.setColorAt(0.0, c1)
        grad.setColorAt(0.5, c2)
        grad.setColorAt(1.0, c3)

        painter.fillRect(r, grad)
        painter.end()


class AnimatedGradientLabel(QLabel):
    """A QLabel that paints its text filled with an animated linear gradient."""

    def __init__(self, text: str = "", parent=None, speed: float = 0.03):
        super().__init__(text, parent)
        self.phase = 0.0
        self.speed = speed
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(30)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _on_timer(self):
        self.phase += self.speed
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        cx = r.center().x()
        cy = r.center().y()
        dx = math.cos(self.phase) * r.width() / 2
        dy = math.sin(self.phase) * r.height() / 2

        grad = QLinearGradient(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
        c1 = QColor(theme("palette.primary", "#0D7C66"))
        c2 = QColor(theme("palette.secondary", "#8E7FD6"))
        c3 = QColor(theme("palette.accent", "#5FBF9F"))
        grad.setColorAt(0.0, c1)
        grad.setColorAt(0.5, c2)
        grad.setColorAt(1.0, c3)

        pen = QPen(QBrush(grad), 0)
        painter.setPen(pen)

        # Apply themed font size if available
        font = self.font()
        try:
            size = int(theme("typography.fontSizeHero", 100))
        except Exception:
            size = 100
        font.setPointSize(size)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(r, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


#laura
#TEST_BASE_PATH = "/Users/laura/Desktop/Desktop-2026/sox9-fig-thesis"
#TEST_SURFACE_PATH = "HCR11_MEIS2_l1_dapi_488_LF_surface.vtk"

# #gemma
# TEST_SURFACE_PATH = "HCR12_HOXA11_l1_dapi_405_LF_surface.vtk"
# TEST_DAPI_FILENAME = "HCR12_HOXA11_l1_dapi_405_LF.vti" 

env = {}
with open("../../../.env") as f:
    for line in f:
        if line.startswith("#"): continue
        if line == " ": continue
        line = line.strip().split("=")
        if len(line) != 2: continue
        k, v = line
        env[k] = v

TEST_BASE_PATH = env["TEST_BASE_PATH"]
TEST_SURFACE_PATH = env["TEST_SURFACE_PATH"]
TEST_DAPI_FILENAME = env["TEST_DAPI_FILENAME"]


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
            v0 = 0,
            v1 = 54
        )
    ],
)


class MainWindow(QMainWindow, NavigationMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LimbLab")
        self.setStyleSheet(f"QMainWindow, QWidget {{ background-color: {theme('palette.background', '#141414')}; color: {theme('palette.textPrimary', '#FFFFFF')}; }}")
        self.setStatusBar(QStatusBar(self))

        ##########
        # DATABASE
        self.db_path = Path("experiments.db")

        #each time the app is loadde a new db is created TESTING!!!   
        init_db(self.db_path)  # Creates empty database with schema only
        print(f"Created empty database: {self.db_path}")

    
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
        

        
        self.surface = SurfaceController(self)
        self.clean = CleanController(self)
        self.align = AlignController(self)
        self.stage = StageController(self) 

        #self.current_experiment = experiment   # set when the user picks a real experiment
        self.current_experiment = None

        #self.navigate_to(lambda:self.surface.show(self.current_experiment))
        self.navigate_to(self.show_home)


    def reset_database(self):
        reply = QMessageBox.question(
            self, "Reset database",
            "This deletes all saved experiment records from the database.\n"
            "Volume files on disk are NOT deleted.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if self.db_path.exists():
            self.db_path.unlink()
        init_db(self.db_path)

        self.experiments = []
        self.experiment_metadata = {}
        self.experiment_names = {}
        self.current_experiment = None
        self.filepath = None

        self._load_experiments_from_db()
        self.show_exp()


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
            ('Reset database', None),
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
                if text == "Reset Database":
                    action.triggered.connect(self.reset_database)
                else:
                    action.triggered.connect(self.menu_button_clicked)
                file_menu.addAction(action)

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

        
        top_row.addStretch()

        if next_label and next_callback:
            next_btn = create_styled_button(next_label)
            next_btn.clicked.connect(next_callback)
            top_row.addWidget(next_btn)

        return top_row

    # NOTE: Laura build this. So if actually works for her. 
    def _build_workflow_container(
        self,
        next_label=None,
        next_callback=None,
        back_guard=None,
        action_widget=None,
        current_step=None,
    ):
        """Construct the standard workflow container used by pipeline screens.

        Layout (left -> right):
          - left: top row, 3D viewer, optional per-step action bar
          - right: side panel (visualizer / pipeline / params)

        Parameters mirror what controllers pass in: next button label/callback,
        back guard callable, and an optional widget to show under the viewer.
        """
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(12)

        # --- Left: viewer + top row + action bar ---
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Top row (Back / menu / Next)
        top_row = self._build_workflow_top_row(next_label, next_callback, back_guard)
        left_layout.addLayout(top_row)

        # Create a fresh VTK viewer widget for this container.
        # Reusing a previously-created QVTKRenderWindowInteractor can lead
        # to "wrapped C/C++ object has been deleted" errors when Qt
        # has already destroyed the old widget. Always instantiate a new
        # widget here and overwrite any previous references.
        try:
            self.frame = QFrame()
            self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
            # create a Plotter for convenience (may be re-used by controllers)
            try:
                self.plt = Plotter(qt_widget=self.vtkWidget)
            except Exception:
                self.plt = None
        except Exception:
            # Fallback: lightweight placeholder
            self.vtkWidget = QWidget()

        # Keep both attribute names used elsewhere compatible
        self.vtk_widget = getattr(self, "vtkWidget")

        # Add the viewer to the layout
        left_layout.addWidget(self.vtkWidget, stretch=1)

        # Optional per-step action bar below the viewer
        if action_widget is not None:
            left_layout.addWidget(action_widget)

        h_layout.addWidget(left, stretch=3)

        # --- Right: side panel ---
        side = self._build_side_panel()
        h_layout.addWidget(side, stretch=1)

        return container


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

    def _reset_top_menu_bar(self, current_step=None):
        """Clear the QMainWindow menu bar and rebuild it with pipeline steps."""
        menu_bar = self.menuBar()
        menu_bar.setVisible(True)
        menu_bar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {theme('palette.background', '#141414')};
                color: {theme('palette.textSecondary', '#A0A0A0')};
                border: none;
                padding: 0px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                color: {theme('palette.textSecondary', '#A0A0A0')};
                padding: 8px 15px;
                spacing: 0px;
                border: none;
            }}
            QMenuBar::item:selected {{
                background-color: {theme('palette.panel', '#2A2A2A')};
                color: {theme('palette.textPrimary', '#FFFFFF')};
                border-radius: 4px;
            }}
            QMenuBar::item:disabled {{
                color: {theme('palette.textDisabled', '#3A3A3A')};
            }}
        """)
        old_corner = menu_bar.cornerWidget(Qt.Corner.TopRightCorner)
        menu_bar.setCornerWidget(None)
        if old_corner is not None:
            old_corner.deleteLater()
        menu_bar.clear()
        
        # Add pipeline steps first if we have a current step
        if current_step is not None:
            # Add pipeline steps as top-level menu items
            for idx, step in enumerate(self.PIPELINE_STEPS):
                flag = self.STEP_DONE_FLAG.get(step)
                is_done = bool(flag and self.workflow_state.get(flag))
                is_reachable = all(
                    self.workflow_state.get(self.STEP_DONE_FLAG[s])
                    for s in self.PIPELINE_STEPS[:idx]
                    if s in self.STEP_DONE_FLAG
                )
                is_current = step == current_step
                
                if is_current:
                    label = f"● {step}"
                elif is_done:
                    label = f"✓ {step}"
                elif is_reachable:
                    label = step
                else:
                    label = f"🔒 {step}"
                
                action = QAction(label, self)
                action.setEnabled(is_reachable and not is_current)
                if action.isEnabled():
                    action.triggered.connect(
                        lambda checked=False, s=step: self._navigate_to_step(s, current_step)
                    )
                menu_bar.addAction(action)
                
                # Add separator between steps
                if idx < len(self.PIPELINE_STEPS) - 1:
                    menu_bar.addSeparator()
            
            # Add a separator before File menu
            menu_bar.addSeparator()
        
        return menu_bar

   

    def setup_workflow_menu(self, current_step):
        """Build the main menu bar with File, View, and pipeline steps."""
        menu_bar = self._reset_top_menu_bar(current_step=current_step)
        self._build_file_menu(menu_bar)
        self._build_view_menu(menu_bar)

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

        menu_bar.setStyleSheet(f"""
            QMenuBar {{ background-color: {theme('palette.primary', '#0D7C66')}; color: {theme('palette.textPrimary', '#FFFFFF')}; }}
            QMenuBar::item {{ background-color: transparent; color: {theme('palette.textPrimary', '#FFFFFF')}; padding: 20px 30px; }}
            QMenuBar::item:selected {{ background-color: {theme('palette.primaryHover', '#41B3A2')}; }}
        """)

        left_panel = QWidget()
        get_started_btn = create_styled_button("Get Started", size=50)
        get_started_btn.clicked.connect(
            lambda: self.navigate_to(self.show_first_screen)
        )

        label_main = AnimatedGradientLabel("LimbLab")
        try:
            hero_size = int(theme("typography.fontSizeHero", 100))
        except Exception:
            hero_size = 100
        fnt = label_main.font()
        fnt.setPointSize(hero_size)
        fnt.setBold(True)
        label_main.setFont(fnt)

        sublabel_main = create_label(
            "Analyze your 3D limb data with unprecedented ease.",
            f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeLarge', 18)}px;",
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

        container = AnimatedGradientWidget()
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
        self.label_upload = create_label("Create New Experiment", f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeHero', 40)}px;")
        self.button_upload = create_styled_button("Upload TIF Volume")
        self.button_upload.clicked.connect(self.create_new_experiment)

        upload_desc = create_label(
            "Upload a TIF volume to start a new experiment.\n"
            "You can add more channels later.",
            f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeBase', 14)}px; text-align: center;"
        )
        upload_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_desc.setWordWrap(True)

        
        # ---- Library Access ----
        self.label_library = create_label("Access Limb Library", f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeHero', 40)}px;")
        self.button_library = create_styled_button("View Experiments")
        self.button_library.clicked.connect(lambda: self.navigate_to(self.show_exp))

        library_desc = create_label(
            "View and manage your existing experiments\n"
            "or load them for visualization.",
            f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeBase', 14)}px; text-align: center;"
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
            # Get the experiment object
            exp_obj = self.experiment_metadata.get(path)
            
            # Handle case where experiment might not exist
            if exp_obj is None:
                continue
                
            # Access attributes directly from the Experiment object
            display_name = self.experiment_names.get(path, os.path.basename(path))
            
            # Access channels directly from the Experiment object
            channels = exp_obj.channels if hasattr(exp_obj, 'channels') else []
            channel_names = [ch.channel_name for ch in channels] if channels else []

            ''''
        
            # Check if experiment is complete (has DAPI + gene)
            is_valid, status_message = self._validate_experiment_channels(path)
            status_icon = "✅" if is_valid else "⚠️"
            status_color = theme('palette.primaryHover', '#41B3A2') if is_valid else theme('palette.warning', '#FF6B6B')

            
            '''

            # Show channel info
            channel_display = ""
            if channels:
                channel_display = f"[{', '.join(channel_names)}]"
            else:
                channel_display = "[No channels]"
            
            # Create row with status indicator
            row = QHBoxLayout()
            
            # Experiment name with status
            name_label = QLabel(f"{display_name}")
            name_label.setStyleSheet(f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeLarge', 18)}px;")
            #name_label.setToolTip(status_message if not is_valid else "Experiment is complete")
            
            # Show channel count - use the channels from the Experiment object directly
            channel_count = len(channels)
            channel_info = QLabel(f"({channel_count} channels)")
            channel_info.setStyleSheet(f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeSmall', 12)}px;")
            
            threebutton = QToolButton()
            threebutton.setIcon(QIcon("threedots.png"))
            threebutton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            threebutton.clicked.connect(lambda checked, p=path, b=threebutton: self._click_threebuttons(p, b))

            checkbox = QCheckBox()
            checkbox.setEnabled(True)   

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
            f"background-color: {theme('palette.panel', '#2A2A2A')}; border-radius: {theme('shape.borderRadiusPanel', '12px')};"
        )
        experiments_card.setLayout(card_layout)
        experiments_card.setMinimumHeight(250)

        self.add_btn = create_styled_button('+ Add Experiment')
        self.add_channel_btn = create_styled_button('+ Add Channel')
        self.view_btn = create_styled_button('View Experiment')
        self.refresh_btn = create_styled_button('↻ Refresh')

        self.add_btn.clicked.connect(self.addexp_button_clicked)
        self.add_channel_btn.clicked.connect(self.addchannel_button_clicked)
        self.view_btn.clicked.connect(self.viewexp_button_clicked)
        self.refresh_btn.clicked.connect(self._refresh_experiments)

        buttons_row = QVBoxLayout()
        buttons_row.setContentsMargins(0, 20, 0, 20)  # Add vertical padding

        # Add stretch before and after to center the group, but with big spacing
        buttons_row.addStretch(1)  # Big stretch on left
        buttons_row.addWidget(self.add_btn)
        buttons_row.addSpacing(10)
        buttons_row.addWidget(self.add_channel_btn)
        buttons_row.addSpacing(10)
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

    def addchannel_button_clicked(self, checked=False):
        """Add channel button handler - adds a channel to an existing experiment."""
        self._add_channel_to_existing()



    def _refresh_experiments(self):
        """Refresh the experiments list."""
        self._load_experiments_from_db()
        self.show_exp()
        QMessageBox.information(self, "Refreshed", "Experiment list updated.")


    def show_viz(self):
        container = self._build_workflow_container(
        next_label="Clean",
        next_callback=lambda: self.navigate_to(lambda: self.clean.show(self.current_experiment)),
        back_guard=None,
        current_step="Visualize"
    )
        self.setCentralWidget(container)

        # Use the helper
        self.setup_workflow_menu("Visualize")

        if (
            self.workflow_state.get("align_done")
            and self.align.source is not None
            and self.align.surface_path is not None
        ):
            self._show_final_aligned_mesh()
        elif (
            self.workflow_state.get("clean_done")
            and self.workflow_state.get("last_cleaned_channel")
            and self.workflow_state["last_cleaned_channel"] != "DAPI"
        ):
            self._show_cleaned_channel_preview()
        else:
            self._show_raw_volume_preview(self.current_experiment)


    def _show_final_aligned_mesh(self):
        """Show the fully processed (aligned) limb mesh — final pipeline output."""
        try:
            mesh = Mesh(str(self.align.surface_path))
            T = self.align.source.transform
            mesh.apply_transform(T)

            self.viz_plotter = Plotter(qt_widget=self.vtk_widget)
            self.viz_plotter.show(mesh)
        except Exception as e:
            print(f"Error loading final aligned mesh: {e}")


    def _show_cleaned_channel_preview(self):
        """Show the cleaned (final) volume for a gene-only workflow."""
        channel_name = self.workflow_state["last_cleaned_channel"]
        channel = next(
            (ch for ch in (self.current_experiment.channels or [])
             if ch.channel_name.upper() == channel_name.upper()),
            None,
        )
        if channel is None:
            print(f"Cleaned channel '{channel_name}' not found on experiment.")
            self._show_raw_volume_preview(self.current_experiment)
            return

        full_path = os.path.join(self.current_experiment.base, channel.path)
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            return

        try:
            self.viz_plotter = preview_volume(
                raw_volume_path=full_path,
                renderer="pyqt",
                outside_class=self,
            )
        except Exception as e:
            print(f"Error loading cleaned channel preview: {e}")


    def _show_raw_volume_preview(self, experiment):
        """First-look, non-processed view of the experiment's raw volume."""
        channels = experiment.channels or []
        if not channels:
            print(f"No channels found for experiment: {experiment.experiment_id}")
            return

        dapi_channel = next(
            (ch for ch in channels if ch.channel_name.upper() == "DAPI"), None
        )
        channel = dapi_channel or channels[0]

        full_path = os.path.join(experiment.base, channel.path)
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            return

        try:
            self.viz_plotter = preview_volume(
                raw_volume_path=full_path,
                renderer="pyqt",
                outside_class=self,
            )
        except Exception as e:
            print(f"Error loading volume preview: {e}")


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

    ######################################################################################################
  

    def _show_busy(self, message):
            self._busy_dialog = QDialog(self)
            self._busy_dialog.setWindowTitle("Please wait")
            self._busy_dialog.setModal(True)
            self._busy_dialog.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')}; color: {theme('palette.textPrimary', '#FFFFFF')};")
            layout = QVBoxLayout(self._busy_dialog)
            layout.addWidget(create_label(message, f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeBase', 14)}px;"))
            self._busy_dialog.setFixedSize(320, 100)
            self._busy_dialog.show()
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()

    def _hide_busy(self):
        if getattr(self, "_busy_dialog", None) is not None:
            self._busy_dialog.close()
            self._busy_dialog = None




    # ------------------------------------------------------------------
    # Side Panel Methods
    # ------------------------------------------------------------------
    def _build_side_panel(self):
        """Build the collapsible right-side panel."""
        panel = QWidget()
        panel.setFixedWidth(260)
        panel.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: {theme('palette.surface', '#1E1E1E')}; }}
            QScrollBar:vertical {{ border: none; background: {theme('palette.panel', '#2A2A2A')}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {theme('palette.primaryHover', '#41B3A2')}; border-radius: 5px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {theme('palette.primary', '#5FBF9F')}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; }}
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
        self.pipeline_log_widget.setStyleSheet(f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeSmall', 12)}px;")
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
            empty_label.setStyleSheet(f"color: {theme('palette.textDisabled', '#666666')}; font-size: {theme('typography.fontSizeSmall', 12)}px;")
            self.visualizer_list.addWidget(empty_label)
            return

        for path in self.experiments:
            name = self.experiment_names.get(path, os.path.basename(path))
            row = QLabel(f"• {name}")
            row.setStyleSheet(f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeBase', 14)}px; padding: 2px 0px;")
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
                    f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeBase', 14)}px; font-weight: bold; padding: 5px 0px; border-top: 1px solid {theme('palette.panel', '#2A2A2A')};"
                    if is_bold
                    else f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeSmall', 12)}px; font-style: italic; padding: 5px 0px; border-top: 1px solid {theme('palette.panel', '#2A2A2A')};"
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
                QMessageBox.warning(
                    self, "Duplicate",
                    f"Experiment '{exp_id}' already exists. Use '+ Add Channel' instead."
                )
                return

            # Get channel type from dialog
            channel_name = limb_info['channel_type']
          

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
                        path=os.path.basename(filepath)
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
        self._show_busy('Loading volume...')

        selected = [path for path, cb in self.experiment_checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")
            return

        exp_id = selected[0]
        self.filepath = exp_id

        self.current_experiment = get_experiment(self.db_path, exp_id)   # <- real Experiment, not a dict

        self.workflow_state = {
            "clean_done": False, "last_cleaned_channel": None,
            "surface_done": False, "stage_done": False, "selected_stage": None,
            "align_done": False, "alignment_method": None,
        }

        self._hide_busy()

        self.navigate_to(self.show_viz)


    def _add_channel_to_existing(self, specific_exp_id=None):
        if not specific_exp_id:
            if not self.experiments:
                QMessageBox.warning(self, "No experiments", "No existing experiments found.")
                return
            exp_id, ok = QInputDialog.getItem(
                self, "Select Experiment", "Select experiment to add channel to:",
                self.experiments, 0, False
            )
            if not ok or not exp_id:
                return
        else:
            exp_id = specific_exp_id

        exp_data = self.experiment_metadata.get(exp_id)
        if not exp_data:
            QMessageBox.warning(self, "Error", "Experiment not found.")
            return

        current_channels = [ch.channel_name for ch in (exp_data.channels or [])]
        channel_info = f"Current channels: {', '.join(current_channels) if current_channels else 'None'}"

        filepath, _ = QFileDialog.getOpenFileName(
            parent=self, caption='Select gene channel TIF file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti *.nii *.nii.gz)'
        )
        if not filepath:
            return
        if not filepath.lower().endswith((".tif", ".tiff", ".vti", ".nii", ".nii.gz")):
            QMessageBox.warning(self, "Invalid file", "Please select a valid volume file.")
            return

        channel_type, ok = QInputDialog.getItem(
            self, "Channel Type", f"Select channel type to add:\n\n{channel_info}",
            ["Hoxa11", "Sox9", "BMP2", "SHH"], 0, False
        )
        if not ok or not channel_type:
            return

        try:
            for channel in exp_data.channels or []:
                if channel.channel_name.upper() == channel_type.upper():
                    QMessageBox.warning(
                        self, "Duplicate Channel",
                        f"Channel '{channel_type}' already exists in this experiment.\n{channel_info}"
                    )
                    return

            new_channel = Channel(
                experiment_id=exp_id,
                channel_name=channel_type,
                path=os.path.basename(filepath),
                v0=174.0,
                v1=335.0,
            )

            exp_data.channels.append(new_channel)
            save_experiment(self.db_path, exp_data)   # exp_data is already a real Experiment — no need to rebuild it

            self._load_experiments_from_db()
            self.show_exp()

            is_valid, status = self._validate_experiment_channels(exp_id)
            channel_list = ', '.join(ch.channel_name for ch in exp_data.channels)

            if is_valid:
                QMessageBox.information(
                    self, "Success",
                    f"✅ Added {channel_type} channel to experiment: {exp_id}\n"
                    f"📁 File: {os.path.basename(filepath)}\n\n"
                    f"🎉 Experiment is now complete!\nChannels: {channel_list}\n\n"
                    f"You can now visualize this experiment."
                )
            else:
                QMessageBox.information(
                    self, "Success",
                    f"✅ Added {channel_type} channel to experiment: {exp_id}\n"
                    f"📁 File: {os.path.basename(filepath)}\n\n"
                    f"⚠️ Experiment is still incomplete:\n{status}\n\n"
                    f"Current channels: {channel_list}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add channel: {e}")
            import traceback
            traceback.print_exc()


    def _validate_experiment_channels(self, exp_id):
        exp_data = self.experiment_metadata.get(exp_id)
        if not exp_data: 
            return False, f"Experiment '{exp_id}' not found in database."

        channels = exp_data.channels or []
        if not channels:
            return False, "No channels found in this experiment.\nPlease upload at least DAPI and one gene channel."

        has_dapi = False
        gene_channels = []
        gene_names = ['Hoxa11', 'Sox9', 'BMP2', 'SHH']

        for channel in channels:
            channel_name = channel.channel_name.upper()
            if channel_name == 'DAPI':
                has_dapi = True
            elif channel_name in [g.upper() for g in gene_names]:
                gene_channels.append(channel.channel_name)

        if not has_dapi:
            return False, "Missing required DAPI channel.\n\nPlease upload a DAPI .tiff file first."
        if len(gene_channels) == 0:
            return False, "Missing gene channels.\n\nPlease upload at least one gene channel:\n- Hoxa11\n- Sox9\n- BMP2"

        return True, f"Experiment has DAPI and {len(gene_channels)} gene channel(s): {', '.join(gene_channels)}"


    #helper function -> TODO DELETE when everything is done!
    def menu_button_clicked(self, s):
        """Placeholder for menu button clicks."""
        print("click", s)


    def log_pipeline(self, message):
        """Add a message to the pipeline log."""
        self.pipeline_log.append(message)
        if hasattr(self, "pipeline_log_widget"):
            self.pipeline_log_widget.setText("\n".join(self.pipeline_log[-10:]))
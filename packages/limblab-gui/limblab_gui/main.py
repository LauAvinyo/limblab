# pyright: reportOptionalMemberAccess=false
# pyright: ignore[reportAttributeAccessIssue]

import os
import traceback
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import vtkmodules
from components.terminal_paper import TerminalPaperWidget
from config import *
from controllers.align_controller import AlignController
from controllers.clean_controller import CleanController
from controllers.stage_controller import StageController
from controllers.surface_controller import SurfaceController
from limblab.database import (
    delete_channel,
    delete_experiment,
    get_experiment,
    init_db,
    list_experiments,
    rename_experiment,
    save_experiment,
    seed_reference_limbs,
)
from limblab.design import theme
from limblab.models import Channel, Experiment
from limblab.utils import generate_kwargs
from mixin.NavigationMixin import NavigationMixin
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
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
    QMessageBox,
    QPushButton,
    QStatusBar,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from utils import create_back_button, create_label, create_styled_button
from vedo import Mesh, Plotter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

vtkmodules.qt.QVTKRWIBase = "QGLWidget"

import sys
import webbrowser

from controllers.navigate_controller import NavigationController
from controllers.visualization_controller import VisualizationController
from menu_utils import MenuUtils
from vedo import printc

env = {}
with open("../../../.env") as f:
    for line in f:
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        # Ensure there is an '='
        if "=" not in line:
            continue
        # Split only on the first '='
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().replace('"', "").replace("'", "")
        env[key] = value

TEST_BASE_PATH = env["TEST_BASE_PATH"]
TEST_SURFACE_PATH = env["TEST_SURFACE_PATH"]
TEST_DAPI_FILENAME = env["TEST_RAW"]
TEST_DAPI_CLEAN = env["TEST_CLEAN"]


#for the test experiment i added the channels manually 


EXPERIMENT = Experiment(
    experiment_id="manual_test",
    base=TEST_BASE_PATH,
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="F",
    position="L",
    species="mouse",
    # surface_path=TEST_SURFACE_PATH,
    # surface_isovalue=165,
    # stage=260,
    channels=[
        Channel(
            experiment_id="manual_test",
            channel_name="DAPI",
            path=TEST_DAPI_FILENAME,
            # clean_isovalue_min = 0,
            # clean_isovalue_max = 54,
            # current_state = "a", 
            # clean_path=TEST_DAPI_CLEAN,
        )
    ],
)

class MainWindow(QMainWindow, NavigationMixin, MenuUtils):
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

        seed_reference_limbs(self.db_path)
        print('created db reference limb access!')


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
        
        self.active_viz_sections = []


        # Navigation
        self.navigation_stack = []
        self.current_screen = None

        self.action_bar = None
        
        # ---- Workflow state ----
        # Tracks whether the required action for each step of the
        # Viz -> Clean -> Surface -> Stage -> Align pipeline has been
        # completed. This drives both forward-navigation guards (can't
        # jump ahead without finishing the current step) and back
        # navigation warnings (you're about to lose unsaved progress).

        #standard workflow state for any experiment
        self.workflow_checkpoints = {
            "Clean": False,
            "Surface": False,
            "Stage": False,
            "Align": False,
            "Visualize": False # TODO: Think about this.
        }
        

        self.surface = SurfaceController(self)
        self.clean = CleanController(self)
        self.align = AlignController(self)
        self.stage = StageController(self) 
        self.visualizer = VisualizationController(self)

        self.navigation = NavigationController(self)
        
        self.navigation._build_permanent_chrome()

        # self.navigate_to(lambda:self.align.show(experiment))
        self.navigation.navigate_to(self.show_home)



    # ------------------------------------------------------------------
    # Menu Building Methods
    # ------------------------------------------------------------------

    def create_left_button(self):
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
          - right: side panel (visu_dalizer / pipeline / params)

        Parameters mirror what controllers pass in: next button label/callback,
        back guard callable, and an optional widget to show under the viewer.
        """

        self._active_back_guard = back_guard

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

    
    # ------------------------------------------------------------------
    # Screen Methods
    # ------------------------------------------------------------------
    def show_home(self):
        self.action_bar.setVisible(False)

        topbar = self._build_home_topbar()

        left_panel = QWidget()
        get_started_btn = create_styled_button(
            "Get Started",
            color=theme("palette.primary", "#0D7C66"),
            hover_color=theme("palette.primaryHover", "#41B3A2"),
            size=50,
        )
        get_started_btn.clicked.connect(
            lambda: self.navigation.navigate_to(self.show_first_screen)
        )

        label_main = QLabel("LimbLab")
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
        left_layout.addSpacing(12)
        left_layout.addWidget(get_started_btn, alignment=Qt.AlignmentFlag.AlignHCenter)


        paper = TerminalPaperWidget(
            text=(
                "<- ->    use arrows to reduce/increase opacity\n"
                "x        toggle mesh visibility\n"
                "w        toggle wireframe/surface style\n"
                "l        toggle surface edges visibility\n"
                "1-3      cycle surface color\n"
                "k        cycle available lighting styles\n"
                "r        reset camera position\n"
                "shift    pan\n"
                "ctl/cmd  rotate over an axis"
            ),
            parent=self,
        )
        left_layout.addWidget(paper, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addSpacing(8)
        left_layout.addStretch(2)
        left_layout.setContentsMargins(40, 0, 40, 0)

        self.frame = QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtk_widget = self.vtkWidget

        self.limb_home = Mesh("Limb-rec_281.vtk").c(theme("limblab.surface"))
        
        params: dict[str, Any] = dict(bg = theme("palette.background"))
        kwargs = generate_kwargs(params=params, renderer='pyqt', outside_class=self)
        
        self.plt = Plotter(**kwargs)

        # Create vedo renderer and add objects and callbacks
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {theme('palette.background', '#141414')};")
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(topbar)

        body = QWidget()
        layout = QHBoxLayout(body)
        layout.addWidget(left_panel, stretch=3)
        layout.addWidget(self.vtkWidget, stretch=2)
        outer_layout.addWidget(body, stretch=1)

        self.setCentralWidget(container)
        self.plt.show(self.limb_home)

    def show_first_screen(self):
        self.action_bar.setVisible(False)

        top_row = QHBoxLayout()
        top_row.addWidget(create_back_button(self.navigation.go_back))
        top_row.addWidget(self.create_left_button())
        top_row.addStretch()

        # ---- Create New Experiment [UPLOAD] ----
        self.label_upload = create_label("Create New Experiment", f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeHero', 40)}px;")
        self.button_upload = create_styled_button(
            "Upload TIF Volume",
            color=theme("palette.secondary", "#54278F"),
            hover_color=theme("palette.secondaryHover", "#756BB1"),
        )
        self.button_upload.clicked.connect(self.create_new_experiment)

        upload_desc = create_label(
            "Upload a TIF volume to start a new experiment.\n"
            "You can add more channels later.",
            f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeBase', 14)}px; text-align: center;"
        )
        upload_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_desc.setWordWrap(True)

        
        # ---- Library Access [YOUR DATA] ----
        self.label_library = create_label("Access Limb Library", f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeHero', 40)}px;")
        self.button_library = create_styled_button(
            "View Experiments",
            color=theme("palette.accent", "#0D7C66"),
            hover_color=theme("palette.primaryHover", "#41B3A2"),
        )
        self.button_library.clicked.connect(lambda: self.navigation.navigate_to(self.show_user_experiment_list))

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


    def show_user_experiment_list(self):

        self.action_bar.setVisible(False)
        self._load_experiments_from_db()

        top_row = QHBoxLayout()
        top_row.addWidget(create_back_button(self.navigation.go_back))
        top_row.addWidget(self.create_left_button())
        top_row.addStretch()

        # Use a tree view for clear hierarchy: experiments -> channels
        tree = QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderHidden(True)
        tree.setStyleSheet(f"background-color: {theme('palette.panel', '#2A2A2A')}; border-radius: {theme('shape.borderRadiusPanel', '12px')};")
        tree.setIndentation(20)

        for path in self.experiments:
            exp_obj = self.experiment_metadata.get(path)
            if exp_obj is None:
                continue

            displayed_name = self.experiment_names.get(path, os.path.basename(path))
            channels = exp_obj.channels if hasattr(exp_obj, 'channels') else []

            parent = QTreeWidgetItem(tree)
            # store experiment id on the item
            parent.setData(0, Qt.ItemDataRole.UserRole, path)

            # Left column: name + meta
            name_widget = QWidget()
            name_layout = QHBoxLayout(name_widget)
            name_layout.setContentsMargins(8, 6, 8, 6)
            name_label = QLabel(displayed_name)
            name_label.setStyleSheet(f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-size: {theme('typography.fontSizeLarge', 18)}px;")
            channel_info = QLabel(f"({len(channels)} channels)")
            channel_info.setStyleSheet(f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeSmall', 12)}px;")
            name_layout.addWidget(name_label)
            name_layout.addSpacing(8)
            name_layout.addWidget(channel_info)
            name_layout.addStretch()
            tree.setItemWidget(parent, 0, name_widget)

            # Right column: action buttons for experiment
            # compact action buttons (icon-like) for readability
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            def make_small_btn(text, bg, hover, callback):
                btn = QToolButton()
                btn.setText(text)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setFixedSize(72, 28)
                btn.setToolTip(text)
                btn.setStyleSheet(f"background-color: {bg}; color: {theme('palette.textPrimary', '#FFFFFF')}; border-radius: 14px; font-size: 13px; padding: 0px 8px;")
                btn.clicked.connect(callback)
                return btn

            view_btn = make_small_btn('View', theme('palette.accent', '#0D7C66'), theme('palette.primaryHover', '#41B3A2'), lambda checked=False, p=path: self._view_experiment(p))
            add_ch_btn = make_small_btn('+Channel', theme('palette.secondary', '#54278F'), theme('palette.secondaryHover', '#756BB1'), lambda checked=False, p=path: self._add_channel_to_existing(p))
            del_btn = make_small_btn('Delete', theme('palette.error', '#A6284F'), theme('palette.error', '#C9302C'), lambda checked=False, p=path, n=displayed_name: self._delete_experiment(p,n))
            rename_btn = make_small_btn('Rename', theme('palette.error', "#3AAC58"), theme('palette.error', "#58C92C"), lambda checked=False, p=path: self._rename_experiment(p))

            act_layout.addWidget(view_btn)
            act_layout.addWidget(add_ch_btn)
            act_layout.addWidget(rename_btn)
            act_layout.addWidget(del_btn)
            tree.setItemWidget(parent, 1, act_widget)

            # Add channels as children
            for ch in channels:
                ch_name = ch.channel_name if hasattr(ch, 'channel_name') else ch.get('channel_name', '')
                ch_id = ch.id if hasattr(ch, 'id') else ch.get('id')
                child = QTreeWidgetItem(parent)
                # store channel info: tuple (experiment_id, channel_name)
                child.setData(0, Qt.ItemDataRole.UserRole, (path, ch_name, ch_id))
                ch_widget = QWidget()
                ch_layout = QHBoxLayout(ch_widget)
                ch_layout.setContentsMargins(8, 4, 8, 4)
                ch_label = QLabel(f"• {ch_name}")
                ch_label.setStyleSheet(f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeBase', 13)}px;")
                ch_layout.addSpacing(8)
                ch_layout.addWidget(ch_label)
                ch_layout.addStretch()
                tree.setItemWidget(child, 0, ch_widget)

                ch_act = QWidget()
                ch_act_layout = QHBoxLayout(ch_act)
                ch_act_layout.setContentsMargins(4, 2, 4, 2)
                ch_act_layout.setSpacing(6)

                ch_del = QToolButton()
                ch_del.setText('Delete')
                ch_del.setFixedSize(70, 26)
                ch_del.setToolTip('Delete')
                ch_del.setStyleSheet(f"background-color: {theme('palette.error', '#D9534F')}; color: {theme('palette.textPrimary', '#FFFFFF')}; border-radius: 13px; font-size: 12px; padding: 0px 6px;")
                ch_del.clicked.connect(lambda checked=False, p=path, c=ch_name, cid=ch_id: self._delete_channel(p, c, cid))

                ch_act_layout.addWidget(ch_del)
                tree.setItemWidget(child, 1, ch_act)

        # expose tree for other handlers (view button, bulk actions)
        self.experiments_tree = tree

        # improve readability: uniform row heights and column sizing
        tree.setUniformRowHeights(True)
        tree.setRootIsDecorated(True)
        tree.header().setStretchLastSection(False)
        tree.resizeColumnToContents(0)
        tree.setColumnWidth(1, 300)

        experiments_card = QWidget()
        experiments_layout = QVBoxLayout(experiments_card)
        experiments_layout.setContentsMargins(0, 0, 0, 0)
        experiments_layout.addWidget(tree)
        experiments_card.setMinimumHeight(250)

        self.add_btn = create_styled_button(
            '+ Add Experiment',
            color=theme('palette.secondary', '#54278F'),
            hover_color=theme('palette.secondaryHover', '#756BB1'),
        )
        
        self.refresh_btn = create_styled_button(
            '↻ Refresh',
            color=theme('palette.accent', '#0D7C66'),
            hover_color=theme('palette.primaryHover', '#41B3A2'),
        )

        self.add_btn.clicked.connect(self.addexp_button_clicked)
        #self.add_channel_btn.clicked.connect(self.addchannel_button_clicked)
        #self.view_btn.clicked.connect(self.viewexp_button_clicked)
        self.refresh_btn.clicked.connect(self._refresh_experiments)

        buttons_row = QVBoxLayout()
        buttons_row.setContentsMargins(0, 20, 0, 20)  # Add vertical padding

        # Add stretch before and after to center the group, but with big spacing
        buttons_row.addStretch(1)  # Big stretch on left
        buttons_row.addWidget(self.add_btn)
        buttons_row.addSpacing(10)
        buttons_row.addStretch(1)
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
        main_layout.addStretch(1)  # Extra stretch at bottomadd.
        main_layout.setContentsMargins(30, 20, 30, 5)

        self.setCentralWidget(container)

    # ---- Pipeline step screens (Viz -> Clean -> Surface -> Stage -> Align -> Viz) ----

    def addchannel_button_clicked(self, checked=False):
        """Add channel button handler - adds a channel to an existing experiment."""
        self._add_channel_to_existing()


    def _refresh_experiments(self):
        """Refresh the experiments list."""
        self._load_experiments_from_db()
        self.show_user_experiment_list()
        QMessageBox.information(self, "Refreshed", "Experiment list updated.")


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
        QApplication.processEvents()

    def _hide_busy(self):
        if getattr(self, "_busy_dialog", None) is not None:
            self._busy_dialog.close()
            self._busy_dialog = None





#trying things to click anywhere on the screen to make this pop up message dissappear


    def _show_message(self, message):
        self._busy_dialog = QWidget(self)
        self._busy_dialog.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup
        )
        self._busy_dialog.setStyleSheet(
            f"background-color: {theme('palette.surface', '#1E1E1E')}; "
            f"color: {theme('palette.textPrimary', '#FFFFFF')}; "
            f"border: 1px solid {theme('palette.border', '#3A3A3A')};"
        )
        layout = QVBoxLayout(self._busy_dialog)
        layout.addWidget(create_label(
            message,
            f"color: {theme('palette.textPrimary', '#FFFFFF')}; "
            f"font-size: {theme('typography.fontSizeBase', 14)}px;"
        ))
        self._busy_dialog.setFixedSize(320, 100)
        self._busy_dialog.show()
        self._busy_dialog.raise_()
        self._busy_dialog.activateWindow()
        QApplication.processEvents()
    


    # ------------------------------------------------------------------
    # Side Panel Methods
    # ------------------------------------------------------------------

    
    
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
                    self.experiment_metadata[exp_id] = exp_data
                    # Use the persisted display name if set, otherwise fall back to the id
                    self.experiment_names[exp_id] = exp_data.displayed_name or exp_id

            print(f"Loaded {len(self.experiments)} experiments from database")

        except Exception as e:
            print(f"Error loading experiments: {e}")
            self.experiments = []
            self.experiment_metadata = {}

    # ------------------------------------------------------------------
    # Button Actions
    # ------------------------------------------------------------------

    def _rename_experiment(self, path):
        """Rename an experiment and persist to DB."""
        current_name = self.experiment_names.get(path, os.path.basename(path))
        new_name, ok = QInputDialog.getText(
            self, "Rename experiment", "New name:", text=current_name
        )
        if ok and new_name.strip():
            success = rename_experiment(self.db_path, path, new_name.strip())
            if success:
                self.experiment_names[path] = new_name.strip()
                self.show_user_experiment_list()
            else:
                QMessageBox.warning(self, "Error", f"Experiment '{path}' not found in database.")

    # DELETE FUNCTION CALLS DATABASE DELETE FUNCTION, AUXILIAR UI
    def _delete_experiment(self, experiment_id, displayed_name):
        """Delete an experiment from the database."""
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Delete Experiment",
            f"Are you sure you want to delete experiment '{displayed_name}'?\nThis implies deleting all its associated channels from the database entry.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:

            success = delete_experiment(self.db_path, experiment_id)#delete_experiment as a functioin imported from database.py

            if success:#delete function returns True if exp ( exp = session.get(Experiment, experiment_id, if exp: session.delete(exp)session.commit() return True
                # Remove from local lists (UI logistics)
                if experiment_id in self.experiments:
                    self.experiments.remove(experiment_id)
                if experiment_id in self.experiment_names:
                    del self.experiment_names[experiment_id]
                if experiment_id in self.experiment_metadata:
                    del self.experiment_metadata[experiment_id]

                # Refresh the UI
                self.show_user_experiment_list()
                QMessageBox.information(
                    self, "Success", f"Deleted experiment: {displayed_name}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Experiment '{displayed_name}' not found in database.",
                )


    def _delete_channel(self, experiment_id, channel_name, channel_id):
        """Delete a channel from an experiment and persist to DB."""
        reply = QMessageBox.question(
            self,
            "Delete Channel",
            f"Are you sure you want to delete the selected channel '{channel_name}' from experiment '{experiment_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_channel(self.db_path, channel_id)

            if success:
                self.show_user_experiment_list()
                QMessageBox.information(
                    self, "Success", f"Deleted channel: {channel_name}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Channel '{channel_name}' not found in database.",
                )


    def _view_experiment(self, experiment_id):
        """View the selected experiment (show visualization)."""
        
        experiment = get_experiment(self.db_path, experiment_id)
        if not experiment:
            QMessageBox.warning(self, "Error", "Experiment not found.")
            return

        # NOTE: THIS IS DEBUGGING #
        experiment = EXPERIMENT
        ###########################

        
        self._set_current_experiment(experiment)
        self.navigation.navigate_to(lambda: self.visualizer.show_experiment(experiment))
    

    def _infer_workflow_state(self, exp):
        """Derive pipeline progress from what's actually persisted on the
        experiment row + its channels, rather than trusting an in-memory flag
        that could drift from what's really on disk/DB."""
        channels = exp.channels or []

        # A channel counts as "cleaned" if its stored path is a processed .vti,
        # matching the same convention surface_controller already checks.
        cleaned_channels = [ch for ch in channels if ch.path.lower().endswith(".vti")]
        clean_done = len(cleaned_channels) > 0
        last_cleaned_channel = cleaned_channels[-1].channel_name if cleaned_channels else None

        return {
            "clean_done": clean_done,
            "last_cleaned_channel": last_cleaned_channel,
            "surface_done": bool(exp.surface_path),
            "stage_done": exp.stage is not None,
            "selected_stage": exp.stage,
            "align_done": bool(exp.transformation_matrix_path),
            "alignment_method": "rigid" if exp.transformation_matrix_path else None,
        }
    


    def _set_current_experiment(self, exp_obj):
        """Switch the active experiment. Pipeline progress is derived from
        what's actually saved on this experiment's row — so resuming an
        experiment you cleaned/surfaced last week correctly shows those
        steps unlocked, without needing a separate progress table."""
        
        self.current_experiment = exp_obj
        self.workflow_state = self._infer_workflow_state(exp_obj)
        self.align.source = None
        self.align.surface_path = str(
            os.path.join(exp_obj.base, exp_obj.surface_path)
        ) if exp_obj.surface_path else None
    
    

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
                        channel_name=limb_info['channel_type'],
                        path=os.path.basename(filepath),
                    ) # pyright: ignore[reportCallIssue]
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
                f"Experiment created: {exp_id}\n"
                f"File: {os.path.basename(filepath)}\n"
                f"Channel: {channel_name}\n\n"
                f"{next_steps}"
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
            ['DAPI',"Hoxa11", "Sox9", "BMP2", "SHH"],
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
                'path': os.path.basename(filepath)
            }
            
            exp_data['channels'].append(new_channel)
            

            # Save to database
            save_experiment(self.db_path, self.current_experiment)
            
            # Reload and refresh
            self._load_experiments_from_db()
            self.show_exp()
            
            # Check if experiment is now complete
            is_valid, status = self._validate_experiment_channels(exp_id)
            
            if is_valid:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Added {channel_type} channel to experiment: {exp_id}\n"
                    f"File: {os.path.basename(filepath)}\n\n"
                    f"Channels: {', '.join([ch.get('channel_name', '') for ch in exp_data['channels']])}\n\n"
                )
            else:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Added {channel_type} channel to experiment: {exp_id}\n"
                    f"File: {os.path.basename(filepath)}\n\n"
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
            channel_combo.addItems(['DAPI',"Hoxa11", "Sox9", "BMP2"])
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

    def viewexp_button_clicked(self):
        """View experiment button handler."""
        # Use the experiments tree selection to determine the experiment to view
        if not hasattr(self, 'experiments_tree') or self.experiments_tree.currentItem() is None:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")
            return

        item = self.experiments_tree.currentItem()
        parent = item.parent() if item.parent() is not None else item
        exp_id = parent.data(0, Qt.ItemDataRole.UserRole)
        if not exp_id:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")

            return

        exp_obj = get_experiment(self.db_path, exp_id)
        if not exp_obj:
            QMessageBox.warning(self, "Not found", f"Experiment '{exp_id}' not found in database.")
            return

        self._set_current_experiment(exp_obj)
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
                    f"Added {channel_type} channel to experiment: {exp_id}\n"
                    f"File: {os.path.basename(filepath)}\n\n"
                  
                )
            else:
                QMessageBox.information(
                    self, "Success",
                    f"Added {channel_type} channel to experiment: {exp_id}\n"
                    f"File: {os.path.basename(filepath)}\n\n"
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









#self.navigate_to(lambda: self.raycast.show(self.current_channel)),
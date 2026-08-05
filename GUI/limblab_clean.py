from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PIL import Image
import os
import webbrowser
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QStatusBar, QVBoxLayout,
    QPushButton, QWidget, QHBoxLayout, QMessageBox,
    QSizePolicy, QMenuBar, QMenu, QToolButton, QFileDialog,
    QCheckBox, QInputDialog, QSlider, QSpinBox,
    QScrollArea, QComboBox
)

# Constants
MENU_STYLE = """
    QMenu { background-color: #0D7C66; color: white; border: 1px solid #41B3A2; }
    QMenu::item { padding: 8px 25px; background-color: transparent; }
    QMenu::item:selected { background-color: #41B3A2; color: white; }
    QMenu::item:disabled { color: #A0A0A0; }
"""

SECMENU_STYLE = """
    QMenu { background-color: #2B2B2B; color: white; border: 1px solid #2B2B2B; }
    QMenu::item { padding: 8px 25px; background-color: transparent; }
    QMenu::item:selected { background-color: #383838; color: white; }
"""

CATEGORY_PARAMS = {
    "Clean": [
        {"name": "Voxel spacing", "type": "slider", "min": 0, "max": 255, "default": 30},
        {"name": "Gaussian smoothing", "type": "spinbox", "min": 0, "max": 10, "default": 0},
        {"name": "Strip background noise", "type": "spinbox", "min": 0, "max": 10, "default": 0},
        {"name": "Low-pass filter", "type": "spinbox", "min": 0, "max": 10, "default": 0},
    ],
    "Surface": [
        {"name": "Surface extraction", "type": "spinbox", "min": 0, "max": 1, "default": 0},
        {"type": "text", "default": 'Select isovalue'},
    ],
    "Stage": [
        {"name": "aer_line", "type": "aer_line"},
        {"type": "text", "default": "Obtained values:"},
        {"type": "text", "default": "Morphological stage:"},
        {"type": "text", "default": "Staging accuracy:"},
        {"type": "text", "default": "Graphic summary"},
    ],
    "Align_Linear": [{"name": "reference", "type": "limb_reference"}],
    "Align_nonLinear": [
        {"name": "Offset X", "type": "slider", "min": -100, "max": 100, "default": 0},
        {"name": "Offset Y", "type": "slider", "min": -100, "max": 100, "default": 0},
        {"name": "Offset Z", "type": "slider", "min": -100, "max": 100, "default": 0},
        {"type": "text", "default": "⚠️ Align your data by adjusting offsets"},
    ],
}

VIZ_PARAMS = {
    "Isosurface": [
        {"name": "Number of isosurfaces", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Threshold", "type": "slider", "min": 0, "max": 10, "default": 1}
    ],
    'Slices': [
        {"type": "text", "default": "2D Plane sliders"},
        {"name": "X", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Y", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"name": "Z", "type": "slider", "min": 0, "max": 10, "default": 8},
        {"type": "text", "default": "Color map - redefine widget type"}
    ],
    'Raycast': [
        {"type": "text", "default": "Opacity"},
        {"name": "Hoxa11", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Sox9", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"name": "BMP2", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"name": "Limb surface", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"type": "text", "default": "Colour mapping - redefine widget type"}
    ],
    'Probe': [
        {"type": "text", "default": "Make a line through the limb to see the selected gene intensity values across"},
        {"name": "probe_line", "type": "probe_line"}
    ],
    '2D Projection Slab': [
        {"type": "text", "default": "Slab projection"},
        {"name": "Slab Max Value", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Slab Min Value", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"type": "text", "default": "Mean slab projection:"},
    ]
}

# Helper Functions
def create_styled_button(text, color="#0D7C66", hover_color="#41B3A2", size=None):
    """Create a styled push button with consistent styling."""
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: #ffffff;
            font-weight: bold;
            font-size: 18px;
            border-radius: 20px;
            padding: 10px 30px;
        }}
        QPushButton:hover {{ background-color: {hover_color}; }}
    """)
    if size:
        btn.setFixedHeight(size)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def create_label(text, style, alignment=Qt.AlignmentFlag.AlignLeft):
    """Create a styled label."""
    label = QLabel(text)
    label.setStyleSheet(style)
    label.setAlignment(alignment)
    return label

def create_slider(min_val, max_val, default_val, color="#0D7C66"):
    """Create a styled slider."""
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(default_val)
    slider.setStyleSheet(f"""
        QSlider::groove:horizontal {{
            border: 1px solid #999999; height: 8px;
            background: {color}; border-radius: 4px;
        }}
        QSlider::handle:horizontal {{
            background: white; border: 1px solid #5c5c5c;
            width: 18px; margin: -2px 0; border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{ background: #41B3A2; }}
        QSlider::sub-page:horizontal {{ background: {color}; border-radius: 4px; }}
        QSlider::add-page:horizontal {{ background: #2A2A2A; border-radius: 4px; }}
    """)
    return slider

def create_collapsible_section(title, content_widget, expanded=True):
    """Wraps content_widget in a header button that shows/hides it."""
    section = QWidget()
    section_layout = QVBoxLayout(section)
    section_layout.setContentsMargins(0, 0, 0, 0)
    section_layout.setSpacing(0)

    toggle_button = QToolButton()
    toggle_button.setText(title)
    toggle_button.setCheckable(True)
    toggle_button.setChecked(expanded)
    toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    toggle_button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
    toggle_button.setStyleSheet("""
        QToolButton {
            background-color: #2A2A2A; color: #ffffff;
            font-weight: bold; font-size: 14px;
            border: none; padding: 10px 12px; text-align: left;
        }
        QToolButton:hover { background-color: #333333; }
    """)
    toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    content_widget.setVisible(expanded)
    content_widget.setStyleSheet("background-color: #181818;")

    def on_toggle(checked):
        content_widget.setVisible(checked)
        toggle_button.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)

    toggle_button.toggled.connect(on_toggle)
    section_layout.addWidget(toggle_button)
    section_layout.addWidget(content_widget)
    return section

def create_back_button(callback):
    """Create a back button with consistent styling."""
    back_button = QPushButton("←")
    back_button.setFixedSize(30, 30)
    back_button.setCursor(Qt.CursorShape.PointingHandCursor)
    back_button.setStyleSheet("""
        QPushButton {
            background-color: #2A2A2A; color: white;
            font-size: 15px; border-radius: 15px;
        }
        QPushButton:hover { background-color: #41B3A2; }
    """)
    back_button.clicked.connect(callback)
    return back_button

# Custom Classes
class PointSelector(QObject):
    """Base class for point selection on the 3D viewer."""
    points_changed = pyqtSignal(list)
    
    def __init__(self, viewer, color=(0.6, 0.4, 1.0, 1.0)):
        super().__init__()
        self.viewer = viewer
        self.points = []
        self.line_item = None
        self.dot_item = None
        self.active = False
        self.color = color
        self.max_points = None  # None for unlimited

    def start(self):
        self.active = True
        self.clear()

    def stop(self):
        self.active = False

    def clear(self):
        self.points = []
        self._refresh_items()

    def add_point(self, screen_ratio):
        """Add a point at the given screen ratio."""
        if self.max_points and len(self.points) >= self.max_points:
            return
        
        radius = 10
        theta = screen_ratio * np.pi
        x = radius * np.cos(theta)
        y = radius * np.sin(theta) * 0.3
        z = radius * np.sin(theta * 0.5)
        self.points.append((x, y, z))
        self._refresh_items()
        self.points_changed.emit(self.points)

    def remove_last(self):
        if self.points:
            self.points.pop()
            self._refresh_items()
            self.points_changed.emit(self.points)

    def _refresh_items(self):
        if self.line_item is not None:
            self.viewer.removeItem(self.line_item)
            self.line_item = None
        if self.dot_item is not None:
            self.viewer.removeItem(self.dot_item)
            self.dot_item = None

        if not self.points:
            return

        pts = np.array(self.points, dtype=np.float32)

        if len(pts) > 1 and not self.max_points:
            segments = []
            for i in range(len(pts) - 1):
                segments.append(pts[i])
                segments.append(pts[i] + (pts[i + 1] - pts[i]) * 0.6)
            seg_arr = np.array(segments, dtype=np.float32)
            self.line_item = gl.GLLinePlotItem(
                pos=seg_arr, color=self.color, width=3, mode="lines"
            )
            self.viewer.addItem(self.line_item)
        elif len(pts) == 2 and self.max_points == 2:
            self.line_item = gl.GLLinePlotItem(
                pos=pts, color=self.color, width=3, mode="line_strip"
            )
            self.viewer.addItem(self.line_item)

        self.dot_item = gl.GLScatterPlotItem(
            pos=pts, color=self.color, size=10, pxMode=True
        )
        self.viewer.addItem(self.dot_item)


class AERSelector(PointSelector):
    def __init__(self, viewer):
        super().__init__(viewer, color=(0.6, 0.4, 1.0, 1.0))


class ProbeSelector(PointSelector):
    def __init__(self, viewer):
        super().__init__(viewer, color=(0.96, 0.66, 0.23, 1.0))
        self.max_points = 2

    def add_point(self, screen_ratio):
        if len(self.points) >= self.max_points:
            self.points = []
        super().add_point(screen_ratio)


class Viewer3D(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.setCameraPosition(distance=40)
        self.volume_item = None
        self.aer_selector = AERSelector(self)
        self.probe_selector = ProbeSelector(self)
        self.show_default_sphere()

    def show_default_sphere(self):
        if self.volume_item is not None:
            self.removeItem(self.volume_item)
            self.volume_item = None

        md = gl.MeshData.sphere(rows=20, cols=20, radius=10)
        self.volume_item = gl.GLMeshItem(
            meshdata=md, smooth=True, color=(0.4, 0.6, 1.0, 1.0),
            shader="shaded", glOptions="opaque"
        )
        self.addItem(self.volume_item)

    def show_volume(self, volume: np.ndarray):
        if self.volume_item is not None:
            self.removeItem(self.volume_item)
            self.volume_item = None

        vol = volume.astype(np.float32)
        vol -= vol.min()
        max_val = vol.max()
        if max_val > 0:
            vol = (vol / max_val * 255)
        vol = vol.astype(np.ubyte)

        rgba = np.zeros(vol.shape + (4,), dtype=np.ubyte)
        rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = rgba[..., 3] = vol

        self.volume_item = gl.GLVolumeItem(rgba)
        self.volume_item.translate(-vol.shape[0] / 2, -vol.shape[1] / 2, -vol.shape[2] / 2)
        self.addItem(self.volume_item)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            ratio = event.position().x() / max(self.width(), 1)
            if self.aer_selector.active:
                self.aer_selector.add_point(ratio)
                return
            if self.probe_selector.active:
                self.probe_selector.add_point(ratio)
                return
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LimbLab")
        self.setStyleSheet("QMainWindow, QWidget { background-color: #141414; }")
        self.setStatusBar(QStatusBar(self))

        self.viewer = Viewer3D()
        self.experiments = []
        self.experiment_names = {}
        self.pipeline_log = []
        self.param_values = {}
        self.nav_stack = []
        self.current_screen = None
        self.active_categories = []
        self.active_viz_sections = []
        self.check_genes_viz = ['Hoxa11', 'Sox9', 'BMP2']
        self.filepath = None

        self.navigate_to(self.show_home)

    # Navigation Methods
    def navigate_to(self, screen_func):
        if self.current_screen is not None:
            self.nav_stack.append(self.current_screen)
        self.current_screen = screen_func
        screen_func()

    def go_back(self):
        if self.nav_stack:
            previous_screen = self.nav_stack.pop()
            self.current_screen = previous_screen
            previous_screen()

    def reset_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setVisible(False)
        old_corner = menu_bar.cornerWidget(Qt.Corner.TopRightCorner)
        menu_bar.setCornerWidget(None)
        if old_corner is not None:
            old_corner.deleteLater()
        menu_bar.clear()
        menu_bar.setStyleSheet("")

    # Menu Building Methods
    def _build_resources_menu(self, menu):
        """Build the Resources submenu."""
        resources = menu.addMenu("Resources")
        paper = QAction("Paper", self)
        paper.triggered.connect(lambda: webbrowser.open('https://pmc.ncbi.nlm.nih.gov/articles/PMC12794269/'))
        resources.addAction(paper)
        
        github = QAction("GitHub", self)
        github.triggered.connect(lambda: webbrowser.open('https://limblab.embl.es/docs/'))
        resources.addAction(github)
        return resources

    def _build_contact_menu(self, menu):
        """Build the Contact us submenu."""
        contact = menu.addMenu("Contact us")
        contact.addAction(QAction("EMBL, Barcelona", self, enabled=False))
        contact.addAction(QAction("info@embl.es", self, enabled=False))
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
        view_menu.addAction(QAction("Visualization Mode", self, enabled=False))
        
        viz_modes = ["Isosurface", "Slices", "Raycast", "Probe", "2D Projection Slab"]
        for mode in viz_modes:
            action = QAction(mode, self, checkable=True)
            action.triggered.connect(lambda checked, m=mode: self.add_viz_section(m))
            view_menu.addAction(action)
        return view_menu

    def _build_clean_menu(self, menu_bar):
        """Build the Clean menu."""
        clean_menu = menu_bar.addMenu("Clean")
        clean_action = QAction("Clean", self)
        clean_action.triggered.connect(lambda: self.add_category_section("Clean"))
        clean_menu.addAction(clean_action)
        return clean_menu

    def _build_surface_menu(self, menu_bar):
        """Build the Surface menu."""
        surface_menu = menu_bar.addMenu("Surface")
        surface_action = QAction("Surface", self)
        surface_action.triggered.connect(lambda: self.add_category_section("Surface"))
        surface_menu.addAction(surface_action)
        return surface_menu

    def _build_stage_menu(self, menu_bar):
        """Build the Stage menu."""
        stage_menu = menu_bar.addMenu("Stage")
        stage_action = QAction("Stage", self)
        stage_action.triggered.connect(lambda: self.add_category_section("Stage"))
        stage_menu.addAction(stage_action)
        return stage_menu

    def _build_align_menu(self, menu_bar):
        """Build the Align menu."""
        align_menu = menu_bar.addMenu("Align")
        align_menu.addAction(QAction("Alignment method", self, enabled=False))
        
        linear = QAction('Linear-Rigid', self)
        linear.triggered.connect(lambda: self.add_category_section("Align_Linear"))
        align_menu.addAction(linear)
        
        non_linear = QAction('Non Linear-TPS', self)
        non_linear.triggered.connect(lambda: self.add_category_section("Align_nonLinear"))
        align_menu.addAction(non_linear)
        return align_menu

    # Screen Methods
    def show_home(self):
        self.reset_menu_bar()
        self.viewer.setParent(None)

        menu_bar = self.menuBar()
        lb_action = QAction('LimbLab', self)
        lb_action.triggered.connect(lambda: webbrowser.open('https://limblab.embl.es/docs/'))
        menu_bar.addAction(lb_action)

        right_menu = QMenuBar(menu_bar)
        menu_bar.setCornerWidget(right_menu, Qt.Corner.TopRightCorner)

        

        self._build_resources_menu(right_menu)
        
        aboutus_action = QAction("About us", self)
        aboutus_action.triggered.connect(lambda: webbrowser.open('https://www.embl.org/groups/sharpe/'))
        right_menu.addAction(aboutus_action)

        self._build_contact_menu(right_menu)

        menu_bar.setStyleSheet("""
            QMenuBar { background-color: #0D7C66; color: white; }
            QMenuBar::item { background-color: transparent; color: white; padding: 20px 30px; }
            QMenuBar::item:selected { background-color: #41B3A2; }
        """)

        left_panel = QWidget()
        get_started_btn = create_styled_button("Get Started", size=50)
        get_started_btn.clicked.connect(lambda: self.navigate_to(self.show_first_screen))

        label_main = QLabel(
            '<span style="font-size:100px; font-weight:bold; color:#5FBF9F;">Limb</span>'
            '<span style="font-size:100px; font-weight:bold; color:#8E7FD6;">Lab</span>'
        )
        label_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sublabel_main = create_label(
            "Analyze your 3D limb data with unprecedented ease.",
            "color: #A0A0A0; font-size: 20px;"
        )

        left_layout = QVBoxLayout(left_panel)
        left_layout.addStretch(1)
        left_layout.addWidget(label_main, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addWidget(sublabel_main, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addSpacing(20)
        left_layout.addWidget(get_started_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch(2)
        left_layout.setContentsMargins(40, 0, 40, 0)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(left_panel, stretch=3)
        layout.addWidget(self.viewer, stretch=2)
        self.setCentralWidget(container)

    def show_first_screen(self):
        self.reset_menu_bar()
        self.viewer.setParent(None)

        top_row = QHBoxLayout()
        top_row.addWidget(create_back_button(self.go_back))
        top_row.addWidget(self._create_left_button())
        top_row.addStretch()

        self.label_upload = create_label("Upload your limb data", "color: #ffffff; font-size: 40px;")
        self.button_upload = create_styled_button("Select .tiff file")
        self.button_upload.clicked.connect(self.getfilename)

        self.label_library = create_label("Load limb data", "color: #ffffff; font-size: 40px;")
        self.button_library = create_styled_button("Access limb library")
        self.button_library.clicked.connect(lambda: self.navigate_to(self.show_viz))

        upload_column = QVBoxLayout()
        upload_column.addWidget(self.label_upload, alignment=Qt.AlignmentFlag.AlignHCenter)
        upload_column.addWidget(self.button_upload, alignment=Qt.AlignmentFlag.AlignHCenter)

        library_column = QVBoxLayout()
        library_column.addWidget(self.label_library, alignment=Qt.AlignmentFlag.AlignHCenter)
        library_column.addWidget(self.button_library, alignment=Qt.AlignmentFlag.AlignHCenter)

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
        self.viewer.setParent(None)

        top_row = QHBoxLayout()
        top_row.addWidget(create_back_button(self.go_back))
        top_row.addWidget(self._create_left_button())
        top_row.addStretch()

        card_layout = QVBoxLayout()
        self.experiment_checkboxes = []

        for path in self.experiments:
            display_name = self.experiment_names.get(path, os.path.basename(path))
            row = QHBoxLayout()
            label = QLabel(display_name)
            label.setStyleSheet("color: #ffffff; font-size: 18px;")
            
            threebutton = QToolButton()
            threebutton.setIcon(QIcon("threedots.png"))
            threebutton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            threebutton.clicked.connect(lambda checked, p=path, b=threebutton: self._click_threebuttons(p, b))
            
            checkbox = QCheckBox()
            row.addWidget(label)
            row.addWidget(checkbox)
            row.addWidget(threebutton)
            row.addStretch()
            card_layout.addLayout(row)
            self.experiment_checkboxes.append((path, checkbox))

        card_layout.addStretch()

        experiments_card = QWidget()
        experiments_card.setStyleSheet("background-color: #2A2A2A; border-radius: 12px;")
        experiments_card.setLayout(card_layout)
        experiments_card.setMinimumHeight(250)

        self.add_btn = create_styled_button('+ Add Experiment', "#7C6FD6", "#8E7FD6")
        self.save_btn = create_styled_button('Save Experiment', "#4B2E83", "#5C3A9E")
        self.view_btn = create_styled_button('View', "#41B3A2", "#5FBF9F")

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
        buttons_row.addWidget(self.view_btn)
        buttons_row.addStretch(1)  # Big stretch on right

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

    def show_viz(self):
        self.viewer.setParent(None)

        menu_bar = self.menuBar()
        menu_bar.setVisible(False)
        menu_bar.setStyleSheet("")
        old_corner = menu_bar.cornerWidget(Qt.Corner.TopRightCorner)
        menu_bar.setCornerWidget(None)
        if old_corner is not None:
            old_corner.deleteLater()
        menu_bar.clear()

        if hasattr(self, 'filepath') and self.filepath:
            volume = self._png_to_dummy_volume(self.filepath)
            self.viewer.show_volume(volume)

        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_row.addWidget(create_back_button(self.go_back))
        top_row.addStretch()

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addLayout(top_row)
        left_layout.addWidget(self.viewer)

        self.side_panel = self._build_side_panel()

        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(left_container, stretch=1)
        main_layout.addWidget(self.side_panel, stretch=0)
        self.setCentralWidget(container)

        menu_bar.setVisible(True)
        self._build_file_menu(menu_bar)
        self._build_view_menu(menu_bar)
        
        select_action = QAction("Select", self)
        select_action.triggered.connect(self.menu_button_clicked)
        select_menu = menu_bar.addMenu("&Select")
        select_menu.addAction(select_action)

        self._build_clean_menu(menu_bar)
        self._build_surface_menu(menu_bar)
        self._build_stage_menu(menu_bar)
        self._build_align_menu(menu_bar)

    # Side Panel Methods
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

        scroll_layout.addWidget(create_collapsible_section("Visualizer", self.visualizer_content, expanded=True))

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
            "\n".join(self.pipeline_log[-10:]) if self.pipeline_log else "pipeline.log was automatically generated. \nNo actions yet."
        )
        self.pipeline_log_widget.setWordWrap(True)
        self.pipeline_log_widget.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        pipeline_layout.addWidget(self.pipeline_log_widget)

        scroll_layout.addWidget(create_collapsible_section("Pipeline", pipeline_content, expanded=True))

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

    # Category and Viz Section Builders
    def add_category_section(self, category):
        """Add a category section to the side panel."""
        if category not in self.active_categories:
            self.active_categories.append(category)
            self.log_pipeline(f"{category} parameters added.")

        if not hasattr(self, 'dynamic_sections_layout'):
            return

        if category in getattr(self, '_current_section_widgets', {}):
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
                    if is_bold else
                    "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
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

        if not hasattr(self, 'viz_sections_layout'):
            return

        if viz_name in getattr(self, '_current_viz_section_widgets', {}):
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
            "probe_line": self._add_probe_line_param,
        }

        for param in params:
            if param.get("type") == "text":
                is_bold = viz_name == '2D Projection Slab'
                style = (
                    "color: #ffffff; font-size: 13px; font-weight: bold; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
                    if is_bold else
                    "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
                )
                info_label = create_label(param.get("default", ""), style, Qt.AlignmentFlag.AlignLeft)
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
            'Channels overlaid',
            "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
        )
        layout.addWidget(channels_label)

        colors = ['#41B3A2', '#54278F', '#756BB1']
        stored_channels = self.param_values.setdefault(viz_name, {}).setdefault("channels", {})

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
                lambda state, v=viz_name, g=gene: self._on_gene_channel_changed(v, g, state)
            )
            layout.addWidget(checkbox)

    def _on_gene_channel_changed(self, viz_name, gene, state):
        """Handle gene channel checkbox changes."""
        checked = bool(state)
        self.param_values.setdefault(viz_name, {}).setdefault("channels", {})[gene] = checked
        self.log_pipeline(f"{viz_name} - {gene} channel: {'on' if checked else 'off'}")

        refresh_callbacks = getattr(self, '_probe_refresh_callbacks', {})
        if viz_name in refresh_callbacks:
            refresh_callbacks[viz_name]()

    # Parameter Builders
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
            lambda val, cat=category, pname=name, vlabel=value_label: self._on_param_changed(cat, pname, val, vlabel)
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
            lambda val, cat=category, pname=name: self._on_param_changed(cat, pname, val, None)
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
            "color: #A0A0A0; font-size: 11px;"
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
        curve = plot.plot([], [], pen=pg.mkPen("#F2A93B", width=2), symbol="o",
                         symbolBrush="#E34A4A", symbolSize=6)
        layout.addWidget(plot)

        start_btn.clicked.connect(self.viewer.aer_selector.start)
        clear_btn.clicked.connect(self.viewer.aer_selector.clear)

        def update_plot(points):
            if not points:
                curve.setData([], [])
                return
            pts = np.array(points)
            curve.setData(pts[:, 0], pts[:, 2])

        self.viewer.aer_selector.points_changed.connect(update_plot)
        confirm_btn.clicked.connect(self._confirm_aer_selection)

    def _confirm_aer_selection(self):
        """Confirm AER selection."""
        points = self.viewer.aer_selector.points
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

    def _add_limb_reference_param(self, layout, category, param, stored):
        """Add limb reference alignment controls."""
        stored.setdefault("reference_choice", None)
        stored.setdefault("apply_all_channels", False)
        stored.setdefault("show_reference", False)

        ref_label = create_label(
            "Chosen stage reference",
            "color: #A0A0A0; font-size: 12px; font-style: italic; padding: 5px 0px; border-top: 1px solid #2A2A2A;"
        )
        layout.addWidget(ref_label)

        reference_combo = QComboBox()
        reference_options = [
            "Stage 20 - E10.5 reference", "Stage 22 - E11.5 reference",
            "Stage 24 - E12.5 reference", "Stage 26 - E13.5 reference"
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
            lambda checked, cat=category: self._on_apply_all_toggled(cat, checked, style_apply_btn)
        )
        layout.addWidget(apply_all_btn)

        reset_btn = create_styled_button("Reset", "#4B2E83", "#5C3A9E")
        reset_btn.clicked.connect(
            lambda: self._reset_reference_alignment(category, reference_combo, apply_all_btn, style_apply_btn)
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
        self.log_pipeline(f"{category} - apply to all channels: {'on' if checked else 'off'}")

    def _on_show_reference_toggled(self, category, state):
        checked = bool(state)
        self.param_values.setdefault(category, {})["show_reference"] = checked
        self.log_pipeline(f"{category} - show reference in viz: {'on' if checked else 'off'}")

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
            self, "Confirm alignment",
            f"Confirm manual alignment with reference '{reference}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.log_pipeline(f"{category} - alignment confirmed against '{reference}'.")

    # Button Actions
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
        about.triggered.connect(lambda: webbrowser.open('https://www.embl.org/groups/sharpe/'))
        menu.addAction(about)

        self._build_contact_menu(menu)

        button.setMenu(menu)
        return button

    def _click_threebuttons(self, path, button):
        """Handle three-dots button click for experiment actions."""
        menu = QMenu(self)
        menu.setStyleSheet(SECMENU_STYLE)

        delete_act = QAction('Delete')
        delete_act.triggered.connect(lambda: self._delete_selected_experiments(path))
        menu.addAction(delete_act)

        rename_act = QAction('Rename')
        rename_act.triggered.connect(lambda: self._rename_experiment(path))
        menu.addAction(rename_act)

        details_act = QAction('Details')
        details_act.triggered.connect(self.menu_button_clicked)
        menu.addAction(details_act)

        download_act = QAction('Download .tiff')
        download_act.triggered.connect(self.menu_button_clicked)
        menu.addAction(download_act)

        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def _delete_selected_experiments(self, checked=False):
        """Delete selected experiments."""
        if not hasattr(self, 'experiment_checkboxes') or not self.experiment_checkboxes:
            return

        selected = [path for path, cb in self.experiment_checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Nothing selected", "Please check an experiment to delete.")
            return

        reply = QMessageBox.question(
            self, "Delete experiment",
            f"Delete {len(selected)} selected experiment(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for path in selected:
            self.experiments.remove(path)

        if hasattr(self, 'filepath') and self.filepath in selected:
            self.filepath = None

        self.navigate_to(self.show_exp)

    def _rename_experiment(self, path):
        """Rename an experiment."""
        current_name = self.experiment_names.get(path, os.path.basename(path))
        new_name, ok = QInputDialog.getText(
            self, "Rename experiment", "New name:", text=current_name
        )
        if ok and new_name.strip():
            self.experiment_names[path] = new_name.strip()
            self.show_exp()

    def _png_to_dummy_volume(self, filepath, depth=10, size=64):
        """Convert PNG to dummy 3D volume for testing."""
        img = Image.open(filepath).convert("L")
        img = img.resize((size, size))
        arr = np.array(img)
        return np.stack([arr] * depth, axis=0)

    # Public Methods
    def getfilename(self):
        """Handle file selection dialog."""
        file_filter = 'Images (*.png *.jpg *.jpeg)'
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self, caption='Select a .tiff file',
            directory=os.getcwd(), filter=file_filter,
            initialFilter=file_filter
        )
        if not filepath:
            return

        if not filepath.lower().endswith((".png", ".jpg", ".jpeg")):
            QMessageBox.warning(self, "Invalid file", "Please select a .tiff file (a png image for trial).")
            return

        if filepath not in self.experiments:
            self.experiments.append(filepath)

        self.navigate_to(self.show_exp)

        

    def addexp_button_clicked(self, checked=False):
        """Add experiment button handler."""
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self, caption='Select an image!',
            directory=os.getcwd(), filter='Images (*.png *.jpg *.jpeg)'
        )
        if not filepath:
            return

        if not filepath.lower().endswith((".png", ".jpg", ".jpeg")):
            QMessageBox.warning(self, "Invalid file", "Please select an image file.")
            return

        if filepath not in self.experiments:
            self.experiments.append(filepath)

        self.navigate_to(self.show_exp)

    def saveexp_button_clicked(self):
        """Save experiment button handler."""
        print(True)

    def viewexp_button_clicked(self):
        """View experiment button handler."""
        selected = [path for path, cb in self.experiment_checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")
            return

        self.filepath = selected[0]
        self.navigate_to(self.show_viz)

    def menu_button_clicked(self, s):
        """Placeholder for menu button clicks."""
        print("click", s)

    def log_pipeline(self, message):
        """Add a message to the pipeline log."""
        self.pipeline_log.append(message)
        if hasattr(self, 'pipeline_log_widget'):
            self.pipeline_log_widget.setText("\n".join(self.pipeline_log[-10:]))


# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()

import numpy as np
import pyqtgraph.opengl as gl
from limblab.design import theme
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def create_styled_button(
    text: str,
    color: str | None = None,
    hover_color: str | None = None,
    size: int | None = None,
):
    """Create a styled push button with consistent styling."""
    if color is None:
        color = theme("palette.primary", "#0D7C66")
    if hover_color is None:
        hover_color = theme("palette.primaryHover", "#41B3A2")

    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: {theme("palette.textPrimary", "#FFFFFF")};
            font-weight: {theme("typography.fontWeightBold", "bold")};
            font-size: {theme("typography.fontSizeLarge", 18)}px;
            border-radius: {theme("shape.borderRadiusButton", "20px")};
            padding: {theme("layout.spacingBase", "10px")} {theme("layout.spacingLarge", "30px")};
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


def create_slider(min_val, max_val, default_val, color=None):
    """Create a styled slider."""
    if color is None:
        color = theme("palette.primary", "#0D7C66")
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
            background: {theme("palette.textPrimary", "#FFFFFF")}; border: 1px solid #5c5c5c;
            width: 18px; margin: -2px 0; border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{ background: {theme("palette.primaryHover", "#41B3A2")}; }}
        QSlider::sub-page:horizontal {{ background: {color}; border-radius: 4px; }}
        QSlider::add-page:horizontal {{ background: {theme("palette.panel", "#2A2A2A")}; border-radius: 4px; }}
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
    toggle_button.setArrowType(
        Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
    )
    toggle_button.setStyleSheet(f"""
        QToolButton {{
            background-color: {theme("palette.panel", "#2A2A2A")}; color: {theme("palette.textPrimary", "#FFFFFF")};
            font-weight: {theme("typography.fontWeightBold", "bold")}; font-size: {theme("typography.fontSizeBase", 14)}px;
            border: none; padding: {theme("layout.spacingBase", "10px")} {theme("layout.spacingBase", "10px")}; text-align: left;
        }}
        QToolButton:hover {{ background-color: {theme("palette.surfaceAlt", "#333333")}; }}
    """)
    toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    content_widget.setVisible(expanded)
    content_widget.setStyleSheet(f"background-color: {theme('palette.panelAlt', '#181818')};")

    def on_toggle(checked):
        content_widget.setVisible(checked)
        toggle_button.setArrowType(
            Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        )

    toggle_button.toggled.connect(on_toggle)
    section_layout.addWidget(toggle_button)
    section_layout.addWidget(content_widget)
    return section


def create_back_button(callback):
    """Create a back button with consistent styling."""
    back_button = QPushButton("←")
    back_button.setFixedSize(30, 30)
    back_button.setCursor(Qt.CursorShape.PointingHandCursor)
    back_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {theme('palette.panel', '#2A2A2A')}; color: {theme('palette.textPrimary', '#FFFFFF')};
            font-size: 15px; border-radius: 15px;
        }}
        QPushButton:hover {{ background-color: {theme('palette.primaryHover', '#41B3A2')}; }}
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
            meshdata=md,
            smooth=True,
            color=(0.4, 0.6, 1.0, 1.0),
            shader="shaded",
            glOptions="opaque",
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
            vol = vol / max_val * 255
        vol = vol.astype(np.ubyte)

        rgba = np.zeros(vol.shape + (4,), dtype=np.ubyte)
        rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = rgba[..., 3] = vol

        self.volume_item = gl.GLVolumeItem(rgba)
        self.volume_item.translate(
            -vol.shape[0] / 2, -vol.shape[1] / 2, -vol.shape[2] / 2
        )
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

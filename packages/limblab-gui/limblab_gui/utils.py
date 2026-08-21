
import webbrowser

import numpy as np
import pyqtgraph.opengl as gl
from config import *
from limblab.design import theme
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QLabel,
    QMenu,
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


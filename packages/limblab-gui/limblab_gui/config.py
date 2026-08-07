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
        {
            "name": "Voxel spacing",
            "type": "slider",
            "min": 0,
            "max": 255,
            "default": 30,
        },
        {
            "name": "Gaussian smoothing",
            "type": "spinbox",
            "min": 0,
            "max": 10,
            "default": 0,
        },
        {
            "name": "Strip background noise",
            "type": "spinbox",
            "min": 0,
            "max": 10,
            "default": 0,
        },
        {
            "name": "Low-pass filter",
            "type": "spinbox",
            "min": 0,
            "max": 10,
            "default": 0,
        },
    ],
    "Surface": [
        {
            "name": "Surface extraction",
            "type": "spinbox",
            "min": 0,
            "max": 1,
            "default": 0,
        },
        {"type": "text", "default": "Select isovalue"},
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
        {
            "name": "Number of isosurfaces",
            "type": "slider",
            "min": 0,
            "max": 10,
            "default": 3,
        },
        {"name": "Threshold", "type": "slider", "min": 0, "max": 10, "default": 1},
    ],
    "Slices": [
        {"type": "text", "default": "2D Plane sliders"},
        {"name": "X", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Y", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"name": "Z", "type": "slider", "min": 0, "max": 10, "default": 8},
        {"type": "text", "default": "Color map - redefine widget type"},
    ],
    "Raycast": [
        {"type": "text", "default": "Opacity"},
        {"name": "Hoxa11", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Sox9", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"name": "BMP2", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"name": "Limb surface", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"type": "text", "default": "Colour mapping - redefine widget type"},
    ],
    "Probe": [
        {
            "type": "text",
            "default": "Make a line through the limb to see the selected gene intensity values across",
        },
        {"name": "probe_line", "type": "probe_line"},
    ],
    "2D Projection Slab": [
        {"type": "text", "default": "Slab projection"},
        {"name": "Slab Max Value", "type": "slider", "min": 0, "max": 10, "default": 3},
        {"name": "Slab Min Value", "type": "slider", "min": 0, "max": 10, "default": 1},
        {"type": "text", "default": "Mean slab projection:"},
    ],
}

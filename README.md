<!-- ![Alt text](assets/logo.png "LimbLab") -->
<p align="center">
  <img src="docs/assets/header-white.png" alt="Alt text">
</p>
<p align="center"><strong>Work fast, code less.</strong> Analyze your 3D limb data with ease. Aesthetic out of the box.</p>

---------
**Documentation:** https://limblab.embl.es/docs

**Source Code:** https://github.com/lauavinyo/limblab

---------

# LimbLab

LimbLab is a Python package and command-line tool for preprocessing, staging, aligning, and visualizing 3D limb imaging data. It is designed for mouse limb models and combines automated pipelines with interactive visualization powered by Vedo. 
** THIS HAS CHANGED A LOT!!! ** 
README underconstruction! 

## WARNINGS
Currently morphing is not active. 
There VTK >= 9.3 does not allow it with the current code and needs a re-implementation. 

# Development 

## Building the macOS App

### Prerequisites
- Python environment with dependencies installed (`pip install -r requirements.txt` or equivalent)
- `pyinstaller` installed in your venv (`pip install pyinstaller`)

### Build

From the repo root (`limblab-gui/`):

```bash
source .venv/bin/activate
pyinstaller --noconfirm LimbLab.spec
```

The `.app` bundle is generated at: `dist/LimbLab.app`

### Test the build

Run from Terminal (not double-click) to catch errors:

```bash
./dist/LimbLab.app/Contents/MacOS/LimbLab
```

### Notes
- Config lives in `LimbLab.spec` — edit there for icon, bundle ID, hidden imports, etc.

# License

Licensed under the terms of the project license.

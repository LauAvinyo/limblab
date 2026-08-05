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

LimbLab is a Python package and command-line tool for preprocessing, staging, aligning, and visualizing 3D limb imaging data. It is designed for mouse limb models and combines automated pipelines with interactive visualization powered by Vedo. Gemma ha estat aqui

## What LimbLab Does

- Preprocess 3D volume data (`clean_volume`)
- Extract surface meshes from DAPI volumes (`extract_surface`)
- Stage limbs interactively and align them to reference templates
- Perform rigid and non-linear morphing alignment
- Render high-quality visualizations using 3D isosurfaces, raycasting, slabs, slices, and probe views
- Offer a CLI with the same API as the Python package

## Installation

Install the published package from PyPI:

```bash
pip install limblab
```

If you are working on the repository locally, use Poetry to install dependencies:

```bash
cd /Users/laura/limblab
poetry install
```

## Quick Start

```python
import limblab

limblab.create_experiment("my_experiment", "./experiments/")
limblab.clean_volume("./experiments/my_experiment", "raw_data.tif", "DAPI")
limblab.extract_surface("./experiments/my_experiment", auto=True)
limblab.stage_limb("./experiments/my_experiment")
limblab.align("./experiments/my_experiment")
limblab.one_channel_isosurface("./experiments/my_experiment", "DAPI")
```

## Core Functions

- `create_experiment(experiment_folder_path, experiment_name)` — initialize experiment structure with `pipeline.log`
- `clean_volume(experiment_folder_path, raw_volume, channel, **kwargs)` — preprocess the volume with thresholding, smoothing, and filtering
- `extract_surface(experiment_folder_path, isovalue=None, auto=False)` — create a 3D surface mesh from DAPI volume
- `stage_limb(experiment_folder_path, limb_stager=None)` — interactive limb staging using 3D spline fitting
- `rotate_limb(experiment_folder_path)` — align limb with a reference template using rigid transformation
- `morph_limb(experiment_folder_path)` — perform non-linear morphing alignment

## Visualization Functions

- `one_channel_isosurface(experiment_folder_path, channel)` — 3D surface rendering for a single channel
- `two_chanel_isosurface(experiment_folder_path, channel1, channel2)` — dual channel 3D surface rendering
- `dynamic_slab(experiment_folder_path, channel)` — interactive slab visualization with dynamic slicing
- `probe(experiment_folder_path, channels)` — interactive probe visualization for multiple channels
- `raycast(experiment_folder_path, channel)` — volume raycasting for high-quality rendering
- `slices(experiment_folder_path, channel)` — 2D slice visualization with navigation controls
- `arbitary_slice(experiment_folder_path, channel1, channel2)` — arbitrary plane slicing for dual channels

## Utility Functions

- `load_pipeline(experiment_folder_path)` — load and parse experiment pipeline data
- `file2dic(file_path)` — read key/value pairs from a file
- `dic2file(dictionary, file_path)` — write dictionary to a key/value file format
- `closest_value(lst, value)` — find the closest value in a sorted list
- `get_reference_limb(stage, side, position)` — get the path to a reference limb template
- `interpolate_colors(color1, color2, steps)` — generate a gradient between two colors
- `pick_evenly_distributed_values(array, n_values)` — select evenly distributed values from an array

## Custom Parameters

Use optional parameters to fine-tune volume cleaning:

```python
limblab.clean_volume(
    experiment_path,
    volume_path,
    "DAPI",
    gaussian_sigma=(8, 8, 8),
    frequency_cutoff=0.03,
    low_res_size=(1024, 1024, 296),
)
```

## CLI Usage

LimbLab provides a CLI command called `limb` with the same functionality as the Python API.

```bash
limb create-experiment my_experiment ./experiments/
limb clean-volume ./experiment ./volume.tif DAPI
limb clean-volume ./experiment ./volume.tif DAPI --sigma 8,8,8 --cutoff 0.03 --size 1024,1024,296
limb extract-surface ./experiment --auto
limb stage ./experiment
limb align ./experiment
limb align ./experiment --morph
limb vis isosurfaces ./experiment DAPI
limb vis isosurfaces ./experiment DAPI GFP
limb vis raycast ./experiment DAPI
limb vis slices ./experiment DAPI GFP
limb vis slab ./experiment DAPI
limb vis probe ./experiment DAPI GFP RFP
```

### CLI Options

- `--sigma` — Gaussian smoothing parameters as `x,y,z` (default `6,6,6`)
- `--cutoff` — low-pass filter frequency cutoff (default `0.05`)
- `--size` — output volume size as `x,y,z` (default `512,512,296`)
- `--auto` — automatically determine parameters for surface extraction
- `--morph` — perform non-linear morphing instead of rigid transformation

Run `limb <command> --help` for per-command usage details.

> Windows note: Vedo / VTK may not work reliably in WSL. Make sure your Python `Scripts` directory is on `PATH` if you use Windows.

## Documentation

This repository uses MkDocs Material for documentation.

To build locally:

```bash
pip install mkdocs-material
mkdocs build
```

To preview locally:

```bash
mkdocs serve
```

Then open `http://127.0.0.1:8000` in your browser.

To publish documentation to GitHub Pages:

```bash
mkdocs gh-deploy --force
```

The GitHub Actions workflow at `docs/.github-workflows-ci.yml` also deploys documentation automatically on pushes to `master` / `main`.

## Package Publishing

Packaging is configured with Poetry in `pyproject.toml`.

Build a package:

```bash
poetry build
```

Publish to PyPI with Poetry using an API token:

```bash
poetry config pypi-token.pypi <YOUR_PYPI_TOKEN>
poetry publish --build
```

Alternatively, build and upload with Twine:

```bash
poetry build
pip install twine
twine upload dist/*
```

## Development

If you are contributing or modifying the repository, install dependencies with Poetry:

```bash
poetry install
```

Run tests and verify functionality before publishing.

## License

Licensed under the terms of the project license.

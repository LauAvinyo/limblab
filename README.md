# Secret Project

Run this: 

pip install -U git+https://github.com/marcomusy/vedo.git

## Pipeline HCR 

The pipeline assumes the user has at least two `.tif` volumes, one with the DAPI channel and one with the Sox9 channel.
With @Heura's nomenclature.

`00.make_folder.py`
The first script receives the DAPI channel and creates a working folder with the name of the experiment (extracted from the input file) and a pipeline file that will be used to write the paths to the generated files and values used for that particular experiment. 

`01.clean_volume.py`
This script receives a `.tif` volume and generates a properly spaced `.vti`.

> [!NOTE]
> Remember you have to run it for each of the channels.

`20.select_isovalue.py`
[Optional] To extract the surface from the DAPI channel, we use the vedo's isosurface browser to select the value. Once the viewer is closed, the script saves the value on the pipeline file. 

`21.extract_surface.py`
Using the selected value on the previous step or the most common value of the DAPI histogram.

`30.staging.py`
This is the 3D staging system. It uses the extracted DAPI surface to stage the limb. The user has to manually click the AER. The script saves the stage on the pipeline file.

`40.morphing.py`
Using the extracted surface from the DAPI and the _Canonical 3D surface_ for that stage the user has to manually click the morphing points. The script stores the non-linear transformation needed for the morphing and it does store the path in the pipeline file.

> [!IMPORTANT]
> The user needs to get the reference limbs!


`50.dynamic_slab.py`
The user can select the upper and lower bounds of the slab. 

> [!WARNING]
> For now we just do the mean projection of the slab 





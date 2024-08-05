# Sox9 and BMP2 Pipeline

Here you can find a detailed exploration of HCR data showcasing Sox9 and BMP2 expression using our pipeline. We will follow the same steps as in the other tutorial now with a specific focus on examining the gene expression overlap between Sox9 and BMP2 genes.

## Objective

Our aim is to investigate the HCR (Hybridization Chain Reaction) data to observe the spatial distribution of Sox9 and BMP2 expression. Analyzing these genes in three dimensions can reveal their interaction and roles in limb development more accurately than traditional 2D projections (2D sections may arguable be the best technique tho).

## Pipeline Overview

The initial data required for this study is located in the `example_data/sox9_bmp2_raw_data` directory. This directory contains TIFF volumes for both Sox9 and BMP2 channels.

### Initial Setup

To maintain the integrity of your raw data, start by creating a new experiment folder separated from it. Execute the following command:

```sh
limb create-experiment case_studies/sox9_bmp2_pipeline
```

You'll be prompted to enter details about the limb, such as whether it's a Forelimb or Hindlimb, Left or Right side, and the microscope's spacing parameters. For this demonstration, we use: Left, Forelimb, with a default spacing value of 0.65 0.65 2.

Your `pipeline.log` file should now resemble:

```txt
BASE ./case_studies/sox9_bmp2_pipeline
SIDE L
POSITION F
SPACING 0.65 0.65 2.0
```

### Cleaning the Volumes

The next step involves preparing the volumes, beginning with the DAPI channel. Cleaning involves removing noise to get a clear structure of the limb. Execute the command:

```sh
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_dapi_405_LF.tif dapi
```

A plotter will prompt you to select isovalues to clip the volume, eliminating noise. Confirm the smoothness of the volume afterward. Repeat the procedure for the Sox9 and BMP2 channels:

```sh
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_sox9_594_LF.tif sox9
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_bmp2_647_LF.tif bmp2
```

**Note:** This step requires patience as careful selection of isovalues is critical.

### Limb Analysis

Proceed with the following steps to analyze the limb:

1. **Extract the Limb Surface**
2. **Stage the Limb**
3. **Align the Limb with a Reference**

#### Extracting the Surface

Surface extraction creates a 3D model of the limb, essential for further analysis since, trying to align volumes to references will be very computationally consuming. Initiate the process by running:

```sh
limb extract-surface case_studies/sox9_bmp2_pipeline/
```
You will be able to notice that this isosurface is not very beautiful, real life experiments. We are working on a a way to clean it surface through with this pipeline. Do not hesitate to contact us about how to do this. For now, we have shared a clean version of the surface using blender. For the code to use it in you next step, please, add the next line to your pipeline.log file. 
You can do it by: 
```sh
echo 'BLENDER HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk' >> case_studies/sox9_bmp2_pipeline/pipeline.log
cp example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk case_studies/sox9_bmp2_pipeline 
```


#### Staging the Limb

Staging involves determining the developmental stage of the limb. Execute:

```sh
limb stage case_studies/sox9_bmp2_pipeline/
```

A plotter will appear where you mark the limb's contour. Click 's' to determine the stage. This process generates key files and images depending on whether you're using a local or server version.

#### Aligning the Limb

Aligning the limb ensures it matches a reference model for precise analysis. You have two methods:

1. **Linear Transformation** (rotation and scaling)
2. **Non-Linear Transformation** (morphing)


```sh
limb stage case_studies/sox9_bmp2_pipeline/ --morph
```

### Visualizing Gene Expression

Visualization helps interpret the data, providing a clear graphical representation of gene expression.

#### Viewing Isosurfaces

Let's visualize the isosurfaces for both genes at the same time. Visualize them by running:

```sh
limb vis isosurfaces case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

If the isosurfaces are not precomputed, a plotter will help you select appropriate isovalues for visualization.

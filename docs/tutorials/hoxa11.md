
# Hoxa11 Pipeline

Welcome to the comprehensive guide on analyzing HCR with Hoxa11 expression using our advanced pipeline. This guide is tailored for researchers looking to delve deeper into 3D gene expression data, specifically focusing on the Hoxa11 gene in mouse limb models. By following this guide, you will gain a thorough understanding of how to set up, clean, analyze, and visualize 3D limb data effectively.

## The Goal

The primary objective of this guide is to analyze HCR (Hybridization Chain Reaction) with Hoxa11 expression. This is particularly interesting because the traditional 2D projection may not accurately represent the gene expression in a 3D context. Understanding the 3D spatial distribution of Hoxa11 can provide deeper insights into its role and functionality in limb development.

## The Pipeline

The raw data required for this analysis can be found in the `example_data/hoxa11_raw_data` directory. This folder contains the TIFF volumes for both Hoxa11 and DAPI channels.

### Setting Up the Experiment

Before starting the analysis, it's crucial to set up a new experiment to ensure the raw data remains unaltered. To do this, run the following command:

```sh
limb create-experiment case_studies/hoxa11_pipeline
```

This command generates a log file for the experiment and prompts the user to input details about the limb, such as whether it's a Forelimb or Hindlimb, Left or Right side, and the microscope spacing. For our example, the inputs are as follows: Left, Hindlimb, with a default spacing value of 0.65 0.65 2. 

The log file `pipeline.log` will help in tracking the experiment settings and ensuring reproducibility. Your `pipeline.log` file should now look like this:

```txt
BASE ./case_studies/hoxa11_pipeline
SIDE L
POSITION H
SPACING 0.65 0.65 2.0
```

### Volume Clean-Up

The next step is to clean up the volumes, starting with the DAPI channel. Cleaning up involves removing noise and irrelevant data to get a clear representation of the limb's structure. This process includes selecting isovalues to clip the volume.

To clean the DAPI volume, use the following command:

```sh
limb clean-volume case_studies/hoxa11_pipeline example_data/hoxa11_raw_data/HCR11_HOXA11_l1_dapi_488_LH.tif dapi
```

A plotter will appear, prompting you to select the top and bottom isovalues. This helps in clipping the volume to eliminate noise. After smoothing, confirm that everything looks fine. Repeat the process for the Hoxa11 channel:

```sh
limb clean-volume case_studies/hoxa11_pipeline example_data/hoxa11_raw_data/HCR11_HOXA11_l1_hoxa11_647_LH.tif hoxa11
```

**Note:** This step is time-consuming as it involves careful selection and verification of isovalues to ensure data integrity.

### Analyzing the Limb

To analyze the limb, follow these steps:

1. **Extract the Limb Surface**
2. **Stage the Limb**
3. **Align the Limb to a Reference Limb**

#### Surface Extraction

Surface extraction involves creating a 3D representation of the limb's surface, which is crucial for further analysis. Run the following command to start the process:

```sh
limb extract-surface case_studies/hoxa11_pipeline/
```

If you don't specify an isovalue, a plotter will prompt you to select the appropriate isovalue manually. This ensures that the surface extraction is based on the correct data points.

#### Stage the Limb

Staging the limb involves determining its developmental stage based on its morphology. To stage the limb, use the command:

```sh
limb stage case_studies/hoxa11_pipeline/
```

A plotter will appear where you can click on the limb's contour. After clicking 's', the limb's stage will be determined. This process involves selecting key morphological points which are then used to calculate the stage of the limb.

Depending on whether you're using a local or server version, this will generate:

1. A file with the measured points
2. A file with the fit line
3. An image with the results (local version)

#### Align the Limb

Alignment ensures that the limb's data is comparable to a reference model, which is essential for accurate analysis. You have two options for alignment:

1. **Linear Transformation** (rotation and scaling)
2. **Non-Linear Transformation** (morphing)

For this example, we will use a linear transformation. This involves rotating and scaling the limb to match the reference model, making it easier to compare and analyze the data.

### Visualizing the Limb Expression

Visualization helps in interpreting the data by providing a clear, graphical representation of the gene expression.

#### Visualize the Isosurfaces

Isosurfaces represent surfaces of constant value within the volume data. To visualize the isosurfaces, run:

```sh
limb vis isosurfaces case_studies/hoxa11_pipeline HOXA11
```

If the isosurfaces have not been computed yet, a plotter will prompt you to select the top and bottom isovalues, enabling you to customize the visualization according to your needs.

#### Visualize the Slab

To visualize the 2D projection using the dynamic slab, use:

```sh
limb vis slab case_studies/hoxa11_pipeline HOXA11
```

This command provides a dynamic view of the data, allowing you to observe the gene expression in a 2D context while retaining the depth information from the 3D data.


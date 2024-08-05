Certainly! Below is the revised text with "limb" in place of "your_script.py":

# Command Documentation: `vis`

The `vis` command is the tool for visualizing 3D limbs, offering a range of algorithms tailored to various analysis needs. This command plays a crucial role in transforming raw data into meaningful visual representations.

!!! tip
    We are developing more visualitzation algorithms! Keep posted.

To utilize the `vis` command effectively, specify the desired visualization algorithm, provide the path to your experiment data, and list the channels you want to visualize. Each algorithm is optimized for different types of visualizations. Currently you can visualize isoseufaces, slabs, raycast, probe and slices of your volumes.

## Visualization Algorithms

### Isosurface Visualization

The isosurface algorithm is used to render three-dimensional surfaces within a volume of data, highlighting specific features or regions of interest. Depending on your needs, you can choose to visualize one or two channels, just by setting the channel(s). If the number of channels provided is not as expected (one or two), a `NotImplementedError` will be raised to ensure valid configurations.

```bash
limb vis isosurface /data/experiment/ channel_1 (channel_2)
```

### Raycast Visualization

The raycasting algorithm generates a two-dimensional projection from a three-dimensional dataset by projecting data along a specified direction. This technique is excellent for visualizing internal structures and data distribution within the volume. Since raycasting supports only one channel at a time, a warning will be issued if multiple channels are specified, and the first channel in the list will be used for the projection. This method is useful for creating projections that reveal internal features or patterns within a 3D model.

```bash
limb vis raycast /data/experiment/ channel_1
```

### Slices Visualization

   The slices algorithm creates two-dimensional cross-sections from a three-dimensional dataset, producing multiple 2D slices at various depths. This allows users to examine different planes within the data volume, providing a detailed view of the structural organization across various sections. For example, slices can be used to investigate internal layers or planes within a 3D model.

```bash
limb vis slices /data/experiment/ channel_1
```

### Probe Visualization

The probe algorithm enables interactive exploration of specific points or regions within the 3D data. This feature is valuable for extracting detailed information from selected areas of interest. By focusing on one channel, the `probe` function allows for detailed examination of points or regions, which is essential for analyzing gene expression levels or other features at specific locations within the tissue.

```bash
limb vis probe /data/experiment/ channel_1
```

### Slab Visualization

The slab algorithm visualizes a subset of the data within a defined slab or section of the 3D volume. This method helps users focus on specific layers or regions, providing a clearer view of particular sections. The `slab` function, which operates on one channel, enables users to create a focused view within a defined section of the dataset, highlighting features within a particular layer of a 3D structure.

```bash
limb vis slab /data/experiment/ channel_1
```


# Styles

**TLDR;** The `customization.py` file is designed to provide users with the ability to adjust the visual aspects of the application to better meet their preferences or requirements. This file contains a dictionary named `styles` as well that outlines various parameters for customizing colors, transparencies, and positions of different elements in the application.

!!! warning
    This is still in development. Maybe unreliable.

### Understanding the Styles Dictionary

The `styles` dictionary within the file is structured to define a range of visual attributes for different elements. Here’s a detailed look at how you can utilize and modify these settings.

**Color Schemes** are defined by keys `0` and `1`. These keys correspond to pairs of color values that can be used to apply a specific color theme across different components of the application. For example, key `0` is associated with a light blue color (`#9ce4f3`) and a dark blue color (`#128099`), while key `1` pairs a light pink (`#ec96f2`) with a dark purple (`#c90dd6`). You can use them for different channels for instance. 

**Positions** for various UI elements are specified under the `postions` key (mainly sliders). This includes the `number` and `values` coordinates, which dictate where numerical and value indicators should appear within the interface. The coordinates `[0.1, 0.25]` and `[0.2, 0.25]` are examples for positioning numerical indicators, whereas `[0.1, 0.1]` and `[0.2, 0.1]` are used for value indicators.


**Limb Appearance** settings are found under the `limb` key. This section allows you to adjust the color and transparency of limb models within the application. The `alpha` value of `0.1` ensures that the limb appears very transparent, while the color `#FF7F11` gives it an orange tint.

**Reference Appearance** is defined by the `reference` key, where `alpha` is set to `1`, indicating full opacity, and `color` is set to `1`, which typically represents white in RGB color space.

**Isosurfaces** customization is handled under the `isosurfaces` key. Here, the transparency levels for isosurfaces are specified. The `alpha` value of `0.3` adjusts the general transparency of isosurfaces, while `alpha-unique` at `0.8` applies a higher transparency level for unique or highlighted isosurfaces.

**User Interface (UI) Colors** are controlled by the `ui` key. The `primary` color (`#0d1b2a`) sets the main color scheme of the UI, while the `secondary` color (`#fb8f00`) is used for accent elements, providing a vibrant orange contrast to the primary dark blue.

### Applying Customizations

To change the appearance of different elements, you simply need to update the relevant values within this dictionary. For example, if you want to alter the limb color, you would modify the `color` attribute in the `limb` section. Similarly, adjusting the UI color scheme involves updating the `primary` and `secondary` colors under the `ui` key. 

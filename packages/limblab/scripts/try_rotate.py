from limblab.tools.align import rotate_limb
from limblab.models import Experiment


TEST_BASE_PATH = "/Users/laura/Desktop/Desktop-2026/sox9-fig-thesis/"
TEST_SURFACE_PATH = "HCR11_MEIS2_l1_dapi_488_LF_surface.vtk"


experiment = Experiment(
    experiment_id="manual_test",
    base=TEST_BASE_PATH,
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="F",
    position="L",
    species="mouse",
    surface=TEST_SURFACE_PATH,
    stage=260,
)

transformation_path = rotate_limb(experiment)
print(f"Transformation matrix saved at: {transformation_path}")

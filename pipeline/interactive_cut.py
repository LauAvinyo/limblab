
"""Interactively cut a mesh by drawing free-hand a spline in space"""
# The tool can also be invoked from command line e.g.: > vedo --edit mesh.ply
import vedo
from vedo.applications import FreeHandCutPlotter
import sys
from utils import file2dic
import os
from vedo import *

if len(sys.argv) != 3:
    print("Usage: python script_name.py folder_name channel")
    sys.exit(1)
folder = sys.argv[1]
channel = sys.argv[2]


# Get the paths
pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
path = pipeline[channel.upper()]


# This affects how colors are interpolated between points
settings.interpolate_scalars_before_mapping = True

s = Sphere()
s.color("white").alpha(0.25).backface_culling(True)
s.pointdata['scalars1'] = np.sqrt(range(s.npoints))
print(s)

# Pick a few points on the sphere
sv = s.vertices[[10, 15, 129, 165]]
pts = Points(sv).ps(12)

# Cut the loop region identified by the points
scut = s.clone().cut_with_point_loop(sv, invert=False).scale(1.01)
scut.cmap("Paired", "scalars1").alpha(1).add_scalarbar()
print(scut)

show(s, pts, scut, __doc__, axes=1, viewup="z")

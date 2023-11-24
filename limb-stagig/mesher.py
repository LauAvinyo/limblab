#!/usr/bin/env python3
#
"""
Generate meshes from line contours
"""
import numpy as np
from vedo import load, show, Axes, Line, Text2D, Spline

limbs = load("data/timecourse1d_lines/")
outdir = "output/newmeshes"

axe = Axes(xrange=(-1,6), yrange=(-2.7,2.3))

areas = []
for i, limb in enumerate(limbs):

    age = i + 241
    if age > 298: break
    # if age != 290: continue #test

    ln =  Line(limbs[i]).length()
    # print('line length=', ln)
    path = limbs[i].points().tolist()
    shape = Spline(path, res=int(np.sqrt(ln)*50))
    path = shape.points().tolist()

    # let's make a box to represent the flank, num is the resolution
    path += np.linspace(path[-1],       [0.0, -2.7, 0], num=10, endpoint=False).tolist()
    path += np.linspace([0.0, -2.7, 0], [-1., -2.7, 0], num=10, endpoint=False).tolist()
    path += np.linspace([-1., -2.7, 0], [-1.,  2.3, 0], num=50, endpoint=False).tolist()
    path += np.linspace([-1., 2.3, 0],  [0.0,  2.3, 0], num=10, endpoint=False).tolist()
    path += np.linspace([0.0, 2.3, 0],  path[0],        num=10, endpoint=False).tolist()
    path = list(reversed(path)) # flip line orientation

    # Generate the mesh
    ln = Line(path).clean()
    mesh = ln.generate_mesh().smooth()
    mesh.color("k4").lw(0.1).lc('p2')
    # mesh.write(f"{outdir}/mesh_{age}.vtk")
    # mesh.write("{outdir}/mesh_{age}.xml") # dolfin format

    txt = Text2D(__doc__+f"{outdir}/mesh_{age}.vtk")
    plt = show(mesh, txt, axe, interactive=False)
    plt.remove(txt)
    plt.render()

plt.interactive()




#!/usr/bin/env python3
# (vedo 2023.4.6)
from vedo import Mesh, Plotter, Points, Text2D, settings

"""
pressing 'c' clears the points
pressing 'd' deletes the last point
"""

################################################
settings.default_font = "Calco"
settings.enable_default_mouse_callbacks = False

################################################
def update():
    source_pts = Points(sources, r=12, c="purple5")
    target_pts = Points(targets, r=12, c="purple5")
    source_pts.name = "source_pts"
    target_pts.name = "target_pts"
    slabels = source_pts.labels2d("id", c="purple3")
    tlabels = target_pts.labels2d("id", c="purple3")
    slabels.name = "source_pts"
    tlabels.name = "target_pts"
    plt.at(0).remove("source_pts").add(source_pts, slabels)
    plt.at(1).remove("target_pts").add(target_pts, tlabels)
    plt.render()

    if len(sources) == len(targets) and len(sources) > 3:
        warped = limb.clone().warp(sources, targets)
        warped.name = "warped"
        # wpoints = points.clone().apply_transform(warped.transform)
        plt.at(2).remove("warped").add(warped)
        plt.render()

def click(evt):
    if evt.actor == limb:
        sources.append(evt.picked3d)
        limb.pickable(False)
        reference.pickable(True)
        msg0.text("->")
        msg1.text("now select a reference point")
    elif evt.actor == reference:
        targets.append(evt.picked3d)
        limb.pickable(True)
        reference.pickable(False)
        msg0.text("now select a limb point")
        msg1.text("<-")
    update()

def keypress(evt):
    global sources, targets
    if evt.keypress == "c":
        sources.clear()
        targets.clear()
        plt.at(0).remove("source_pts")
        plt.at(1).remove("target_pts")
        plt.at(2).remove("warped")
        limb.pickable(True)
        reference.pickable(False)
        update()
    elif evt.keypress == "d":
        n = min(len(sources), len(targets))
        sources = sources[:n-1]
        targets = targets[:n-1]
        limb.pickable(True)
        reference.pickable(False)
        update()
    elif evt.keypress == "q":
        plt.close()
        exit()

################################################
reference = Mesh("297.vtk").c("yellow5")
reference.cut_with_plane(origin=(1,0,0))
ref = reference.clone().pickable(False).alpha(0.5)
limb = Mesh("Limb_Surface.vtk").c("k5").alpha(0.8)

sources = []
targets = []
limb.pickable(True)
reference.pickable(False)

msg0 = Text2D("select a limb point", c='white', bg="blue4", alpha=1, pos="bottom-center")
msg1 = Text2D(c='white', bg="blue4", alpha=1, pos="bottom-center")

clicked = []
plt = Plotter(N=3, axes=0, sharecam=0, size=(2490, 810))
plt.add_callback("click", click)
plt.add_callback("keypress", keypress)
plt.at(0).show("Limb", limb, msg0)
plt.at(1).show(f"Reference {reference.filename}", msg1, reference)
cam = plt.renderers[1].GetActiveCamera()
plt.at(2).show("Aligment Output", ref, camera=cam, bg="k9")
plt.interactive()
plt.close()

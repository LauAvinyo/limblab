#!/usr/bin/env python3
#
import argparse
import os
from datetime import datetime

import numpy as np
from vedo import (
    Line,
    Picture,
    Plotter,
    Points,
    Spline,
    Text2D,
    grep,
    precision,
    printc,
    settings,
    vector,
)

version = "0.3"
blackandwhite = True

# Parse user command line input
pr = argparse.ArgumentParser(description="GENE MAPPER - version 0.1")
pr.add_argument(
    "-i",
    "--image",
    type=str,
    help="Input image",
    default="data/hoxa11/selectiontrans/11-15.png",
    metavar="",
)
pr.add_argument(
    "-o", "--output", type=str, default="", help="output file name", metavar=""
)
pr.add_argument(
    "-g", "--gene-name", type=str, default="", help="gene shortcut name", metavar=""
)
pr.add_argument(
    "-e",
    "--executable",
    type=str,
    default="src/limbstager",
    help="limb staging system executable",
    metavar="",
)
pr.add_argument(
    "-s",
    "--staging-file",
    type=str,
    default="",
    help="reuse limb staging system output file",
    metavar="",
)
pr.add_argument(
    "-t",
    "--timecourse",
    type=str,
    default="data/timecourse1d",
    help="timecourse mesh directories",
    metavar="",
)
args = pr.parse_args()

if not args.gene_name:  # some automatic guessing of the gene name
    gene_name = "Unknown"
    fl = args.image.lower()
    if "hoxa11" in fl:
        gene_name = "HOXA11"
    if "hoxd13" in fl:
        gene_name = "HOXD13"
    if "sox9" in fl:
        gene_name = "SOX9"
    if "meis" in fl:
        gene_name = "MEIS"
    if "smad4" in fl:
        gene_name = "SMAD4"
    # printc("WARNING! Specify the gene name with option -g. Assuming:", gene_name, c='y')
else:
    gene_name = args.gene_name

limbstager_file = args.staging_file
if not args.staging_file:  # some automatic picking of previous staging points
    sf = (
        "output/"
        + gene_name.lower()
        + "/"
        + os.path.basename(args.image).split(".")[0]
        + ".txt"
    )
    if os.path.isfile(sf):
        limbstager_file = sf
    sf = os.path.basename(args.image).split(".")[0] + ".txt"
    if os.path.isfile(sf):
        limbstager_file = sf

if not args.output:
    outfile = os.path.basename(args.image)
    outfile = (
        outfile.replace(".png", ".txt").replace(".jpg", ".txt").replace(".jpeg", ".txt")
    )
    outfile = (
        outfile.replace(".PNG", ".txt").replace(".JPG", ".txt").replace(".JPEG", ".txt")
    )
else:
    outfile = args.output

infile = args.image
limbstager_exe = args.executable
limbs_dir = args.timecourse
staging_data_tab = "../stagings_data.tab"


# Callback functions
def update():
    global spline, points
    plt.remove([spline, points, txtpred])
    points = Points(cpoints, r=8).c("violet").z(1)
    spline = None
    if len(cpoints) > 2:
        spline = Spline(cpoints, closed=False).c("orange7").z(1)
    plt.add([points, spline])


def leftClick(evt):
    if not evt.actor:
        return
    cpt = vector(evt.picked3d) + [0, 0, 1]
    if precision(cpt[:2], 4) == "NaN":
        return
    cpoints.append(cpt)
    printc(f"Added point: {precision(cpt[:2],4)}  n={len(cpoints)}", c="g")
    update()


def rightClick(evt):
    if not evt.actor or len(cpoints) == 0:
        return
    p = cpoints.pop()
    plt.actors.pop()
    printc(f"Deleted point: {precision(p[:2],4)}  n={len(cpoints)}", c="r")
    update()


def keypress(evt):
    global spline, points, txtpred, ageh, isRight

    if evt.keypress == "c":  # CLEAR
        plt.remove(ssys_splines + [spline, points, txtpred]).render()
        ssys_splines.clear()
        cpoints.clear()
        points, spline = None, None
        printc("==== Cleared all points ====", c="r")

    elif evt.keypress == "s":  # STAGE
        if len(cpoints) < 10:
            printc("Pick at least 10 points to stage a limb", c="r")
            return

        if len(ssys_splines):
            plt.remove([ssys_splines.pop(), txtpred]).render()

        printc("Staging the image, please wait..", c="y", invert=1, italic=1)

        if os.path.isfile(limbstager_exe):
            # create an output file to feed the staging system executable
            with open(outfile, "w") as f:
                f.write(f"gene_mapper {outfile}  u 1.0  0 0 0 0 {len(cpoints)}\n")
                for p in vector(cpoints):
                    f.write(f"MEASURED {p[0]} {p[1]}\n")

            # now stage: a .tmp_out.txt file is created
            errnr = os.system(f"{limbstager_exe} {outfile} > .tmp_out.txt 2> /dev/null")
            if errnr:
                printc(
                    f"limbstager executable {limbstager_exe} returned error:",
                    errnr,
                    c="r",
                )
                return
        else:
            printc("INFO: limbstager executable not found.", c="lg")
            if os.path.isfile(
                limbstager_file
            ):  # pick previously staged points if exist
                printc(
                    "INFO: Trying to use previous staging data in file:",
                    limbstager_file,
                    c="lg",
                )
                import shutil

                shutil.copy(limbstager_file, ".tmp_out.txt")

        print("Reasing the grep!")
        result = grep(".tmp_out.txt", "RESULT")
        if not len(result):
            printc("Error - Could not stage the limb, RESULT tag is missing", c="r")
            return
        result = result[0]
        fitshape = grep(".tmp_out.txt", "FITSHAPE")
        predicted = grep(".tmp_out.txt", "PREDICTED")
        sidechi2 = grep(".tmp_out.txt", "side")
        LR = "Unknown"
        if len(sidechi2):
            isRight = float(sidechi2[0][5]) > float(sidechi2[0][7])
            LR = "RIGHT" if isRight else "LEFT"

        # now append the spline from staging system in outfile.txt
        # also copy some info from .tmp_out.txt
        splinecoors = []
        txtpred = None
        with open(outfile, "a") as f:
            for c in fitshape:
                f.write(c[0] + " " + c[1] + " " + str(float(c[2])) + "\n")
                splinecoors.append([float(c[1]), float(c[2])])
            f.write(" ".join(result) + "\n")
            if len(sidechi2):
                f.write(" ".join(sidechi2[0]) + "\n")
            if len(predicted):
                f.write(" ".join(predicted[0]) + "\n")
                printc(" ".join(predicted[0]), c="y")
            printc("..coordinates saved to file:", outfile, c="y", invert=1)
            txtpred = Text2D(
                " ".join(predicted[0])
                + f"\n:chi:^2={precision(result[3],3)}\nLimb side is {LR}",
                font="VictorMono",
            )

        splinecoors = np.array(splinecoors)
        splinecoors[:, 1] *= -1  # staging system uses inverted y

        ssp = Line(splinecoors).lw(4).c("red4")
        ssys_splines.append(ssp.z(1))

        plt.add(ssys_splines + [txtpred])
        ageh = int(result[1])

        # Store the id and its stage on an external table
        limbf = os.path.splitext(os.path.basename(infile))[0]
        stage = predicted[0][2]
        error = "".join(predicted[0][3:5])
        cdate = datetime.now()
        fdate = cdate.strftime("%d/%m/%Y %H:%M:%S")

        row = (limbf, stage, error, LR.lower(), fdate)

        # Check if the file exists
        if not os.path.exists(staging_data_tab):
            # If the file doesn't exist, create it and add the line
            with open(staging_data_tab, "w") as f:
                print("limb_id", "stage", "error", "side", "created", sep="\t", file=f)
                print(*row, sep="\t", file=f)
        else:
            # If the file exists, append the line
            with open(staging_data_tab, "a") as f:
                print(*row, sep="\t", file=f)


# ########################################################### stage the limb

settings.use_parallel_projection = True

plt = Plotter(bg="blackboard", title=f"gene_mapper v{version} - gene: {gene_name}")

cpoints, ssys_splines = [], [None]
points, spline, txtpred, ageh = None, None, None, None
pic = Picture(infile, channels=[0, 1, 2])
if blackandwhite:
    pic.bw()

if os.path.isfile(limbstager_file):  # pick previously staged points if exist
    printc(
        "INFO: loading previously picked points from staging file:",
        limbstager_file,
        c="lg",
        italic=True,
    )
    cpoints = [
        [float(mi[1]), float(mi[2]), 0] for mi in grep(limbstager_file, "MEASURED")
    ]
    update()

t = """Click to add a point
Right-click to remove it
Drag mouse to change contrast
Press c to clear points
      s to stage
      q to exit"""
instrucs = Text2D(t, pos="bottom-left", c="white", bg="green", font="Calco", s=0.85)

id1 = plt.add_callback("key press", keypress)
id2 = plt.add_callback("left click", leftClick)
id3 = plt.add_callback("right click", rightClick)

plt += [pic, instrucs]
plt.show(zoom="tightest", mode="image")
plt.remove_callback(id1).remove_callback(id2).remove_callback(id3)
if not ageh:  # not staged so exit peacefully :)
    plt.close()
    exit(0)

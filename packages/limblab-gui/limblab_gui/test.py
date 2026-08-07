import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import vtk


app = QApplication(sys.argv)

window = QMainWindow()

widget = QVTKRenderWindowInteractor()
window.setCentralWidget(widget)

renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.3, 0.4)

cube = vtk.vtkCubeSource()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cube.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer.AddActor(actor)

widget.GetRenderWindow().AddRenderer(renderer)
widget.Initialize()
widget.Start()
renderer.ResetCamera()

window.resize(800, 600)
window.show()

app.exec()

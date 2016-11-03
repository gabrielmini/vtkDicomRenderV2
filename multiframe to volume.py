from vtk import *
import matplotlib
import numpy
from IPython.display import Image

def printImage(imageData):

    imageViewer = vtkImageViewer2()
    imageViewer.SetInputConnection(imageData.GetOutputPort())

    renderWindowInteractor = vtkRenderWindowInteractor()
    imageViewer.SetupInteractor(renderWindowInteractor)

    imageViewer.Render()
    renderWindowInteractor.Start()

    return None
    print imageData


# Abrindo a imagem DICOM
IMAGE_PATH = r"samples\dental"

imageReader = vtkDICOMImageReader()
imageReader.SetDirectoryName(IMAGE_PATH)
imageReader.Update()

printImage(imageReader)

# Ajustando o Threshold da imagem
threshold = vtkImageThreshold()
threshold.SetInputConnection(imageReader.GetOutputPort())
threshold.ThresholdByLower(1000)  # remove all soft tissue
threshold.ReplaceInOn()
threshold.SetInValue(0)  # set all values below 400 to 0
threshold.ReplaceOutOn()
threshold.SetOutValue(1)  # set all values above 400 to 1
threshold.Update()

dmc = vtkDiscreteMarchingCubes()
dmc.SetInputConnection(threshold.GetOutputPort())
dmc.GenerateValues(1, 1, 1)
dmc.Update()


#smooth = vtk.vtkLoopSubdivisionFilter()
smooth = vtkButterflySubdivisionFilter()
smooth.SetNumberOfSubdivisions(1)
#smooth.SetInputConnection(dmc.GetOutputPort())
smooth.SetInputConnection(dmc.GetOutputPort())
smooth.Update()


# Salvando o volume
writer = vtkSTLWriter()
#writer.SetInputConnection(smoothsmooth.GetOutputPort())
#writer.SetInputConnection(dmc.GetOutputPort())
writer.SetInputConnection(dmc.GetOutputPort())

writer.SetFileTypeToBinary()
writer.SetFileName("C:\\Projects\\volume.stl")
writer.Write()
import os
os.system("pause")





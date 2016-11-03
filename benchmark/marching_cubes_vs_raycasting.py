"""
    Script to test the difference between the algorithm marching cubes and
    raycasting with vtkGPUVolumeRayCastMapper()

    Author: Gabriel Mini

"""

from vtk import *
import time
from psutil import Process
import os
import csv

chronometer = time.time()


def reset_timer():
    global chronometer
    lap = time.time()
    diff = lap - chronometer
    chronometer = lap
    return diff

LAP_TIMES = 10

MARCHING_CUBES = "Marching Cubes"
GPU_RAY_CASTING = "GPU Ray Casting"


def main():
    # Opening Image (Put outside of loop to avoid multiple reads on disk)
    img_reader = vtkDICOMImageReader()
    img_reader.SetDirectoryName("..\\samples\\dental 2")  # Test Directory
    img_reader.Update()
    reset_timer()

    result_dictionary = dict()
    for algorithm in (MARCHING_CUBES, GPU_RAY_CASTING):

        time_mean_list = list()
        for lap in range(LAP_TIMES):
            lap_time_list = list()
            # Applying the threshold filter
            thresh_filter = vtkImageThreshold()
            thresh_filter.SetInputConnection(img_reader.GetOutputPort())
            thresh_filter.ThresholdByUpper(1000)
            thresh_filter.SetInValue(255)
            thresh_filter.ReplaceInOn()
            thresh_filter.SetOutValue(0)
            thresh_filter.ReplaceOutOn()
            thresh_filter.Update()

            reset_timer()  # To compare the algoritms

            if algorithm == MARCHING_CUBES:  # Discrete marching cubes
                mesh = vtkDiscreteMarchingCubes()
                mesh.SetInputConnection(thresh_filter.GetOutputPort())
                mesh.GenerateValues(1, 255, 255)
                mesh.Update()

                poly_data_mapper = vtkPolyDataMapper()
                poly_data_mapper.ImmediateModeRenderingOn()
                poly_data_mapper.SetInputConnection(mesh.GetOutputPort())
                poly_data_mapper.Update()

                volume_actor = vtkActor()
                volume_actor.SetMapper(poly_data_mapper)
                volume_actor.GetProperty().SetColor(0, 1, 0)

            else:  # Ray cast Algorithm
                cast_filter = vtkImageCast()
                cast_filter.SetInputConnection(thresh_filter.GetOutputPort())
                cast_filter.SetOutputScalarTypeToUnsignedShort()
                cast_filter.Update()

                opacity_function = vtkPiecewiseFunction()
                opacity_function.AddPoint(0, 0)  # Transparent (External Volume)
                opacity_function.AddPoint(255, 1)  # Non Transparent (Object)

                # Color Function (Index 0: External Volume. Index 255: Object)
                func_color = vtkColorTransferFunction()
                func_color.AddRGBPoint(0, 0, 0, 0)
                func_color.AddRGBPoint(255, 0, 0, 255)

                # Create volume Property
                volume_property = vtkVolumeProperty()
                volume_property.SetColor(func_color)
                volume_property.ShadeOn()
                volume_property.SetScalarOpacity(opacity_function)
                volume_property.SetInterpolationTypeToLinear()

                mapper_volume = vtkGPUVolumeRayCastMapper()
                mapper_volume.SetInputData(cast_filter.GetOutput())

                volume_actor = vtkVolume()
                volume_actor.SetMapper(mapper_volume)
                volume_actor.SetProperty(volume_property)

            lap_time_list.append(reset_timer())

            renderer = vtk.vtkRenderer()
            render_window = vtk.vtkRenderWindow()
            render_window.AddRenderer(renderer)
            render_interactor = vtk.vtkRenderWindowInteractor()
            render_interactor.SetRenderWindow(render_window)

            renderer.AddActor(volume_actor)  # Adding a new Actor
            render_window.SetSize(200, 200)

            render_interactor.Initialize()
            renderer.ResetCamera()
            render_window.Render()
            lap_time_list.append(reset_timer())

            # Analise of memory consumption
            total_memory = Process(os.getpid()).memory_info().rss
            lap_time_list.append(total_memory / 1000000)  # In Bytes
            time_mean_list.append(lap_time_list)

        cum_sum = [sum(item) / LAP_TIMES for item in zip(*time_mean_list)]
        result_dictionary[algorithm] = cum_sum

    return result_dictionary

if __name__ == '__main__':

    values_dict = main()
    file_name = os.path.basename(__file__).split(".")[0] + ".csv"
    with open(file_name, "wb") as data_file:
        writer = csv.writer(data_file)
        header = ["Algorithm", "Algorithm Time(s)",
                  "Time To Render(s)", "Time Total(s)",
                  "Memory Consumption(MB)"]

        writer.writerow(header)

        for algorithm, values in values_dict.iteritems():
            without_memory = values[:-1]
            total_time = sum(without_memory)
            writer.writerow([algorithm] +
                            [format(item, ".2f") for item in without_memory] +
                            [format(total_time, ".2f"), values[-1]])

        writer.writerow([])
        writer.writerow(["Lap Times", LAP_TIMES])


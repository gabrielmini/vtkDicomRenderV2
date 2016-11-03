"""
    Script to test the time in comparison of many ray casting methods

    Author: Gabriel Mini
"""
from vtk import *
import time
import csv
from psutil import Process

import os


# Mapper Types
TEXTURE_MAPPER_2D = "Texture Mapper 2D"
GPU_RAY_CAST_MAPPER = "GPU Ray Cast Mapper"
FIXED_POINT_RAY_CAST_MAPPER = "Fixed Point Ray Cast Mapper"
TEXTURE_MAPPER_3D = "Texture Mapper 3D"
RAY_CAST_COMPOSITE = "Volume Ray Cast with Composite Function"

MAPPER_TYPES = [TEXTURE_MAPPER_2D,
                GPU_RAY_CAST_MAPPER,
                FIXED_POINT_RAY_CAST_MAPPER,
                TEXTURE_MAPPER_3D,
                RAY_CAST_COMPOSITE]

chronometer = time.time()


def reset_timer():
    global chronometer
    lap = time.time()
    diff = lap - chronometer
    chronometer = lap
    return diff


LEVELS = ["Threshold(s)",
          "Image Cast(s)",
          "Assign Volume Property(s)",
          "Creating Actor(s)",
          "Algorithm Time(s)",
          "Configuring Renderer(s)",
          "Total Time(s)",
          "Total Memory(MB)"]

LAP_TIMES = 10


def main():
    # Opening Image (Put outside of loop to avoid multiple reads on disk)
    img_reader = vtkDICOMImageReader()
    img_reader.SetDirectoryName("..\\samples\\dental 2")  # Test Directory
    img_reader.Update()
    reset_timer()

    benchmark_dict = dict()

    for mapper_type in MAPPER_TYPES:
        benchmark_dict[mapper_type] = list()

        temp_list = list()
        for i in range(LAP_TIMES):  # Times to get the mean
            times_list = list()

            # Applying the threshold filter
            thresh_filter = vtkImageThreshold()
            thresh_filter.SetOutputScalarTypeToUnsignedChar()
            thresh_filter.SetInputConnection(img_reader.GetOutputPort())
            thresh_filter.ThresholdByUpper(1500)  # Fixed value
            thresh_filter.SetInValue(255)
            thresh_filter.ReplaceInOn()
            thresh_filter.SetOutValue(0)
            thresh_filter.ReplaceOutOn()
            thresh_filter.Update()
            times_list.append(reset_timer())

            # Creating Cast Filter
            cast_filter = vtkImageCast()
            cast_filter.SetInputConnection(thresh_filter.GetOutputPort())
            cast_filter.SetOutputScalarTypeToUnsignedShort()
            cast_filter.Update()
            times_list.append(reset_timer())

            # Creating Opacity of object
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
            times_list.append(reset_timer())

            if mapper_type == TEXTURE_MAPPER_2D:
                mapper_volume = vtkVolumeTextureMapper2D()
                mapper_volume.SetInputData(cast_filter.GetOutput())

            elif mapper_type == TEXTURE_MAPPER_3D:
                mapper_volume = vtkVolumeTextureMapper3D()
                mapper_volume.SetInputData(cast_filter.GetOutput())

            elif mapper_type == FIXED_POINT_RAY_CAST_MAPPER:
                mapper_volume = vtkFixedPointVolumeRayCastMapper()
                mapper_volume.SetInputData(cast_filter.GetOutput())

            elif mapper_type == RAY_CAST_COMPOSITE:
                ray_cast_function = vtkVolumeRayCastCompositeFunction()
                ray_cast_function.SetCompositeMethodToClassifyFirst()

                mapper_volume = vtkVolumeRayCastMapper()
                mapper_volume.SetVolumeRayCastFunction(ray_cast_function)
                mapper_volume.SetInputData(cast_filter.GetOutput())

            elif mapper_type == GPU_RAY_CAST_MAPPER:
                mapper_volume = vtkGPUVolumeRayCastMapper()
                mapper_volume.SetInputData(cast_filter.GetOutput())

            times_list.append(reset_timer())

            # Creating Actor Volume
            volume_actor = vtkVolume()
            volume_actor.SetMapper(mapper_volume)
            volume_actor.SetProperty(volume_property)
            times_list.append(reset_timer())

            # Configuring Renderer
            renderer = vtkRenderer()
            renderer.SetBackground(1, .5, 1)
            render_window = vtkRenderWindow()
            render_window.AddRenderer(renderer)
            render_interactor = vtkRenderWindowInteractor()
            render_interactor.SetRenderWindow(render_window)

            renderer.AddActor(volume_actor)
            render_window.SetSize(200, 200)

            render_interactor.Initialize()
            renderer.ResetCamera()
            render_window.Render()
            times_list.append(reset_timer())

            times_list.append(sum(times_list))  # Adding sum of time

            # Memory Consumption
            total_memory = Process(os.getpid()).memory_info().rss  # In Bytes
            times_list.append(total_memory / 1000000)

            # Adding values on benchmark dictionary
            temp_list.append(times_list)

        cum_sum = [sum(item) / LAP_TIMES for item in zip(*temp_list)]
        benchmark_dict[mapper_type] = cum_sum

    return benchmark_dict

if __name__ == '__main__':

    values_dict = main()
    file_name = os.path.basename(__file__).split(".")[0] + ".csv"
    with open(file_name, "wb") as data_file:
        writer = csv.writer(data_file)
        # Write Header
        writer.writerow(["Algorithm"] + LEVELS)

        # Write Data
        for algorithm, values in values_dict.iteritems():
            writer.writerow([algorithm] + values)

        # Complementary Data
        writer.writerow([])
        writer.writerow(["Lap Times", LAP_TIMES])

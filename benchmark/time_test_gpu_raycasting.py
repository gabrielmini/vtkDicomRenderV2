"""
    Script to test the percentage of polydata rendering using a dicom images

    The result will be tested 10 times
    Author Gabriel Mini
"""
from vtk import *
import time
import csv
from psutil import Process
import os

chronometer = time.time()


def reset_timer():
    global chronometer
    lap = time.time()
    diff = lap - chronometer
    chronometer = lap
    return diff

LAP_TIMES = 10


def main():

    # opening the image
    img_reader = vtkDICOMImageReader()
    img_reader.SetDirectoryName("..\\samples\\dental 2")
    img_reader.Update()

    time_list = list()

    for lap in range(LAP_TIMES):
        lap_time_list = list()
        reset_timer()

        # Applying the threshold filter
        thresh_filter = vtkImageThreshold()
        thresh_filter.SetOutputScalarTypeToUnsignedChar()
        thresh_filter.SetInputConnection(img_reader.GetOutputPort())
        thresh_filter.ThresholdByUpper(1000)
        thresh_filter.SetInValue(255)
        thresh_filter.ReplaceInOn()
        thresh_filter.SetOutValue(0)
        thresh_filter.ReplaceOutOn()
        thresh_filter.Update()
        lap_time_list.append(reset_timer())

        # Creating a Image Cast Filter
        cast_filter = vtkImageCast()
        cast_filter.SetInputConnection(thresh_filter.GetOutputPort())
        cast_filter.SetOutputScalarTypeToUnsignedShort()
        cast_filter.Update()
        lap_time_list.append(reset_timer())

        # Color and Opacity Configuration
        func_opacity = vtkPiecewiseFunction()
        func_opacity.AddPoint(0, 0)  # 0 is the External volume
        func_opacity.AddPoint(255, 1)  # 255 is the Object Volume
        func_color = vtkColorTransferFunction()
        func_color.AddRGBPoint(0, 0, 0, 0)
        func_color.AddRGBPoint(255, 0, 0, 255)

        # Set Volume Property
        volume_property = vtkVolumeProperty()
        volume_property.SetColor(func_color)
        volume_property.ShadeOn()
        volume_property.SetScalarOpacity(func_opacity)
        volume_property.SetInterpolationTypeToLinear()
        lap_time_list.append(reset_timer())

        # Creating GpuRayCasteMapper
        mapper_volume = vtk.vtkGPUVolumeRayCastMapper()
        mapper_volume.SetInputData(cast_filter.GetOutput())
        lap_time_list.append(reset_timer())

        # Creating Volume Actor
        vol_actor = vtkVolume()
        vol_actor.SetMapper(mapper_volume)
        vol_actor.SetProperty(volume_property)
        lap_time_list.append(reset_timer())

        # Configuring Renderer
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_interactor = vtk.vtkRenderWindowInteractor()
        render_interactor.SetRenderWindow(render_window)

        renderer.AddActor(vol_actor)  # Adding a new Actor
        render_window.SetSize(200, 200)

        render_interactor.Initialize()
        renderer.ResetCamera()
        render_window.Render()
        lap_time_list.append(reset_timer())

        # Memory Consumption
        total_memory = Process(os.getpid()).memory_info().rss  # In Bytes
        lap_time_list.append(total_memory / 1000000)

        time_list.append(lap_time_list)

    cum_sum = [sum(item) / LAP_TIMES for item in zip(*time_list)]

    return cum_sum


if __name__ == '__main__':

    values = main()
    memory_consumption = values[-1]
    values = values[:-1]

    sum_values = sum(values)
    file_name = os.path.basename(__file__).split(".")[0] + ".csv"
    with open(file_name, "wb") as data_file:
        writer = csv.writer(data_file)
        header = ["", "Threshold Filter(s)", "Image Cast(s)",
                  "Set Volume Property(s)", "Creating GPU Ray Cast Mapper(s)",
                  "Creating Actor(s)", "Time to Render(s)", "Total(s)"]

        # Values
        writer.writerow(header)
        values_f = [format(item, ".2f") for item in values]
        writer.writerow(["Times"] + values_f + [format(sum_values, ".2f")])

        # Percentage
        perc = [(item * 100) / float(sum_values) for item in values]
        perc_list = [format(item, ".4f") + "%" for item in perc]

        # Complementary Data
        writer.writerow(["Percentage:"] + perc_list + [str(sum(perc)) + "%"])
        writer.writerow([])
        writer.writerow(["Memory Consumption(MB)", memory_consumption])
        writer.writerow(["Lap Times", LAP_TIMES])

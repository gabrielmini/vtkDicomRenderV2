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
    reset_timer()  # Starting the timer
    img_reader = vtkDICOMImageReader()
    img_reader.SetDirectoryName("..\\samples\\dental 2")
    img_reader.Update()

    times_list = list()
    for lap in range(LAP_TIMES):
        lap_time_list = list()
        reset_timer()

        # Applying the threshold filter
        thresh_filter = vtkImageThreshold()
        thresh_filter.SetInputConnection(img_reader.GetOutputPort())
        thresh_filter.ThresholdByUpper(1000)
        thresh_filter.SetInValue(255)
        thresh_filter.ReplaceInOn()
        thresh_filter.SetOutValue(0)
        thresh_filter.ReplaceOutOn()
        thresh_filter.Update()
        lap_time_list.append(reset_timer())

        # Making the mesh from vtkOutputAlgorithm
        mesh = vtkDiscreteMarchingCubes()
        mesh.SetInputConnection(thresh_filter.GetOutputPort())
        mesh.GenerateValues(1, 255, 255)
        mesh.Update()
        lap_time_list.append(reset_timer())

        # Create a polydata mapper from discrete marching cubes
        poly_data_mapper = vtkPolyDataMapper()
        poly_data_mapper.ImmediateModeRenderingOn()
        poly_data_mapper.SetInputConnection(mesh.GetOutputPort())
        poly_data_mapper.Update()
        lap_time_list.append(reset_timer())

        # Creating an Actor by poly data
        volume_3d_actor = vtkActor()
        volume_3d_actor.SetMapper(poly_data_mapper)
        volume_3d_actor.GetProperty().SetColor(0, 1, 0)
        lap_time_list.append(reset_timer())

        # Creating Renderer
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_interactor = vtk.vtkRenderWindowInteractor()
        render_interactor.SetRenderWindow(render_window)

        renderer.AddActor(volume_3d_actor)  # Adding a new Actor
        render_window.SetSize(200, 200)

        render_interactor.Initialize()
        renderer.ResetCamera()
        render_window.Render()
        lap_time_list.append(reset_timer())

        # Memory Consumption
        total_memory = Process(os.getpid()).memory_info().rss
        lap_time_list.append(total_memory / 1000000)  # In Bytes

        times_list.append(lap_time_list)

    return [sum(item) / LAP_TIMES for item in zip(*times_list)] # Cumulative sum

if __name__ == '__main__':
    values = main()
    memory_consumption = values[-1]
    values = values[:-1]

    sum_values = sum(values)
    file_name = os.path.basename(__file__).split(".")[0] + ".csv"
    with open(file_name, "wb") as data_file:
        writer = csv.writer(data_file)
        header = ["", "Threshold(s)", "Creating Marching Cubes(s)",
                  "Creating PolyDataMapper(s)", "Creating Actor(s)",
                  "Rendering(s)", "Total(s)"]

        # Values
        writer.writerow(header)
        values_f = [format(item, ".2f") for item in values]
        writer.writerow(["Times"] + values_f + [format(sum_values, ".2f")])

        # Percentage
        perc = [(item * 100)/float(sum_values) for item in values]
        perc_list = [format(item, ".4f") + "%" for item in perc]

        # Complementary Data
        writer.writerow(["Percentage:"] + perc_list + [str(sum(perc)) + "%"])
        writer.writerow([])
        writer.writerow(["Memory Consumption(MB)", memory_consumption])
        writer.writerow(["Lap Times", LAP_TIMES])

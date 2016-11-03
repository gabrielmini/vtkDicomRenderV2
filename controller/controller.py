from vtk import *
from vtk.util.numpy_support import *
import numpy as np
#from wxmplot import ImagePanel
import matplotlib.cm as cmap
import matplotlib.pyplot as plt
from scipy.stats import threshold
from utils import  str_to_rgb_tuple
from object_actor import ObjectActor
from view.controls.components_list_ctrl import ListCtrlComponent
from psutil import Process
from i18n import _
import os

PID = os.getpid()



try:
    import dicom
except ImportError:
    import pydicom as dicom

import wx
import tempfile
import os

# DICOM Constraints
TAG_ROWS = (0x0028, 0x0010)
TAG_COLUMNS = (0x0028, 0x0011)
TAG_BITS_ALLOCATED = (0x0028, 0x0100)
TAG_PHOTOM_INTERPR = (0x0028, 0x0004)


class DicomImage(object):
    def __init__(self, image):
        assert isinstance(image, dicom.dataset.FileDataset)
        
        self.__index = image[0x00200013].value
        self.__rows = image[TAG_ROWS].value
        self.__columns = image[TAG_COLUMNS].value
        self.__bits_allocated = image[TAG_BITS_ALLOCATED].value
        self.__original_array = image.pixel_array
        self.__min_value = np.amin(self.__original_array)
        self.__max_value = np.amax(self.__original_array)

        # Generating normalized gray scale array
        array = image.pixel_array.copy()  # will not change original array
        min_value = np.amin(array)
        if min_value < 0:
            array += abs(min_value)

        norm_array = ((array / float(np.ptp(array))) * 255).astype(int)
        img_gsc = np.empty((self.__columns, self.__rows, 3), dtype='uint8')
        img_gsc[:, :, 0] = img_gsc[:, :, 1] = img_gsc[:, :, 2] = norm_array
        self.__gsc_array = img_gsc

        # Generating wx Image from gray scale image array
        self.__gsc_image = wx.ImageFromBuffer(self.__columns,
                                              self.__rows,
                                              self.__gsc_array.tostring())

        # Creating Histogram (for convention use only 100 paths)
        self.__histogram_data = np.histogram(image.pixel_array, bins=100)

    @property
    def index(self):
        return self.__index

    def get_gsc_image(self):
        return self.__gsc_image

    def get_histogram(self):
        x, y = self.__histogram_data
        return x, y[:-1]

    def get_threshold_image(self, lower=None, upper=None):
        array = self.__original_array.copy()

        # TODO Need to verify if lower is greater than upper value
        if lower is not None and upper is not None:
            new_array = ((array > lower) & (array < upper)).astype(int)

        elif lower and not upper:
            raise NotImplementedError()
        else:  # if has only a upper value
            raise NotImplementedError()

        # Replacing the value 1 to 255
        np.place(new_array, new_array == 1, 255)
        new_image = np.zeros((self.__columns, self.__rows, 3), dtype='uint8')

        new_image[:, :, 0] = new_array  # Assuming the Red Color

        return wx.ImageFromBuffer(self.__columns,
                                  self.__rows,
                                  new_image.tostring())

    def get_image_range(self):
        return self.__min_value, self.__max_value


class Controller(object):
    def __init__(self, parent):
        from view.main_frame import MainFrame  # To avoid circular import
        assert type(parent).__name__ == MainFrame.__name__

        try:  # TODO Temporary
            assert isinstance(parent, MainFrame)
        except:
            pass
        self.parent = parent
        self.image_directory = None

        self.__path = None
        self.__image_reader = None
        self.__lowest_value = 0
        self.__highest_value = 0
        self.__image_buffer_list = list()


	self.set_dicom_image_dir(r"C:/projects/ic/samples/dental 2")
        #self.set_dicom_image_dir(r"C:\Tcc\samples\sample")


        return
        # temporary Configuration
        image_reader = vtkDICOMImageReader()
        image_reader.SetDirectoryName(r"C:\Tcc\samples\dental")
        image_reader.Update()

        threshold_filter = vtkImageThreshold()
        threshold_filter.SetInputConnection(image_reader.GetOutputPort())
        threshold_filter.ThresholdByUpper(1000)
        threshold_filter.SetInValue(0)
        threshold_filter.ReplaceInOn()
        threshold_filter.SetOutValue(1)
        threshold_filter.ReplaceOutOn()
        threshold_filter.Update()

        mesh_3d = vtkDiscreteMarchingCubes()
        mesh_3d.SetInputConnection(threshold_filter.GetOutputPort())
        mesh_3d.GenerateValues(1, 1, 1)
        mesh_3d.Update()

        decimatedVolume = vtkDecimatePro()
        decimatedVolume.SetInputConnection(mesh_3d.GetOutputPort())
        decimatedVolume.SetTargetReduction(0.7)
        decimatedVolume.Update()
        mesh_3d = decimatedVolume


        poly_data = vtkPolyDataMapper()
        poly_data.ImmediateModeRenderingOn()
        poly_data .SetInputConnection(mesh_3d.GetOutputPort())
        poly_data.Update()

        v = vtkActor()
        v.GetProperty().SetColor(1, 0.5, 0.7)
        v.SetMapper(poly_data)

        self.parent.render_window.add_object(v)

    def get_px_range(self):
        return self.__lowest_value, self.__highest_value

    def get_max_px_value(self):
        return self.__highest_value

    def get_min_px_value(self):
        return self.__lowest_value

    def get_slice_by_index(self, index):
        return self.__image_buffer_list[index]

    def get_slices_number(self):
        return len(self.__image_buffer_list)

    def set_dicom_image_dir(self, path):

        # Creating DICOM Configuration for this path
        self.__path = path
        self.__image_reader = vtkDICOMImageReader()
        self.__image_reader.SetDirectoryName(self.__path)
        self.__image_reader.Update()

        #self.__image_buffer_list = list()
        temp_buffer = list()
        for item in os.listdir(path):
            file_path = os.path.join(path, item)
            dicom_image = DicomImage(dicom.read_file(file_path))
            temp_buffer.append((dicom_image.index, dicom_image))
            min_v, max_v = dicom_image.get_image_range()
            self.__highest_value = max(self.__highest_value, max_v)
            self.__lowest_value = min(self.__lowest_value, min_v)


        # Need to sort the image instances
        self.__image_buffer_list = [item[1] for item in sorted(temp_buffer)]
       
        # View update
        self.parent.add_object_button.Enable()

    def normalize_value(self, value, lim_inf, lim_sup):
        return float((value - lim_inf)) / float((lim_sup - lim_inf))

    def get_vtk_actor_by_threshold(self, lower=None, upper=None,
                                   opacity=1, colour_tuple=(255, 255, 255)):


        # Creating a threshold Filter from memory image
        thresh_filter = vtkImageThreshold()
        thresh_filter.SetOutputScalarTypeToUnsignedChar()
        thresh_filter.SetInputConnection(self.__image_reader.GetOutputPort())

        if lower and upper:
            thresh_filter.ThresholdBetween(lower, upper)
        elif lower and not upper:
            thresh_filter.ThresholdByLower(lower)
        else:
            thresh_filter.ThresholdByUpper(upper)

        # TODO Need to change  if have lower and upper value
        #thresh_filter.ThresholdByUpper(upper)  # Fixed value
        thresh_filter.SetInValue(255)
        thresh_filter.ReplaceInOn()
        thresh_filter.SetOutValue(0)
        thresh_filter.ReplaceOutOn()
        thresh_filter.Update()

        # Creating a Image Cast Filter
        cast_filter = vtkImageCast()
        cast_filter.SetInputConnection(thresh_filter.GetOutputPort())
        cast_filter.SetOutputScalarTypeToUnsignedShort()
        cast_filter.Update()

        # Creating a opacity of object
        if opacity < 0:
            opacity = 0.0
        elif opacity > 1:
            opacity = 1.0

        opacity_function = vtkPiecewiseFunction()
        opacity_function.AddPoint(0, 0)  # Transparent (External Volume)
        print "OPACITY", opacity
        opacity_function.AddPoint(255, opacity)  # Non Transparent (Object)

        # Color Function (Index 0: External Volume. Index 255: Object)
        func_color = vtkColorTransferFunction()
        func_color.AddRGBPoint(0, 0, 0, 0)
        #func_color.AddRGBPoint(255, 0, 0, 255)
        func_color.AddRGBPoint(255, *colour_tuple)

        # Create volume Property
        volume_property = vtkVolumeProperty()
        volume_property.SetColor(func_color)
        volume_property.ShadeOn()
        volume_property.SetScalarOpacity(opacity_function)
        volume_property.SetInterpolationTypeToLinear()

        # Creating Mapper
        mapper_volume = vtkGPUVolumeRayCastMapper()
        mapper_volume.SetInputData(cast_filter.GetOutput())

        # Creating Actor
        volume_actor = vtkVolume()
        volume_actor.SetMapper(mapper_volume)
        volume_actor.SetProperty(volume_property)

        return volume_actor

    def add_object(self, object_actor, remove_all=False):
        assert isinstance(object_actor, ObjectActor)

        list_component = ListCtrlComponent(self.parent.tree_list_ctrl, object_actor)
        self.parent.tree_list_ctrl.add_component(list_component)
        self.parent.update_object_actors()

    def get_refresh_dict(self):

        # Left Down Section
        total_memory = Process().memory_info().rss / 1000000  # Memory in MB
        if total_memory >= 1000:
            memory_string = "{0:.2f} GB".format(total_memory / 1000.0)
        else:
            memory_string = "{0} MB".format(total_memory)

        ld = [_("Memory:  ") + memory_string,
              _("Usage:  ") + "{0:.2f} %".format(Process().memory_percent())]

        # Right Down Section
        rd = ["Gabriel Alberto Mini",
              "12/10/2016",
              "70 " + _("Images")]

        # Right Up Section
        ru = []

        return {"LD": ld,
                "RD": rd,
                "RU": ru}


if __name__ == '__main__':
    from view.controls.histogram_panel import HistogramPanel
    main_app = wx.App(None)
    main_frame = wx.Frame(None)


    f =dicom.read_file(r"C:\Tcc\samples\dental\Dentascan  0.75  "
                     r"H60s-CT-3-59.dcm")

    a = f.pixel_array
    # np.ptp() # peak to peak (range)
    print "min:",np.amin(a)
    print "max:",np.amax(a)
    print "ptp:",np.ptp(a)
    print a
    m = np.amin(a)
    a += abs(m) # add min value to  normalize
    norm_float = (a / float(np.ptp(a))) * 255
    print dir(a), type(a)
    norm_int = norm_float.astype(int)
    print norm_int
    print np.amin(norm_int)
    plt.imshow(norm_float)
    plt.show()
    plt.imshow(norm_int)
    plt.show()


    #print np.histogram(a,bins='auto'))
    #print np.linalg.norm(f.pixel_array,axis=0)




    #main_frame.Show()


    main_app.MainLoop()





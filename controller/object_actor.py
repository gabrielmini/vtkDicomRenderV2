import wx
import numpy as np
from utils import str_to_rgb_tuple

# Bitmap Constraints
DIM = 16  # size of color bitmap
BORDER_COLOR = (255, 255, 255, 255)  # border color of color bitmap


class ObjectActor(object):
    def __init__(self, vtk_actor, name, color="#FF00FF", visible=True):
        self.__name = name
        self.__visible = visible
        self.__actor = vtk_actor
        self.__color = None
        self.__color_bitmap = None
        self.set_color(color)

    def set_color(self, color):
        if isinstance(color, wx.Colour):
            self.__color = color

        elif isinstance(color, str):
            self.__color = str_to_rgb_tuple(color)

        elif isinstance(color, (list, tuple)) and len(color) == 3:
            self.__color = color

        else:
            raise AttributeError("Invalid Type for component colour" +
                                 str(type(color)))

        r, g, b = self.__color
        arr = np.zeros((DIM, DIM, 4), np.uint8)

        # Assign Values
        arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3] = r, g, b, 255

        # Setting borders
        arr[0, 0:DIM] = BORDER_COLOR  # first row
        arr[DIM - 1, 0:DIM] = BORDER_COLOR  # last row
        arr[0:DIM, 0] = BORDER_COLOR  # first col
        arr[0:DIM, DIM - 1] = BORDER_COLOR  # last col

        self.__color_bitmap = wx.BitmapFromBufferRGBA(DIM, DIM, arr)
        return self.__color_bitmap

    @property
    def actor(self):
        return self.__actor

    @property
    def name(self):
        return self.__name

    @property
    def colour(self):
        return self.__color

    @property
    def colour_bitmap(self):
        return self.__color_bitmap

    @property
    def visible(self):
        return self.__visible

    def change_text(self, new_text):
        self.__name = new_text

    def set_visible(self, visible=True):
        self.__visible = visible

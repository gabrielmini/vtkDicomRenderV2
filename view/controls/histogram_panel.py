import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np


class HistogramPanel(wx.Panel):
    def __init__(self, parent, h_fill="#FF0000", bg_color="#00FF00"):
        wx.Panel.__init__(self, parent)
        self.bg_color = bg_color
        self.h_fill = h_fill

        #self.figure = Figure(figsize=(-1, -1))
        self.figure = Figure(figsize=(2, 1))            
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axis = self.figure.add_subplot(111)
        self.values = None
        self.fill = None

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(self.canvas, 1, wx.EXPAND | wx.GROW)
        self.SetSizer(root_sizer)

        self.FitInside()
        self.Layout()

    def SetBackgroundColour(self, colour):
        self.axis.set_axis_bgcolor(colour)
        self.figure.set_facecolor(colour)

    def clear_data(self):
        self.axis.clear()

    def update_fill(self, inf_lim, sup_lim, color="#FFFFFF"):
        if self.fill:
            try:
                self.fill.remove()
            except ValueError:
                pass

        mask = np.zeros(len(self.values), dtype=int)
        mask[inf_lim:sup_lim] = 1  # Put a true value in mask

        self.fill = self.axis.fill_between(range(0, len(self.values)),
                                           self.values,
                                           color=color,
                                           linewidth=0,
                                           where=mask)
        self.Layout()

    def set_data(self, x, color="red", clear=True):

        if clear:
            self.clear_data()
            self.axis.axis('off')

        self.values = x
        self.axis.plot(x, linewidth=0)
        self.axis.fill_between(range(0, len(x)), x, color="#000000",
                               linewidth=0, where=np.ones(len(x), dtype=int))

        self.axis.set_xlim([0, len(x) - 1])
        self.Layout()
        self.Refresh()


if __name__ == '__main__':
    main_app = wx.App(None)

    main_app.MainLoop()

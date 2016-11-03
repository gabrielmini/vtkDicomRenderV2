import wx
from wx.lib.buttons import GenBitmapTextButton as BitmapButton


class FlatButton(BitmapButton):
    DEFAULT_COLOR = "#999999"

    def __init__(self, parent, label=None, bmp=None):
        assert isinstance(bmp, wx.Bitmap) or bmp is None
        label = "" if not isinstance(label, basestring) else " " + label
        BitmapButton.__init__(self, parent,
                              bitmap=bmp,
                              label=label,
                              style=wx.BORDER_NONE)

        self.SetBackgroundColour(self.DEFAULT_COLOR)
        self.SetForegroundColour("#000000")
        self.SetFont(wx.Font(14, wx.DECORATIVE, wx.NORMAL,
                             wx.BOLD, False, face="Calibri"))

        # Binds
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.SetDoubleBuffered(True)  # To avoid Flicking

    def _on_motion(self, evt):
        self.SetBackgroundColour("#C8C8C8")
        self.Refresh()

    def _on_leave_window(self, evt):
        self.SetBackgroundColour(self.DEFAULT_COLOR)
        self.Refresh()

if __name__ == "__main__":
    main_app = wx.App(None)
    main_frame = wx.Frame(None)
    sizer = wx.BoxSizer(wx.VERTICAL)
    main_frame.SetSizer(sizer)

    sizer.Add(FlatButton(main_frame,"teste"))

    main_frame.Show()
    main_app.MainLoop()

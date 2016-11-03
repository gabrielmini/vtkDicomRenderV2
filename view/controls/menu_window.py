import wx
from pkg_resources import resource_filename
from wx.lib.newevent import NewCommandEvent

CONFIG_ICON_PATH = resource_filename("view", "resources/config_72.png")
EXIT_ICON_PATH = resource_filename("view", "resources/exit_72.png")
OPEN_ICON_PATH = resource_filename("view", "resources/open_72.png")
INFO_ICON_PATH = resource_filename("view", "resources/info_72.png")

event_open_file, EVT_OPEN_FILE = NewCommandEvent()
event_exit, EVT_EXIT = NewCommandEvent()
event_open_config, EVT_OPEN_CONFIG = NewCommandEvent()


class TransparentMenu(wx.Frame):
    def __init__(self, parent, position=(0, 0)):
        wx.Frame.__init__(self, parent,
                          style=wx.NO_BORDER | wx.FRAME_NO_TASKBAR)

        self.SetBackgroundColour("#FF0000")

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root_sizer)

        # Initial Configuration
        self.SetTransparent(128)

        self.SetPosition(self.GetParent().GetPosition())
        self.SetBackgroundColour("#AAAAAA")

        # Open Button
        open_bmp = wx.Bitmap(OPEN_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.open_button = wx.BitmapButton(self, -1, open_bmp,
                                           style=wx.NO_BORDER)
        self.open_button.Bind(wx.EVT_BUTTON, self.on_button_open)

        # Config Button
        config_bmp = wx.Bitmap(CONFIG_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.config_button = wx.BitmapButton(self, -1, config_bmp,
                                             style=wx.NO_BORDER)
        self.config_button.Bind(wx.EVT_BUTTON, self.on_button_open_config)

        # Info Button
        info_bmp = wx.Bitmap(INFO_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.info_button = wx.BitmapButton(self, -1, info_bmp,
                                           style=wx.NO_BORDER)
        self.info_button.Bind(wx.EVT_BUTTON, self.on_button_open_config)

        # Exit Button
        exit_bmp = wx.Bitmap(EXIT_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.exit_button = wx.BitmapButton(self, -1, exit_bmp,
                                           style=wx.NO_BORDER)
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_button_exit)

        for btn in [self.open_button, self.config_button,
                    self.info_button, self.exit_button]:
            root_sizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
            btn.SetBackgroundColour("#AAAAAA")
            btn.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_button)
            btn.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_button)

        self.Layout()
        self.SetSize(self.GetBestSize())

    def on_button_open(self, evt):
        wx.PostEvent(self.GetParent(), event_open_file(id=0, pid=0))
        evt.Skip()

    def on_button_open_config(self, evt):
        wx.PostEvent(self.GetParent(), event_open_config(id=0, pid=0))
        evt.Skip()

    def on_button_info(self, evt):
        pass
        evt.Skip()

    def on_button_exit(self, evt):
        print "ON EXIT"
        wx.PostEvent(self.GetParent(), event_exit(id=0, pid=0))
        evt.Skip()

    def on_enter_button(self, evt):
        evt.GetEventObject().SetBackgroundColour("#FFFFFF")
        evt.Skip()

    def on_leave_button(self, evt):
        evt.GetEventObject().SetBackgroundColour("#AAAAAA")
        evt.Skip()

    def Show(self):
        self.Raise()
        super(TransparentMenu, self).Show()
        self.Layout()
        self.Move(self.GetParent().GetPosition())


class TestFrame(wx.Frame):
    def __init__(self, p, s):
        wx.Frame.__init__(self, None)

        self.SetBackgroundColour("#FF0000")
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(root_sizer)

        config_bmp = wx.Bitmap(CONFIG_ICON_PATH, wx.BITMAP_TYPE_PNG)
        root_sizer.Add(wx.BitmapButton(self, config_bmp, style=wx.NO_BORDER))
        root_sizer.Add(wx.BitmapButton(self, config_bmp, style=wx.NO_BORDER))
        root_sizer.Add(wx.BitmapButton(self, config_bmp, style=wx.NO_BORDER))
        root_sizer.Add(wx.BitmapButton(self, config_bmp, style=wx.NO_BORDER))


if __name__ == '__main__':

    def on_exit_event(evt):
        exit()
    
    main_app = wx.App(None)

    main_frame = wx.Frame(None,size=(400, 400))
    main_frame.Bind(EVT_EXIT, on_exit_event)
    
    main_frame.Show()
    a = TransparentMenu(main_frame, (400, 200))
    a.Show()

    main_app.MainLoop()

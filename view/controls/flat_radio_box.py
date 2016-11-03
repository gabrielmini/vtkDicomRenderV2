
import wx
from flat_button import FlatButton
from pkg_resources import resource_filename

TRUE_PATH = resource_filename("view", "resources/radio_checked_light_32.png")
FALSE_PATH = resource_filename("view", "resources/radio_unche_light_32.png")


class FlatRadioBox(wx.Panel):
    def __init__(self, parent, choices, sel=0):
        wx.Panel.__init__(self, parent)
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(root_sizer)
        self.SetBackgroundColour("##2F3F4F")

        self.choices = choices
        for choice in choices:
            bmp = wx.Bitmap(FALSE_PATH, wx.BITMAP_TYPE_PNG)
            btn = FlatButton(self, label=choice,bmp=bmp)

            btn.SetBackgroundColour("#2F3F4F")
            root_sizer.Add(btn)


    def on_button(self, evt):
        pass





if __name__ == '__main__':
    main_app = wx.App(None)
    main_frame = wx.Frame(None)
    main_frame.SetBackgroundColour("#2F3F4F")
    root_sizer = wx.BoxSizer(wx.VERTICAL)
    main_frame.SetSizer(root_sizer)

    root_sizer.Add(FlatRadioBox(main_frame,["a","b"]))

    main_frame.Show()
    main_app.MainLoop()



import os
import wx
from pkg_resources import resource_filename
from controls.flat_button import FlatButton
import wx.lib.agw.thumbnailctrl as tc
from i18n import _

CANCEL_ICON_PATH = resource_filename("view", "resources/cancel_32.png")
APPLY_ICON_PATH = resource_filename("view", "resources/check_32.png")
OPEN_FILE_PATH = resource_filename("view", "resources/folder_48.png")


class OpenImageDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, style=wx.BORDER_NONE)
        self.controller = parent.controller

        # General Configuration
        self.SetBackgroundColour("#2F3F4F")
        self.SetSize((1000, 600))
        self.CenterOnParent()
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(root_sizer)

        # Left Section
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(left_sizer, 6, wx.EXPAND | wx.ALL, 10)

        f_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(f_line_sizer, 0, wx.EXPAND)

        # Button Section
        open_bitmap = wx.Bitmap(OPEN_FILE_PATH, wx.BITMAP_TYPE_PNG)

        self.open_image_button = FlatButton(self, bmp=open_bitmap)
        # self.open_image_button.SetBackgroundColour(self.GetBackgroundColour())
        f_line_sizer.Add(self.open_image_button, 0)
        self.open_image_button.SetSize((40, 100))

        self.open_image_button.Bind(wx.EVT_BUTTON, self.on_open_image)

        # Path TextCtrl
        self.path_text_ctrl = wx.TextCtrl(self, -1, style=wx.NO_BORDER |
                                                          wx.TE_MULTILINE |
                                                          wx.FIXED_MINSIZE)
        self.path_text_ctrl.SetMinSize((20, 20))
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, face="Calibri")
        self.path_text_ctrl.SetFont(font)
        self.path_text_ctrl.Bind(wx.EVT_CHAR, self.on_change_text)
        self.path_text_ctrl.SetBackgroundColour("#CBCBCB")
        self.path_text_ctrl.SetForegroundColour("#2F3F4F")
        f_line_sizer.Add(self.path_text_ctrl, 1, wx.EXPAND | wx.LEFT, 10)

        # Left Center Area (Image Preview Area)
        p = wx.Panel(self)
        p.SetBackgroundColour("#FF0000")
        left_sizer.Add(p, 1, wx.EXPAND | wx.TOP, 10)

        # Left Bottom Area (Buttons Area)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.TOP, 10)

        c_bmp = wx.Bitmap(CANCEL_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.cancel_button = FlatButton(self, label=_("Cancel"), bmp=c_bmp)
        bottom_sizer.Add(self.cancel_button, 1, wx.RIGHT, 5)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)

        a_bmp = wx.Bitmap(APPLY_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.apply_button = FlatButton(self, label=_("Apply"), bmp=a_bmp)
        bottom_sizer.Add(self.apply_button, 1, wx.EXPAND | wx.LEFT, 5)
        self.apply_button.Bind(wx.EVT_BUTTON, self.on_apply_button)
        self.apply_button.Disable()  # Enable after choose a valid directory

        # Right Section
        self.thumbnail_ctrl = tc.ThumbnailCtrl(self)
        self.thumbnail_ctrl.SetBackgroundColour("#FF0000")
        root_sizer.Add(self.thumbnail_ctrl, 10, wx.EXPAND | wx.ALL, 10)

        self.ShowModal()

    def on_cancel_button(self, evt):
        self.Destroy()

    def on_apply_button(self, evt):

        try:
            self.controller.set_dicom_image_dir(self.path_text_ctrl.GetLabel())

        except:
            # TODO Shows a message error

            pass
        finally:
            self.Destroy()

    def on_change_text(self, evt):
        pass  # Ignore Event

    def on_open_image(self, evt):
        dialog = wx.DirDialog(self, "Choose a Directory with DICOM Images",
                              style=wx.DD_DEFAULT_STYLE)

        if dialog.ShowModal() == wx.ID_OK:
            self.path_text_ctrl.SetLabel(dialog.GetPath())
            self.apply_button.Enable()

if __name__ == '__main__':
    main_app = wx.App(None)
    frame = OpenImageDialog(None)
    main_app.MainLoop()


import wx
from pkg_resources import resource_filename
from view.controls.flat_button import FlatButton
import webbrowser
from wx.lib.stattext import GenStaticText as EventStaticText
from i18n import _

# Constraints
GITHUB_ICON_PATH = resource_filename("view", "resources/github_72.png")
CHECK_ICON_PATH = resource_filename("view", "resources/check_32.png")
REPO_LINK = "https://github.com/gabrielmini"


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour("#2F3F4F")
        self.SetSize((700, 600))
        self.CenterOnParent()

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root_sizer)

        license_ = """Software to transform DICOM Medical images into 3d \
volume to print
Copyright (C) 2016  Gabriel Mini (gabrielmini90@gmail.com)

This program is free software: you can redistribute it and/or modify it under \
the terms of the GNU General Public License as published by the Free Software \
Foundation, either version 3 of the License, or (at your option) any later \
version.

This program is distributed in the hope that it will be useful, but WITHOUT \
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS \
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with \
this program.  If not, see <http://www.gnu.org/licenses/>.

"""
        license_static_text = wx.StaticText(self, -1, label=license_,
                                            style=wx.ALIGN_CENTER_HORIZONTAL)

        license_static_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD,
                                            False, face="Calibri"))
        license_static_text.SetForegroundColour("#000000")  # Black colour

        root_sizer.Add(license_static_text, 1, wx.EXPAND | wx.ALL, 20)

        # GitHub Section
        github_sizer = wx.BoxSizer(wx.HORIZONTAL)
        github_sizer.AddStretchSpacer(1)
        root_sizer.Add(github_sizer, 0, wx.EXPAND | wx.ALL, 5)
        github_bmp = wx.Bitmap(GITHUB_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.github_bmp = wx.StaticBitmap(self, -1, github_bmp)
        github_sizer.Add(self.github_bmp, 0,
                         wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.hyperlink_text = EventStaticText(self, -1, REPO_LINK)
        self.hyperlink_text.SetBackgroundColour("#2F3F4F")
        self.hyperlink_text.SetForegroundColour("#000000")
        self.hyperlink_text.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD,
                                       False, face="Calibri"))

        self.hyperlink_text.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_text)
        self.hyperlink_text.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_text)


        github_sizer.Add(self.hyperlink_text, 0, wx.ALIGN_CENTER_VERTICAL |
                     wx.LEFT, 30)
        github_sizer.AddStretchSpacer(1)

        # Confirmation Button
        button_bmp = wx.Bitmap(CHECK_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.ok_button = FlatButton(self, label=_("Close"), bmp=button_bmp)
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_button_ok)

        root_sizer.Add(self.ok_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL,
                       10)

        # self.ShowModal()
        self.Show()

    def on_button_ok(self, evt):
        self.Close()

    def on_leave_text(self, evt):
        self.hyperlink_text.SetForegroundColour("#000000")
        self.hyperlink_text.Refresh()

    def on_enter_text(self, evt):
        self.hyperlink_text.SetForegroundColour("#000066") # Dark Blue
        self.hyperlink_text.Refresh()

    def on_click_text(self, evt):
        webbrowser.open(REPO_LINK)  # Opens the repo link


if __name__ == "__main__":
    main_app = wx.App()

    AboutDialog(None)

    main_app.MainLoop()

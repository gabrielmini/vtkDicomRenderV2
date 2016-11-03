"""
    Software to transform DICOM Medical images into 3d volume to print
    Copyright (C) 2016  Gabriel Mini (gabrielmini90@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from controls.components_list_ctrl import ObjectsListCtrl
from controls.render_window import VtkRenderPanel
from controls.menu_window import TransparentMenu, \
    EVT_OPEN_CONFIG, EVT_EXIT, EVT_OPEN_FILE
from controls.flat_button import FlatButton
from controller.controller import Controller
from controller.object_actor import ObjectActor
from open_image_dialog import OpenImageDialog
from about_dialog import AboutDialog
from add_object_dialog import AddObjectDialog
from i18n import _
from pkg_resources import resource_filename
from vtk import *
import wx

# Constraints
CREATE_ICON_PATH = resource_filename("view", "resources/add_object_2_48.png")
TXT_BORDER = 10


class MainFrame(wx.Frame):
    """
    Main Frame of this application

    Inheritance:
        wx.Frame
    """
    def __init__(self):
        """
        Constructor of the class MainFrame
        """
        wx.Frame.__init__(self, None, style=wx.NO_BORDER)

        # # # # # # # # # # # # # LAYOUT DEFINITION # # # # # # # # # # # # # #
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(root_sizer)

        # Left Section
        self.render_window = VtkRenderPanel(self)
        self.render_window.Enable(1)
        root_sizer.Add(self.render_window, 4, wx.EXPAND)

        # Right Section
        self.right_panel = wx.Panel(self)
        self.right_panel.SetBackgroundColour("#17202a")
        root_sizer.Add(self.right_panel, 1, wx.EXPAND)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel.SetSizer(right_sizer)

        header_text = wx.StaticText(self.right_panel, -1, _("Objects List"))
        right_sizer.Add(header_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        header_text.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD,
                                    face="Calibri"))
        header_text.SetForegroundColour("#A8B6C5")

        self.tree_list_ctrl = ObjectsListCtrl(self.right_panel)
        right_sizer.Add(self.tree_list_ctrl, 1, wx.EXPAND)

        create_bitmap = wx.Bitmap(CREATE_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.add_object_button = FlatButton(self.right_panel,
                                            label=_("Create Object"),
                                            bmp=create_bitmap)
        right_sizer.Add(self.add_object_button, 0, wx.EXPAND | wx.ALL, 10)
        #self.add_object_button.Disable()  # Enable after select a valid folder

        # Transparent Menu
        self.menu = TransparentMenu(self)

        # # # # # # # # # # # # # # # EVENT BINDS # # # # # # # # # # # # # # #
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.add_object_button.Bind(wx.EVT_BUTTON, self.on_button_create)
        self.Bind(EVT_OPEN_FILE, self.on_open_button)
        self.Bind(EVT_OPEN_CONFIG, self.on_open_config_button)
        self.Bind(EVT_EXIT, self.on_exit_button)

        # # # # # # # # # # DISPLAY INITIALIZATION ROUTINE  # # # # # # # # # #
        primary_display = None
        for item in range(wx.Display.GetCount()):
            primary_display = wx.Display(item)
            # if not primary_display.IsPrimary():
            if primary_display.IsPrimary():
                break

        x, y, w, h = primary_display.GetClientArea()
        self.Move((x, y))
        self.SetSize((w, h))
        #self.Show()  # Show Frame

        # # # # # # # # # # # # ANOTHER CONFIGURATIONS  # # # # # # # # # # # #
        cone_source = vtkConeSource()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(cone_source.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.render_window.add_actor(actor)
        self.controller = Controller(self)  # Controller of all views

        # Timer configurations
        self.refresh_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_refresh)
        self.refresh_timer.Start(500)

        # Text actors
        self.info_texts = dict()

        self.left_down_text = vtkTextActor()
        self.render_window.add_actor(self.left_down_text)
        self.info_texts["LD"] = self.left_down_text

        self.rigth_up_text = vtkTextActor()
        self.render_window.add_actor(self.rigth_up_text)
        self.info_texts["RU"] = self.rigth_up_text

        self.rigth_down_text = vtkTextActor()
        self.render_window.add_actor(self.rigth_down_text)
        self.info_texts["RD"] = self.rigth_down_text

        # Configuration to send all errors on console
        # vtkOutputWindow().SendToStdErrOn()

    # EVENTS EVENTS
    def on_refresh(self, evt):
        x, y, w, h = self.render_window.GetRect()
        text_data_dict = self.controller.get_refresh_dict()

        for position, text_actor in self.info_texts.iteritems():
            text_actor.SetInput("\n".join(text_data_dict[position]))
            text_property = text_actor.GetTextProperty()
            # text_property.SetFontFamilyAsString("Carlito") use?
            text_property.ShadowOn()

            if position == "LD":
                text_actor.SetDisplayPosition(TXT_BORDER, TXT_BORDER)
                text_property.SetJustificationToLeft()

            elif position == "RD":
                text_actor.SetDisplayPosition(w - TXT_BORDER, TXT_BORDER)
                text_property.SetJustificationToRight()

            elif position == "RU":
                text_actor.SetDisplayPosition(w - TXT_BORDER, h - TXT_BORDER)
                text_property.SetJustificationToRight()
                text_property.SetVerticalJustificationToTop()

            self.render_window.add_actor(text_actor)

    def on_motion_create_button(self, evt):
        print "asdasdad"

    def on_open_button(self, evt):
        """
        Event Function called when open button is clicked

        Args:
            evt: (wx.Event) Is a wx event object class
        """
        OpenImageDialog(self)

    def on_open_config_button(self, evt):
        AboutDialog(self)

    def on_exit_button(self, evt):
        print "on_exit_button"
        self.on_close(None)

    def on_button_create(self, evt):
        print "on_button_create"
        a = AddObjectDialog(self)

    def on_motion(self, evt):
        x, y = evt.GetPosition()
        # if self.menu.GetRect().Contains(evt.GetPosition()):
        if x < 100:
            self.menu.Show()
        else:
            self.menu.Hide()

    def on_close(self, evt):
        self.render_window.shutdown()
        self.Destroy()

    def add_actor(self, actor):
        self.render_window.add_actor(actor)

    def update_object_actors(self):
        # Add gizmo

        self.render_window.clear_objects()  # Needs to clear all objects

        for component in self.tree_list_ctrl.get_all_components():
            assert isinstance(component, ObjectActor)
            self.render_window.add_actor(component.actor)





def main():
    main_app = wx.App(None)
    frame = MainFrame()

    frame.Show()
    #AddObjectDialog(frame)
    #OpenImageDialog(frame)
    #exit()
    main_app.MainLoop()


if __name__ == '__main__':
    main()

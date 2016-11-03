import wx
import wx.lib.agw.customtreectrl as ct
from view.view_constraints import ITEM_FONT
import numpy as np
from pkg_resources import resource_filename
from controller.utils import str_to_rgb_tuple
from controller.object_actor import ObjectActor
from i18n import _
from view.controls.flat_button import FlatButton

# Constraints
# Icon Paths
VISIBLE_ICON_PATH = resource_filename("view", "resources/visible_16_l.png")
INVISIBLE_ICON_PATH = resource_filename("view", "resources/invisible_16_l.png")
ICON_SIZE = (16, 16)

event_item_left_click, EVT_ITEM_LEFT_CLICK = wx.lib.newevent.NewCommandEvent()

# Popup Window Constraints
POPUP_WIDTH = 200


class OptionsPopupWindow(wx.Panel):

    ID_NONE_OPTION = -1
    ID_EXIT = 0
    ID_EXPORT = 1

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("#FF0000")
        self.Hide()

        # Control Configuration
        self.export_button = FlatButton(self, label=_("Export"))
        self.export_button.Bind(wx.EVT_BUTTON, self.on_button)
        self.exit_button = FlatButton(self, label=_("Exit"))
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_button)

        # layout Configuration
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root_sizer)
        root_sizer.Add(self.export_button, 0, wx.EXPAND)
        root_sizer.Add(self.exit_button, 0, wx.EXPAND)

        # Modal Configuration
        self.__option = self.ID_NONE_OPTION
        self.event_loop = wx.EventLoop()
        self.MakeModal(True)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
        self.SetSize(self.GetBestSize())

    def on_button(self, evt):

        evt_object = evt.GetEventObject()
        if evt_object == self.export_button:
            self.__option = self.ID_EXPORT
        elif evt_object == self.exit_button:
            self.__option = self.ID_EXIT

        self.MakeModal(False)
        self.event_loop.Exit()

    def on_leave_window(self, evt):
        x, y = self.GetPosition()
        evt_x, evt_y = evt.GetPosition()

        # If leaves main window, but is not a child window
        if not self.GetRect().Contains((evt_x + x, evt_y + y)):
            self.MakeModal(False)
            self.event_loop.Exit()

    def ShowModal(self, pos):
        self.MakeModal(True)

        # Verifies if the point of event will create a window out of parent
        x, y = pos
        s_x, s_y = self.GetSize()
        parent_width = self.GetParent().GetSize().width
        if (x + s_x) > parent_width:  # If the event goes out of parent
            self.SetPosition((parent_width - s_x, y - 10))
        else:
            self.SetPosition((x - 10, y - 10))

        self.Show()
        self.event_loop.Run()
        self.Hide()
        return self.__option


class ObjectsListCtrl(ct.CustomTreeCtrl):
    def __init__(self, parent):
        ct.CustomTreeCtrl.__init__(self, parent,
                                   style=wx.NO_BORDER,
                                   agwStyle=ct.TR_HAS_BUTTONS |
                                            ct.TR_HIDE_ROOT)

        self.view_components_dict = dict()
        self.image_list = wx.ImageList(*ICON_SIZE)

        # Add Custom Bitmaps
        self.VISIBLE_IMG = self.image_list.Add(wx.Bitmap(VISIBLE_ICON_PATH,
                                                         wx.BITMAP_TYPE_PNG))
        self.INVISIBLE_IMG = self.image_list.Add(wx.Bitmap(INVISIBLE_ICON_PATH,
                                                           wx.BITMAP_TYPE_PNG))
        self.AssignImageList(self.image_list)
        self.root = self.AddRoot("")

        # Style Configuration
        self.SetBackgroundColour("#17202a")
        self.SetForegroundColour("#A8B6C5")
        self.SetFont(wx.Font(*ITEM_FONT))

        # Bind Events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        # self.Bind(wx.EVT_MOTION, self.on_motion)

    def on_right_down(self, evt):
        result = OptionsPopupWindow(parent=self).ShowModal(evt.GetPosition())

        if result == OptionsPopupWindow.ID_EXPORT:
            print "Export"

        a.Destroy()

    def on_left_down(self, evt):
        evt_pos = evt.GetPosition()
        view_item, b = self.HitTest(evt_pos)
        if view_item is not None:
            parent_item = view_item.GetParent()
            if parent_item == self.root:  # Is a name component
                print "Need to implement the branch item"
            else:
                for name, component in self.view_components_dict.iteritems():
                    if parent_item == component.get_branch_item():
                        component.on_attribute_clicked(view_item, evt_pos)
                        break

        evt.Skip()

    def on_motion(self, evt):
        a, b = self.HitTest(evt.GetPosition())
        if a:
            print a.GetParent()
        print evt.GetPosition()

    def on_change_item(self, evt):
        print dir(evt)
        print evt.GetEventObject()
        self.GetTargetRect()

        item = evt.GetItem()
        print "item:", item

        print "Bounding Box", self.GetBoundingRect(evt.GetItem())
        if item:
            pass

        else:  # Invalid Item selection
            pass  # Do Nothing

    def add_component(self, component):
        print type(component)

        if component.name not in self.view_components_dict:
            self.view_components_dict[component.name] = component
        else:
            raise AttributeError("This component already exists on widget")

    def get_all_components(self):
        return [item.component for item in self.view_components_dict.values()]

    def get_component(self, name):
        raise NotImplementedError()


class ListCtrlComponent(object):
    def __init__(self, parent, component):
        assert isinstance(component, ObjectActor)
        self.parent = parent
        self.component = component
        self.root_item = parent.AppendItem(self.parent.root,
                                           self.component.name)

        # Visibility Options
        self.visible_item = self.parent.AppendItem(self.root_item, "")
        self.__update_visibility(component.visible)

        # Color Configuration
        self.color_item = self.parent.AppendItem(self.root_item, _("Color"))
        index = self.parent.image_list.Add(component.colour_bitmap)
        self.parent.SetItemImage(self.color_item, index)
        self.root_item.Expand()

    @property
    def name(self):
        return self.component.name

    @property
    def actor(self):
        return self.component.actor

    def __update_color(self, color):
        pass

    def __update_visibility(self, visibility):
        if visibility:
            text, visibility_image = _("Visible"), self.parent.VISIBLE_IMG
        else:
            text, visibility_image = _("Invisible"), self.parent.INVISIBLE_IMG

        self.visible_item.SetText(text)
        self.parent.SetItemImage(self.visible_item, visibility_image)
        self.component.set_visible(visibility)

    def get_component_name(self):
        return self.component.name

    def get_branch_item(self):
        return self.root_item

    def on_attribute_clicked(self, item, position):

        if item == self.visible_item:
            visibility = not self.component.visible  # Toggle visibility values
            self.__update_visibility(visibility)

        elif item == self.color_item:
            colour_dialog = wx.ColourDialog(self.parent)
            if colour_dialog.ShowModal() == wx.ID_OK:
                new_colour = colour_dialog.GetColourData().GetColour().Get()

                new_bitmap = self.component.set_color(new_colour)
                index = self.parent.image_list.Add(new_bitmap)
                self.parent.SetItemImage(item, index)

        else:
            raise NotImplementedError("Unknown item")


if __name__ == "__main__":
    main_app = wx.App(None)
    main_frame = wx.Frame(None)
    a = ObjectsListCtrl(main_frame)
    a.add_component(ListCtrlComponent(a,ObjectActor(123, "Cranio", visible=False, )))
    #a.add_component(ObjectActor(123, "Cerebro"))


    main_frame.Show()

    main_app.MainLoop()


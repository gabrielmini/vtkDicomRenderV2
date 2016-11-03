import wx
from pkg_resources import resource_filename
from controls.render_window import VtkRenderPanel
from controls.flat_slider import FlatSlider
from controls.flat_button import FlatButton
from i18n import _
from controls.histogram_panel import HistogramPanel
from controller.utils import *

from controller.object_actor import ObjectActor

# CREATE_ICON_PATH = resource_filename("view", "resources/plus_48.png")
PAINT_BUCKET_PATH = resource_filename("view", "resources/bucket_light_32.png")
LAYER_PATH = resource_filename("view", "resources/layer_light_32.png")

TOP_LAYER_PATH = resource_filename("view", "resources/top_light_32.png")
BOTTOM_LAYER_PATH = resource_filename("view", "resources/bottom_light_32.png")
TEXT_PATH = resource_filename("view", "resources/text_light_32.png")
OPACITY_PATH = resource_filename("view", "resources/opacity_32_l.png")

CANCEL_ICON_PATH = resource_filename("view", "resources/cancel_32.png")
APPLY_ICON_PATH = resource_filename("view", "resources/check_32.png")

SPACING = wx.EXPAND | wx.BOTTOM
DEFAULT_FONT = (14, wx.DECORATIVE, wx.NORMAL, wx.BOLD, False, 'Calibri')


class AddObjectDialog(wx.Dialog):
    def __init__(self, parent):
        self.parent = parent
        self.controller = self.parent.controller

        wx.Dialog.__init__(self, parent, style=wx.BORDER_NONE)
        self.SetSize((1280, 600))
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(root_sizer)
        self.SetBackgroundColour("#2F3F4F")
        self.actor_color = (255, 255, 255)

        # # # # # # # # # # # # COMPONENTS DEFINITION # # # # # # # # # # # # #
        # Left Section
        preview_static_text = wx.StaticText(self, label="Preview Layer",
                                            style=wx.ALIGN_CENTER_HORIZONTAL)
        preview_static_text.SetForegroundColour("#CCCCCC")
        preview_static_text.SetFont(wx.Font(*DEFAULT_FONT))

        bmp = wx.Bitmap(LAYER_PATH, wx.BITMAP_TYPE_PNG)
        preview_static_bitmap = wx.StaticBitmap(self, -1, bmp)

        slices_number = self.controller.get_slices_number() - 1
        self.layer_preview_slider = FlatSlider(self, min_v=0,
                                               max_v=slices_number)
        self.layer_preview_slider.Bind(wx.EVT_SLIDER, self.on_preview_slider)

        threshold_static_text = wx.StaticText(self, label="Threshold "
                                                          "Configuration",
                                              style=wx.ALIGN_CENTER_HORIZONTAL)

        threshold_static_text.SetForegroundColour("#CCCCCC")
        threshold_static_text.SetFont(wx.Font(*DEFAULT_FONT))
        choices = [_("Top"), _("Bottom"), _("Range")]
        self.threshold_radio = wx.RadioBox(self, -1, choices=choices)

        min_px, max_px = self.controller.get_px_range()

        bmp = wx.Bitmap(TOP_LAYER_PATH, wx.BITMAP_TYPE_PNG)
        top_layer_bitmap = wx.StaticBitmap(self, -1, bmp)
        self.top_layer_slider = FlatSlider(self, min_v=min_px, max_v=max_px)
        self.top_layer_slider.Bind(wx.EVT_SLIDER, self.on_slider)
        self.top_layer_slider.Bind(wx.EVT_LEFT_UP, self.on_up)

        bmp = wx.Bitmap(BOTTOM_LAYER_PATH, wx.BITMAP_TYPE_PNG)
        bottom_layer_bitmap = wx.StaticBitmap(self, -1, bmp)
        self.bottom_layer_slider = FlatSlider(self, min_v=min_px, max_v=max_px)
        self.bottom_layer_slider.Bind(wx.EVT_SLIDER, self.on_slider)
        self.bottom_layer_slider.Bind(wx.EVT_LEFT_UP, self.on_up)

        opacity_static_text = wx.StaticText(self, label="Opacity",
                                            style=wx.ALIGN_CENTER_HORIZONTAL)

        opacity_static_text.SetForegroundColour("#CCCCCC")
        opacity_static_text.SetFont(wx.Font(*DEFAULT_FONT))

        bmp = wx.Bitmap(OPACITY_PATH, wx.BITMAP_TYPE_PNG)
        opacity_bitmap = wx.StaticBitmap(self, -1, bmp)
        self.opacity_slider = FlatSlider(self, min_v=0, max_v=100, value=100)
        self.opacity_slider.Bind(wx.EVT_LEFT_UP, self.on_up_opacity_slider)

        colour_static_text = wx.StaticText(self,
                                           label="Colour",
                                           style=wx.ALIGN_CENTER_HORIZONTAL)
        colour_static_text.SetForegroundColour("#CCCCCC")
        colour_static_text.SetFont(wx.Font(*DEFAULT_FONT))

        bmp = wx.Bitmap(PAINT_BUCKET_PATH, wx.BITMAP_TYPE_PNG)
        colour_bitmap = wx.StaticBitmap(self, -1, bmp)
        self.colour_panel = wx.Panel(self)
        colour = rgb_tuple_to_string(self.actor_color)
        self.colour_panel.SetBackgroundColour(colour)
        self.colour_panel.SetMinSize((30, 30))

        self.change_colour_button = FlatButton(self, "Change Colour")
        self.change_colour_button.Bind(wx.EVT_BUTTON, self.on_change_colour)

        bmp = wx.Bitmap(CANCEL_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.cancel_button = FlatButton(self, "Cancel", bmp)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_close)

        bmp = wx.Bitmap(APPLY_ICON_PATH, wx.BITMAP_TYPE_PNG)
        self.apply_button = FlatButton(self, "Apply", bmp)
        self.apply_button.Bind(wx.EVT_BUTTON, self.on_apply_button)

        # Middle Section

        self.images_panel = wx.Panel(self)
        self.images_panel.SetBackgroundColour("#000000")
        self.original_image = wx.StaticBitmap(self.images_panel)
        self.original_image.SetDoubleBuffered(True)
        self.filtered_image = wx.StaticBitmap(self.images_panel)
        self.filtered_image.SetDoubleBuffered(True)
        #self.filtered_image.SetBackgroundColour("#00FF00")

        self.histogram = HistogramPanel(self)
        self.histogram.SetBackgroundColour("#2F3F4F")

        # Right Section
        self.render_panel = VtkRenderPanel(self)
        self.render_panel.SetBackgroundColour("#FFFF00")

        bmp = wx.Bitmap(TEXT_PATH, wx.BITMAP_TYPE_PNG)
        name_text_bitmap = wx.StaticBitmap(self, -1, bmp)
        self.name_text_ctrl = wx.TextCtrl(self, -1, "Name")

        # # # # # # # # # # # # # LAYOUT DEFINITION # # # # # # # # # # # # # #

        # Left Section
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 10)

        line1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line1_sizer.AddMany([(preview_static_bitmap),
                             (self.layer_preview_slider, 1, wx.EXPAND)])

        line3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line3_sizer.AddMany([(top_layer_bitmap),
                             (self.top_layer_slider, 1, wx.EXPAND)])

        line4_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line4_sizer.AddMany([(bottom_layer_bitmap),
                             (self.bottom_layer_slider, 1, wx.EXPAND)])

        line5_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line5_sizer.AddMany([(opacity_bitmap),
                             (self.opacity_slider, 1, wx.EXPAND)])

        line6_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line6_sizer.AddMany([(colour_bitmap),
                             (self.colour_panel, 0, wx.ALIGN_CENTER_VERTICAL
                              | wx.LEFT, 10),
                             (self.change_colour_button, 0, wx.LEFT, 10)
                             ])

        line7_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line7_sizer.AddMany([(self.cancel_button, 1, wx.RIGHT, 5),
                             (self.apply_button, 1, wx.LEFT, 5)])

        left_sizer.AddMany([(preview_static_text, 0, SPACING, 10),
                            (line1_sizer, 0, SPACING, 10),
                            (-1, 20),
                            (threshold_static_text, 0, SPACING, 10),
                            (self.threshold_radio, 0, SPACING, 10),
                            (line3_sizer, 0, SPACING, 10),
                            (line4_sizer, 0, SPACING, 5),
                            (opacity_static_text, 0, SPACING, 5),
                            (line5_sizer, 0, SPACING, 5),
                            (colour_static_text, 0, SPACING, 5),
                            (line6_sizer, 0, SPACING, 10),
                            ((100, 100), 1, SPACING, 10),
                            (line7_sizer, 0, wx.EXPAND, 10),
                            ])

        # Middle Section
        middle_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(middle_sizer, 2, (wx.EXPAND | wx.ALL) - wx.LEFT, 10)

        line1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.images_panel.SetSizer(line1_sizer)
        line1_sizer.AddMany([(self.original_image, 1, wx.EXPAND),
                             (self.filtered_image, 1, wx.EXPAND)])

        middle_sizer.AddMany([(self.images_panel, 1, wx.EXPAND),
                              (self.histogram, 1, wx.EXPAND)])

        # Right Section
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(right_sizer, 2, (wx.EXPAND | wx.ALL) - wx.LEFT, 10)

        line2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line2_sizer.AddMany([(name_text_bitmap, 0, wx.RIGHT, 10),
                             (self.name_text_ctrl, 1, wx.EXPAND | wx.ALL, 5)])

        right_sizer.AddMany([(self.render_panel, 1, wx.EXPAND),
                             (line2_sizer, 0, SPACING | wx.TOP, 10)])

        self.l_index = None
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Layout()
        self.CenterOnParent()

        # Setting the initial data
        self.layer_preview_slider.set_value(slices_number)
        self.__change_preview_image(slices_number)
        self.top_layer_slider.set_value(max_px)
        self.__update_threshold_image(self.bottom_layer_slider.get_value(),
                                      self.top_layer_slider.get_value())

        self.update_actor()
        self.ShowModal()

    def on_change_colour(self, evt):
        colour_dialog = wx.ColourDialog(self)
        if colour_dialog.ShowModal() == wx.ID_OK:
            colour_tuple = colour_dialog.GetColourData().GetColour().Get()
            self.actor_color = colour_tuple
            colour_string = rgb_tuple_to_string(colour_tuple)
            self.colour_panel.SetBackgroundColour(colour_string)
            self.colour_panel.Refresh()
            self.update_actor()
        else:  # If the user cancelled action, do nothing
            return

    def get_actor(self):
        opacity = self.opacity_slider.get_value()
        top_value = int(self.top_layer_slider.get_value())
        bottom_value = int(self.bottom_layer_slider.get_value())

        return self.controller.get_vtk_actor_by_threshold(bottom_value,
                                                          top_value,
                                                          opacity / 100,
                                                          self.actor_color)

    def update_actor(self):
        self.render_panel.clear_objects()
        actor = self.get_actor()
        self.render_panel.add_actor(actor)

    def on_up_opacity_slider(self, evt):
        self.update_actor()

    def on_up(self, evt):
        self.update_actor()

    def on_apply_button(self, evt):
        # img = self.parent.controller.get_img().image_buffer_list[
        # 25].GetImage()
        # a = img.Scale(*self.original_image.GetSize())
        # self.original_image.SetBitmap(wx.BitmapFromImage(a))

        self.name_text_ctrl.GetValue()
        object_actor = ObjectActor(vtk_actor=self.get_actor(),
                                   name=self.name_text_ctrl.GetValue(),
                                   color=self.actor_color,
                                   visible=True)

        self.controller.add_object(object_actor)
        self.Destroy()

    def on_close(self, evt):
        self.render_panel.shutdown()
        self.Destroy()

    def on_preview_slider(self, evt):
        index = int(self.layer_preview_slider.get_value())
        if self.l_index == index:
            return

        self.__change_preview_image(index)

        top_value = int(self.top_layer_slider.get_value())
        bottom_value = int(self.bottom_layer_slider.get_value())

        lim_range = self.controller.get_px_range()
        norm_top_v = self.controller.normalize_value(top_value, *lim_range)
        norm_bot_v = self.controller.normalize_value(bottom_value, *lim_range)

        self.histogram.update_fill(inf_lim=int(norm_bot_v * 100),
                                   sup_lim=int(norm_top_v * 100),
                                   color="#CCCCCC")

    def __change_preview_image(self, index):
        original_image = self.controller.get_slice_by_index(index)

        # Put data on original Image
        gsc_image = original_image.get_gsc_image()
        a = gsc_image.Scale(*self.original_image.GetSize())
        self.original_image.SetBitmap(wx.BitmapFromImage(a))
        a, b = original_image.get_histogram()
        self.histogram.set_data(a)

        # Put data on filtered Image
        top_value = int(self.top_layer_slider.get_value())
        bottom_value = int(self.bottom_layer_slider.get_value())

        self.__update_threshold_image(bottom_value, top_value)

    def __update_threshold_image(self, bottom_value, top_value):
        image_index = int(self.layer_preview_slider.get_value())
        dicom_image = self.controller.get_slice_by_index(image_index)
        from controller.controller import DicomImage
        t_image = dicom_image.get_threshold_image(bottom_value, top_value)
        t = t_image.Scale(*self.filtered_image.GetSize())
        self.filtered_image.SetBitmap(wx.BitmapFromImage(t))

    def on_slider(self, evt):
        # Updating Histogram
        low_value = self.bottom_layer_slider.get_value()
        top_value = self.top_layer_slider.get_value()

        if evt.GetEventObject() == self.bottom_layer_slider:
            if low_value > top_value:
                print "Veto"
                return

        # TODO Move the processing to controller
        top_value = int(self.top_layer_slider.get_value())
        bottom_value = int(self.bottom_layer_slider.get_value())

        lim_range = self.controller.get_px_range()
        norm_top_v = self.controller.normalize_value(top_value, *lim_range)
        norm_bot_v = self.controller.normalize_value(bottom_value, *lim_range)

        self.histogram.update_fill(inf_lim=int(norm_bot_v * 100),
                                   sup_lim=int(norm_top_v * 100),
                                   color="#CCCCCC")

        # Updating threshold image
        self.__update_threshold_image(bottom_value, top_value)

        return
        # Update actor
        actor = self.controller.get_vtk_actor_by_threshold(bottom_value,
                                                           top_value)
        self.render_panel.add_object(actor)



if __name__ == "__main__":
    main_app = wx.App(None)
    from view.main_frame import MainFrame
    main_frame = MainFrame()
    add_frame_object = AddObjectDialog(main_frame)
    add_frame_object.Show()


    main_app.MainLoop()


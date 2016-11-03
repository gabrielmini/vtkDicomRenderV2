import wx

# Constraints
PATH_WIDTH = 6
PAD_LENGTH = 5


class FlatSlider(wx.Panel):
    """
        Class to represent a custom slider with minimalist appearance

        Inheritance:
            wx.Panel
    """

    def __init__(self, parent, min_v=0, max_v=100, step=1, value=50, radius=25,
                 colour="#CCCCCC"):
        """
            Constructor of the class FlatSlider

            Args:
                parent: (wx.Window) Is a parent window
                min_v: (number) Min value range of this control
                max_v: (number) Max value range of this control
                step: (number) Step between values
                value: (number) Assumed value for this control
                radius: (int) Radius of control button
                colour: (str - Hex Colour) Colour of button and path
        """
        wx.Panel.__init__(self, parent)

        self.button_radius = radius
        self.control_colour = colour
        self.SetMinSize((200, self.button_radius + 10))
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())

        w, h = self.GetSize()
        self._buffer = wx.EmptyBitmap(w, h, 32)
        self.px_position = 0

        # Treating values
        self.__value = None
        self.values_list = list()
        if min_v > max_v:  # Toggle values
            max_v, min_v = min_v, max_v

        self.values_list.append(min_v)
        temp_value = min_v

        while True:  # Creating a value list by step
            new_value = temp_value + step
            if new_value >= max_v:
                self.values_list.append(max_v)
                break
            else:
                self.values_list.append(new_value)
                temp_value = new_value

        # Binds
        self.Bind(wx.EVT_PAINT, self.__on_paint)
        self.Bind(wx.EVT_MOTION, self.__on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)
        self.Bind(wx.EVT_SIZE, self.__on_size)

        self.Refresh()
        # The component must be refreshed before to set a value.
        self.set_value(value)

    def __on_motion(self, evt):
        """
            Event Handler for mouse motion event

            Args:
                evt: (wx.Event) Event instance
        """
        if evt.Dragging():
            self.__set_value_by_x(evt.GetX())

    def __on_left_down(self, evt):
        """
            Event Handler for left down event

            Args:
                evt: (wx.Event) Event instance
        """
        self.__set_value_by_x(evt.GetX())

    def __set_value_by_x(self, coord_x):
        """
            Private function to set value in this control by x coordinate

            Args:
                coord_x: (int) Is the X coordinate to transform into a value

            Note:
                The value generated always is a float number.
        """
        # Range Correction
        if coord_x < self.min_px:
            coord_x = self.min_px
        elif coord_x > self.max_px:
            coord_x = self.max_px

        min_v, max_v = self.values_list[0], self.values_list[-1]
        prop = float(coord_x - self.min_px) / float(self.max_px - self.min_px)
        value = prop * (max_v - min_v) + min_v
        self.set_value(value)
        self.Refresh()
        command_event = wx.PyCommandEvent(wx.EVT_SLIDER.typeId, self.GetId())
        command_event.SetEventObject(self)
        wx.PostEvent(self.GetEventHandler(), command_event)

    def __on_size(self, evt):
        """
            Event Handler for window size event

            Args:
                evt: (wx.Event) Event instance
        """
        self._buffer = wx.EmptyBitmap(*self.ClientSize)
        self.Refresh()

    def __on_paint(self, evt):
        """
            Event Handler for paint event

            Args:
                evt: (wx.Event) Event instance
        """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._buffer, 0, 0)

    def __draw(self, dc):
        """
            Function to draw the components of this window

            Args:
                dc: (wx.DC) Device Context to draw components
        """
        # General Configuration
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetLogicalFunction(wx.COPY)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        x, y = self.GetSize()
        gc = wx.GraphicsContext.Create(dc)

        # Drawing Bar
        gc.SetBrush(wx.Brush(self.control_colour))
        gc.DrawRoundedRectangle(x=PAD_LENGTH,
                                y=y / 2 - PATH_WIDTH / 2,
                                w=x - PAD_LENGTH * 2,
                                h=PATH_WIDTH,
                                radius=PATH_WIDTH / 2)

        # Drawing Button
        gc.SetPen(wx.Pen(self.GetBackgroundColour(), 2))

        # Limits Definitions
        min_v, max_v = self.values_list[0], self.values_list[-1]
        if self.__value < min_v:
            self.__value = min_v
        elif self.__value > max_v:
            self.__value = max_v

        offset = PAD_LENGTH + 5 + self.button_radius / 2
        self.min_px, self.max_px = offset, x - offset

        # Range Treatment
        norm_value = float((self.__value - min_v)) / float(max_v - min_v)
        px_pos = int(norm_value * (self.max_px - self.min_px)) + self.min_px

        gc.DrawEllipse(x=px_pos - self.button_radius / 2,
                       y=y / 2 - self.button_radius / 2,
                       w=self.button_radius,
                       h=self.button_radius)

    def Refresh(self):
        """
            Function to refresh / redraw this component
        """
        dc = wx.MemoryDC()
        dc.SelectObject(self._buffer)
        self.__draw(dc)
        del dc
        super(FlatSlider, self).Refresh(eraseBackground=False)
        self.Update()

    # Value Manipulation
    def set_value(self, value):
        """
            Function to set value in this control

            Args:
                value: (int/float) Is a value to set
        """
        self.__value = value
        self.Refresh()

    def get_value(self):
        """
            Function to get value in this control

            Returns:
                (int/float) Value of this control
        """
        return self.__value


if __name__ == '__main__':
    main_app = wx.App(None)
    main_frame = wx.Frame(None, size=(1000, 400))
    root_sizer = wx.BoxSizer(wx.VERTICAL)
    main_frame.SetSizer(root_sizer)
    a = FlatSlider(main_frame, min_v=0, max_v=10, value=0)
    root_sizer.Add(a, 0, wx.EXPAND)
    # a.set_value(0)
    main_frame.Show()
    main_app.MainLoop()

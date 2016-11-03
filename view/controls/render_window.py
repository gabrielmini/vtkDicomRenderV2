from vtk import *
import wx
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor

class VtkRenderPanel(wx.Panel):
    def __init__(self, parent, use_axis=True):
        wx.Panel.__init__(self, parent)
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root_sizer)

        self.render_window = wxVTKRenderWindowInteractor(self, -1)
        root_sizer.Add(self.render_window, 1, wx.EXPAND)

        self.renderer = vtkRenderer()
        self.render_window.GetRenderWindow().AddRenderer(self.renderer)
        self.render_window.Enable(1)

        if use_axis:
            transform = vtkTransform()
            transform.Translate(-0.5, -1, -1)
            axes = vtkAxesActor()
            axes.SetUserTransform(transform)

            self.add_actor(axes)

        track_ball_style = vtkInteractorStyleTrackballCamera()
        self.render_window.SetInteractorStyle(track_ball_style)

        # Binds
        self.render_window.Bind(wx.EVT_MOTION, self.on_motion)

    def clear_objects(self):
        self.renderer.RemoveAllViewProps()

    def on_motion(self, evt):
        self.GetParent().ProcessEvent(evt)
        evt.Skip()

    def get_render_window(self):
        return self.render_window.GetRenderWindow()

    def add_actor(self, actor):
        # assert isinstance(actor, vtkActor)

        self.renderer.AddActor(actor)
        self.render_window.Render()

    def remove_actor(self, actor):
        self.renderer.RemoveActor(actor)

    def set_size(self, size):
        self.SetMinSize(size)

    def shutdown(self):
        self.renderer.RemoveAllViewProps()
        del self.renderer

        if self.render_window:
            self.render_window.GetRenderWindow().Finalize()
            del self.render_window


if __name__ == '__main__':
    main_app = wx.App(None)
    main_frame = wx.Frame(None)
    main_frame.SetSize((600, 400))
    r_sizer = wx.BoxSizer(wx.HORIZONTAL)
    main_frame.SetSizer(r_sizer)

    re = VtkRenderPanel(main_frame)
    re.set_size((400, 400))

    r_sizer.Add(re)

    cone_source = vtkConeSource()
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cone_source.GetOutputPort())
    actor = vtkActor()
    actor.SetMapper(mapper)
    re.add_actor(actor)

    main_frame.Show()
    main_app.MainLoop()

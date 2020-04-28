import wx
import wx.lib.sized_controls as sc
from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel
from wx.lib.pdfviewer import images
import wx.lib.agw.buttonpanel as bp


class LatexControl(wx.stc.StyledTextCtrl):
    def __init__(self, parent):
        super().__init__(parent)


class LatexPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(LatexPanel, self).__init__(parent, **kwargs)
        self.percent_zoom = 0.3
        self.tex_panel = wx.Panel(self)
        self.tex_panel.SetPosition((0, 0))
        self.tex_panel.SetSize((self.GetSize().width, self.GetSize().height))
        self.zoomIn = wx.Button(self.tex_panel, -1, "Zoom In")
        self.zoomOut = wx.Button(self.tex_panel, -1, "Zoom Out")
        self.Bind(wx.EVT_BUTTON, self.OnZoomIn, self.zoomIn)
        self.Bind(wx.EVT_BUTTON, self.OnZoomOut, self.zoomOut)
        self.viewer = pdfViewer(self.tex_panel, wx.NewId(), wx.DefaultPosition, wx.DefaultSize,
                                wx.HSCROLL | wx.VSCROLL | wx.SUNKEN_BORDER)
        # sizer
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add(self.zoomIn, 1, wx.EXPAND)
        h_sizer.Add(self.zoomOut, 1, wx.EXPAND)
        self.pdf_sizer = wx.BoxSizer(wx.VERTICAL)
        self.pdf_sizer.Add(h_sizer, 0, wx.EXPAND)
        self.pdf_sizer.Add(self.viewer, 1, wx.EXPAND)
        self.tex_panel.SetSizer(self.pdf_sizer)
        self.pdf_sizer.Fit(self)
        #
        self.viewer.LoadFile("la.pdf")
        self.viewer.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.latex_ctrl = LatexControl(self)
        # self.latex_ctrl.Hide()
        self.Layout()

    def render_content(self, tex):
        if tex is not None:
            # render text
            self.tex_panel.Hide()
            self.latex_ctrl.Show()
            self.latex_ctrl.SetValue(tex)
        else:
            # render PDF
            self.tex_panel.Show()
            self.latex_ctrl.Hide()
            self.viewer.LoadFile("la.pdf")

    def OnSize(self, e):
        self.tex_panel.SetPosition((0, 0))
        self.tex_panel.SetSize((self.GetSize().width, self.GetSize().height))
        self.latex_ctrl.SetPosition((0, 0))
        self.latex_ctrl.SetSize((self.GetSize().width, self.GetSize().height))
        self.tex_panel.Layout()

    def OnButtonClicked(self, e):
        print('OnButtonClicked')

    def OnZoomIn(self, e):
        self.percent_zoom = min(self.percent_zoom*2, 1.2)
        self.viewer.SetZoom(self.percent_zoom)

    def OnZoomOut(self, e):
        self.percent_zoom = max(0.15, self.percent_zoom/2.0)
        self.viewer.SetZoom(self.percent_zoom)

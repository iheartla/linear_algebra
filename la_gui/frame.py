# -*- coding: utf-8 -*
import wx
import os
import sys

sys.path.append('../')
from la_parser.parser import parse_and_translate
from la_gui.la_ctrl import LaTextControl
from la_gui.python_ctrl import PyTextControl
from la_gui.latex_panel import LatexPanel


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        w, h = wx.DisplaySize()
        wx.Frame.__init__(self, parent, title=title, pos=(w / 4, h / 4))
        # status
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(1)
        # Menu
        menu_file = wx.Menu()
        item_open = menu_file.Append(wx.ID_OPEN, "&Open", " Open a file to edit")
        item_about = menu_file.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menu_run = wx.Menu()
        item_run = menu_run.Append(wx.NewId(), "&Run program", " Information about this program")
        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, "&File")
        menu_bar.Append(menu_run, "&Run")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.OnOpen, item_open)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        self.Bind(wx.EVT_MENU, self.OnKeyEnter, item_run)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # panel
        self.control = LaTextControl(self)
        self.pyPanel = PyTextControl(self)
        self.latexPanel = LatexPanel(self)
        # sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.control, 1, wx.EXPAND, 100)
        sizer.Add(self.pyPanel, 1, wx.EXPAND, 100)
        sizer.Add(self.latexPanel, 1, wx.EXPAND, 100)
        self.SetSizer(sizer)
        sizer.Fit(self)
        # hot key
        r_new_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnKeyEnter, id=r_new_id)
        zoom_in_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnZoomIn, id=zoom_in_id)
        zoom_out_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnZoomOut, id=zoom_out_id)
        acc_zoom_out = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('R'), r_new_id), (wx.ACCEL_CTRL, ord('='), zoom_in_id), (wx.ACCEL_CTRL, ord('-'), zoom_out_id)])
        self.SetAcceleratorTable(acc_zoom_out)

        self.Show()
        self.SetSize((1000, 600))
        self.control.SetValue('''B = [ A C ]

where

A: ℝ ^ (4 × 4): a matrix
C: ℝ ^ (4 × 4): a matrix
E: { ℤ × ℤ }''')
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)

    def OnButtonClicked(self, e):
        print('frame clicked')

    def SetItemsPos(self):
        w, h = self.GetSize()
        transW, transH = self.translateBtn.GetSize()
        sH = 40
        self.control.SetSize((w - transW) / 2, h - sH)
        self.control.SetPosition((0, 0))
        self.translateBtn.SetPosition(((w - transW) / 2, h / 2 - transH / 2))
        # self.latexPanel.SetSize((w - transW) / 2, h - sH)
        # self.latexPanel.SetPosition(((w + transW) / 2, 0))
        self.pyPanel.SetSize((w - transW) / 2, h - sH)
        self.pyPanel.SetPosition(((w + transW) / 2, 0))

    def OnSize(self, e):
        self.Layout()
        # self.SetItemsPos()

    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "LA editor in wxPython", "About LA Editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)

    def OnKeyEnter(self, e):
        print('Start compilingr')
        self.OnTranslate(e)

    def OnZoomIn(self, e):
        self.latexPanel.OnZoomIn(e)

    def OnZoomOut(self, e):
        self.latexPanel.OnZoomOut(e)

    def OnTranslate(self, e):
        self.statusbar.SetStatusText("Compiling ...", 0)
        self.Update()
        result = parse_and_translate(self.control.GetValue())
        # self.latexPanel.render_content(result[0])
        self.pyPanel.SetText(result[0])
        if result[1] == 0:
            self.statusbar.SetStatusText("Finished", 0)
        else:
            self.statusbar.SetStatusText("Error", 0)

    def OnOpen(self, e):
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            f = open(os.path.join(dirname, filename), 'r')
            self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()

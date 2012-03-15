#!/usr/bin/python
""" Window to save/delete the position log and markers.
    KJR 30 Oct 2010
"""
import wx

class MainApp( wx.App ): 
    def __init__( self, redirect=False, filename=None ):
        wx.App.__init__( self, redirect, filename )
        
        self.mainframe = MainFrame()
        
class MainFrame( wx.Frame ):
    def __init__( self, parent=None, id=wx.ID_ANY, title='Manage Markers', size=wx.Size(350, 80) ):
        wx.Frame.__init__( self, parent=parent, id=id, title=title, size=size )
        
        try:
            self.markers = parent.markers
            self.parent = parent
        except AttributeError:
            """ we're not calling this from the real program, so just generate fake data for testing """
            self.markers = [dict(x=0, y=0, label='A'), dict(x=1, y=1, label='B')]
            self.parent = None
            
        self.mainpanel = wx.Panel( self, id=wx.ID_ANY )

        box = wx.BoxSizer( wx.VERTICAL )
        boxMarkers = wx.BoxSizer( wx.HORIZONTAL )
        
        choices = ["all markers"]
        for item in self.markers:
            choices.append( item['label'] )
        self.MarkerListDropdown = wx.ComboBox( parent=self.mainpanel, id=wx.ID_ANY, choices=choices,
                                               style=wx.CB_DROPDOWN|wx.CB_READONLY )
        self.MarkerListDropdown.SetValue("all markers")
        boxMarkers.Add( self.MarkerListDropdown )
        
        deleteMarkersButton = wx.Button( self.mainpanel, wx.ID_ANY, "Delete" )
        deleteMarkersButton.Bind( wx.EVT_BUTTON, self.on_button_clicked_delete_markers )
        boxMarkers.Add( deleteMarkersButton )

        box.Add( boxMarkers,  proportion=1, flag=wx.CENTER|wx.ALL, border=5 )
        
        self.mainpanel.SetSizer( box )

        self.Centre()
        self.Show( True )


    def on_button_clicked_delete_markers( self, event ):
        if self.MarkerListDropdown.Value == 'all markers':
            dlg = wx.MessageDialog( self, 'Are you sure you want to delete all markers?', 
                "Delete Markers", wx.YES_NO | wx.ICON_QUESTION )
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                del self.markers[:]
                self.MarkerListDropdown.Clear()
                if self.parent is not None:
                    self.parent.MarkerListDropdown.Clear()
                    self.parent.update_plot()
            else:
                dlg.Destroy()
        else:
            for marker in self.markers:
                if marker['label'] == self.MarkerListDropdown.Value:
                    self.markers.remove( marker )
                    self.MarkerListDropdown.Clear()
                    self.MarkerListDropdown.Append( "all markers" )
                    for item in self.markers:
                        self.MarkerListDropdown.Append( item['label'] )
                    
                    # and update the list on the position log frame, too:
                    if self.parent is not None:
                        self.parent.MarkerListDropdown.Clear()
                        for item in self.markers:
                            self.parent.MarkerListDropdown.Append( item['label'] )
                        self.parent.update_plot()

        
if __name__== '__main__': 

    app = MainApp()
    app.MainLoop()


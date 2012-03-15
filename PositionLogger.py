#!/usr/bin/python
""" Window to save/delete the position log and markers.
    KJR 30 Oct 2010
"""
import wx
import matplotlib
if matplotlib.get_backend() != 'WXAgg':
    # this is actually just to check if it's loaded. if it already was loaded
    # and set to a different backend, then we couldn't change it anyway.
    matplotlib.use('WXAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as MPLToolbar
import pylab
from wx._controls import TE_PROCESS_ENTER

import ManageMarkers

ID_Stuff_ManageMarkers = wx.NewId()
ID_MarkerLog_Erase = wx.NewId()
ID_PositionLog_Erase = wx.NewId()

class MainApp( wx.App ): 
    def __init__( self, redirect=False, filename=None ):
        wx.App.__init__( self, redirect, filename )
        
        self.mainframe = MainFrame()
        
class MainFrame( wx.Frame ):
    def __init__( self, parent=None, id=wx.ID_ANY, title='Position Logger',
                 size=wx.Size(500,500) ):
        wx.Frame.__init__( self, None, id=id, title=title, size=size )
        self.Bind( wx.EVT_CLOSE, self.on_close_mainframe )
        
        self.x_log = parent.x_log
        self.y_log = parent.y_log
        self.markers = parent.markers
        self.positioners = parent.positioners
        self.moveto = False
        self.cid = None
        
        plotpanel = wx.Panel( self, id=wx.ID_ANY )
        box = wx.BoxSizer( wx.VERTICAL )

        self.PositionLogAutoRange = True
        #self.fig = pylab.figure( facecolor='white' )
        self.fig = Figure( facecolor='white' )
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel( 'X position (mm)' )
        self.axes.set_ylabel( 'Y position (mm)' )
        self.axes.set_title( 'Motor Position Log' )
        if self.positioners['motorX']['direction'] == -1:
            self.PositionLogMaxPlotRange_X = [self.positioners['motorX']['control'].GetStageAxisInfo_MinPos(),
                      self.positioners['motorX']['control'].GetStageAxisInfo_MaxPos()]
        else:
            self.PositionLogMaxPlotRange_X = [self.positioners['motorX']['control'].GetStageAxisInfo_MaxPos(),
                      self.positioners['motorX']['control'].GetStageAxisInfo_MinPos()]
            
        if self.positioners['motorY']['direction'] == -1:
            self.PositionLogMaxPlotRange_Y = [self.positioners['motorY']['control'].GetStageAxisInfo_MinPos(),
                      self.positioners['motorY']['control'].GetStageAxisInfo_MaxPos()]
        else:
            self.PositionLogMaxPlotRange_Y = [self.positioners['motorY']['control'].GetStageAxisInfo_MaxPos(),
                      self.positioners['motorY']['control'].GetStageAxisInfo_MinPos()]
            
        self.axes.set_xlim( self.PositionLogMaxPlotRange_X )
        self.axes.set_ylim( self.PositionLogMaxPlotRange_Y )
        self.axes.set_aspect('equal')
        
        self.canvas = FigureCanvas( parent=plotpanel, id=wx.ID_ANY, figure=self.fig )
        box.Add( self.canvas, proportion = 1, flag=wx.EXPAND, border=10 )

        ######## toolbar sizer; includes marker making button and text entry field
        boxToolbar = wx.BoxSizer( wx.HORIZONTAL )
        mpl_toolbar = MPLToolbar( self.fig.canvas )
        boxToolbar.Add( mpl_toolbar, proportion = .2, flag=wx.BOTTOM, border=5 )
        
        boxToolbar.AddStretchSpacer(1)
        
        self.button_move_to_click = wx.Button( plotpanel, wx.ID_ANY, 'move to click' )
        boxToolbar.Add( self.button_move_to_click, flag=wx.CENTER )
        self.button_move_to_click.Bind( wx.EVT_BUTTON, self.on_button_clicked_move_to_click )

        button_AddMarker = wx.Button( plotpanel, wx.ID_ANY, 'Add Marker' )
        boxToolbar.Add( button_AddMarker, flag=wx.CENTER )
        button_AddMarker.Bind( wx.EVT_BUTTON, self.on_button_clicked_add_marker )

        self.text_marker = wx.TextCtrl( plotpanel, wx.ID_ANY, '', style=TE_PROCESS_ENTER )
        self.text_marker.Bind( wx.EVT_TEXT_ENTER, self.on_button_clicked_add_marker )
        boxToolbar.Add( self.text_marker, flag=wx.CENTER|wx.RIGHT, border=2 )

        box.Add( boxToolbar, 0, wx.EXPAND )
        
        ### buttons for changing ranges/autoscaling. includes moving to markers
        boxButtons = wx.BoxSizer( wx.HORIZONTAL )
        button_ResetRange = wx.Button( plotpanel, wx.ID_ANY, 'Full Scale' )
        boxButtons.Add( button_ResetRange, flag=wx.CENTER )
        button_ResetRange.Bind( wx.EVT_BUTTON, self.on_button_clicked_reset_range )
        
        self.button_AutoRange = wx.Button( plotpanel, wx.ID_ANY, 'Stop Auto-Scale' )
        boxButtons.Add( self.button_AutoRange, flag=wx.CENTER )
        self.button_AutoRange.Bind( wx.EVT_BUTTON, self.on_button_clicked_autoscale_range )
        
        boxButtons.AddStretchSpacer( 1 )

        boxButtons.Add( wx.StaticText( parent=plotpanel, id=wx.ID_ANY, label="Move to marker: " ), flag=wx.CENTER )
        self.MarkerListDropdown = wx.ComboBox( parent=plotpanel, id=wx.ID_ANY, choices=[ d['label'] for d in self.markers ],
                                               style=wx.CB_DROPDOWN|wx.CB_READONLY )
        boxButtons.Add( self.MarkerListDropdown, flag=wx.CENTER )

        button_MoveToMarker = wx.Button( plotpanel, wx.ID_ANY, 'Go' )
        boxButtons.Add( button_MoveToMarker, flag=wx.CENTER )
        button_MoveToMarker.Bind( wx.EVT_BUTTON, self.on_button_clicked_move_to_marker )

        box.Add( boxButtons, proportion=0, flag=wx.EXPAND )

        plotpanel.SetSizer( box )

        self.add_menu_bar()
        self.Show( True )
        self.update_plot()


    def add_menu_bar(self):
        menuBar = wx.MenuBar()

        """ Stuff menu
        """
        stuff_menu = wx.Menu()
        stuff_menu.Append( ID_Stuff_ManageMarkers, "Manage Markers", "Lets you delete individual markers" )
        wx.EVT_MENU( self, ID_Stuff_ManageMarkers, self.on_stuff_menu_manage_markers )
    
        stuff_menu.Append( ID_MarkerLog_Erase, "Erase Marker Log", "Pretty self-explanatory...")
        wx.EVT_MENU( self, ID_MarkerLog_Erase, self.on_stuff_menu_erase_marker_log )

        stuff_menu.Append( ID_PositionLog_Erase, "Erase Position Log", "Pretty self-explanatory...")
        wx.EVT_MENU( self, ID_PositionLog_Erase, self.on_stuff_menu_erase_position_log )

        menuBar.Append( stuff_menu, "&Stuff" )

        self.SetMenuBar( menuBar )

    
    def on_button_clicked_add_marker( self, event ):
        markername = self.text_marker.GetValue()

        if len( self.x_log ) == 0:
            self.x_log.append( self.positioners['motorX']['control'].GetPosition() )
            self.y_log.append( self.positioners['motorY']['control'].GetPosition() )

        self.markers.append( dict( x=self.x_log[-1], y=self.y_log[-1], label=markername ) )
        self.MarkerListDropdown.Append( markername )
        self.update_plot()
        self.text_marker.SetValue("")


    def on_button_clicked_autoscale_range( self, event ):
        if self.PositionLogAutoRange == False:
            self.PositionLogAutoRange = True
            self.update_plot()
            self.button_AutoRange.SetLabel( "Stop Auto-Scale" )
        else:
            self.PositionLogAutoRange = False
            self.button_AutoRange.SetLabel( "Start Auto-Scale" )
        

    def on_button_clicked_move_to_click( self, event ):
        if self.moveto == False:
            self.moveto = True
            if self.cid is not None:
                self.fig.canvas.mpl_disconnect( self.cid )
            self.cid = self.fig.canvas.mpl_connect( 'button_press_event', self.on_mouse_clicked )
            self.button_move_to_click.SetLabel( "cancel" )
        else:
            # then we're trying to cancel the move-to
            self.fig.canvas.mpl_disconnect( self.cid )
            self.cid = None
            self.button_move_to_click.SetLabel( "move to click" )
            self.moveto = False

    
    def on_button_clicked_move_to_marker( self, event ):
        target = self.MarkerListDropdown.GetValue()
        for marker in self.markers:
            if marker['label'] == target:
                if self.positioners['motorX'] is not None:
                    self.positioners['motorX']['control'].MoveAbsoluteEx( marker['x'], wait=False )
                    self.x_log.append( self.positioners['motorX']['control'].GetPosition() )
                if self.positioners['motorY'] is not None:
                    self.positioners['motorY']['control'].MoveAbsoluteEx( marker['y'], wait=False )
                    self.y_log.append( self.positioners['motorY']['control'].GetPosition() )
                self.update_plot()
                return # if you have multiple identically-named markers, move to the first found.

        
    def on_button_clicked_reset_range( self, event ):
        self.axes.set_xlim( self.PositionLogMaxPlotRange_X )
        self.axes.set_ylim( self.PositionLogMaxPlotRange_Y )
        self.fig.canvas.draw()
        if self.PositionLogAutoRange == True:
            self.PositionLogAutoRange = False
            self.button_AutoRange.SetLabel( "Start Auto-Scale" )
            

    def on_close_mainframe( self, event ):
        self.Destroy()
        
 
    def on_mouse_clicked( self, event ):
        if not event.inaxes:
            return
        
        self.fig.canvas.mpl_disconnect( self.cid )
        self.cid = None

        if self.moveto:
            self.moveto = False
            self.button_move_to_click.SetLabel( "move to click" )
            
            if self.positioners['motorX'] is not None:
                self.positioners['motorX']['control'].MoveAbsoluteEx( event.xdata, wait=False )
                
            if self.positioners['motorY'] is not None:
                self.positioners['motorY']['control'].MoveAbsoluteEx( event.ydata, wait=False )


    def on_stuff_menu_manage_markers( self, event ):
        try: 
            if not self.managemarkers.Show( True ):
                self.managemarkers.Raise()
        except:
            self.managemarkers = ManageMarkers.MainFrame( parent=self )
        

    def on_stuff_menu_erase_marker_log( self, event ):
        dlg = wx.MessageDialog( self, 'Are you sure you want to delete all markers?', 
            "Delete Markers", wx.YES_NO | wx.ICON_QUESTION )
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            del self.markers[:]
            self.MarkerListDropdown.Clear()
            self.update_plot()
            try: 
                if self.managemarkers.Show( True ):
                    self.managemarkers.MarkerListDropdown.Clear()
            except:
                pass
        else:
            dlg.Destroy()



    def on_stuff_menu_erase_position_log( self, event ):
        dlg = wx.MessageDialog( self, 'Are you sure you want to delete the position log?', 
            "Delete Position Log", wx.YES_NO | wx.ICON_QUESTION )
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            del self.x_log[:]
            del self.y_log[:]
            self.update_plot()
        else:
            dlg.Destroy()



    def update_plot( self ):
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()

        if len( self.x_log ) == 0:
            self.x_log.append( self.positioners['motorX']['control'].GetPosition() )
            self.y_log.append( self.positioners['motorY']['control'].GetPosition() )

        self.axes.cla()
        self.axes.plot( self.x_log, self.y_log, 'b-' )
        self.axes.plot( self.x_log[-1], self.y_log[-1], 'bo' ) # mark current loc.
        for marker in self.markers:
            self.axes.plot( marker['x'], marker['y'], 's')
            self.axes.text( marker['x']-0.001, marker['y']+0.001, marker['label'] )

        self.axes.set_xlabel( 'X position (mm)' )
        self.axes.set_ylabel( 'Y position (mm)' )
        self.axes.set_title( 'Motor Position Log' )
        
        if not self.PositionLogAutoRange:
            # just leave the axes where they were, don't autoscale
            self.axes.set_xlim( xlim )
            self.axes.set_ylim( ylim )
        
        self.axes.set_aspect('equal')
        self.fig.canvas.draw()
        

if __name__== '__main__': 

    app = MainApp()
    app.MainLoop()


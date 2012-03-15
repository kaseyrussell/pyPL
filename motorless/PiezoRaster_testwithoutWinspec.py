#!/usr/bin/python
""" 
    Here we have a window to control timestepping 
"""
import wx
from wx._controls import TE_PROCESS_ENTER
import matplotlib
if matplotlib.get_backend() != 'WXAgg':
    # this is actually just to check if it's loaded. if it already was loaded
    # and set to a different backend, then we couldn't change it anyway.
    matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as MPLToolbar

import pylab
import time
from threading import Thread

import sys
sys.path.append( 'C:\\Python26\\Lib\\kasey' )
import kasey_utils as kc
import kasey_fitspectra as kcfit
import WinspecUtils as spe
import glob
import os

class MainApp(wx.App): 
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        
        self.mainframe = MakeMainWindow()
        
class MakeMainWindow( wx.Frame ):
    def __init__( self, parent=None, id=wx.ID_ANY ):
        wx.Frame.__init__( self, parent=None, id=wx.ID_ANY, title='Raster Piezos', size=wx.Size(400, 300) )
        self.mainpanel = MainPanel( self )
        self.Centre()
        self.Show(True)

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()
EVT_UPDATE_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

def EVT_UPDATE(win, func):
    """Define Update Event."""
    win.Connect(-1, -1, EVT_UPDATE_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class UpdateEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Update Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_UPDATE_ID)
        self.data = data

# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class. I stole this class (and the Result Event Class above) from wiki.wxpython.org"""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        values = []
        for i in range(10):
            # here we're starting a scan with WinSpec
            time.sleep(1)
            values.append( i**2 )
            
            if self._want_abort:
                # Use a result of None to acknowledge the abort (of
                # course you can use whatever you'd like or even
                # a separate event type)
                wx.PostEvent(self._notify_window, ResultEvent(None))
                return

            wx.PostEvent(self._notify_window, UpdateEvent(i))
            
        wx.PostEvent(self._notify_window, ResultEvent(True))

    def abort(self):
        """abort worker thread."""
        self._want_abort = 1
        

class MainPanel( wx.Panel ):
    def __init__( self, parent, id=wx.ID_ANY ):
        wx.Panel.__init__( self, parent, id )

        self.SetFocus() # apparently only necessary on linux b/c a frame can't have focus (?)
        self.Bind( wx.EVT_CHAR, self.On_keyboard_pressed )
        
        self.DataPath = ""   # we don't yet know where the data is stored
        self.SPEFiles = None # a list of SPE files to plot
        
        box = wx.BoxSizer( wx.VERTICAL )


        """ Set the scan width parameters
        """
        box_setwidth = wx.BoxSizer( wx.HORIZONTAL )
        box_setwidth.Add( wx.StaticText( self, wx.ID_ANY, "Scan X (um):" ), flag=wx.ALL|wx.CENTER, border=3 )
        stepList = ['1', '2', '5', '10', '20']
        defaultwidth = stepList[2]
        self.scan_width = defaultwidth
        self.combo_scanwidth = wx.ComboBox( self, wx.ID_ANY, value=defaultwidth, size=(60,25),
                                           choices=stepList )
        self.combo_scanwidth.SetToolTip(wx.ToolTip("Select scan width in um from dropdown-list"))
        box_setwidth.Add( self.combo_scanwidth, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.combo_scanwidth.Bind( wx.EVT_TEXT, self.On_combo_scanwidth_Changed )
        
        box_setwidth.Add( wx.StaticText( self, wx.ID_ANY, ",  # points:" ), flag=wx.ALL|wx.CENTER, border=3 )
        pointList = ['10', '15', '20', '25']
        defaultpoints = pointList[0]
        self.scan_width = defaultpoints
        self.combo_scanxpoints = wx.ComboBox( self, wx.ID_ANY, value=defaultpoints, size=(60,25),
                                           choices=pointList )
        self.combo_scanxpoints.SetToolTip(wx.ToolTip("Select number of points for width of scan"))
        box_setwidth.Add( self.combo_scanxpoints, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.combo_scanxpoints.Bind( wx.EVT_TEXT, self.On_combo_scanxpoints_Changed )

        box.Add( box_setwidth,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=3 )
        


        """ Set the scan height parameters
        """
        box_setheight = wx.BoxSizer( wx.HORIZONTAL )
        box_setheight.Add( wx.StaticText( self, wx.ID_ANY, "Scan Y (um):" ), flag=wx.ALL|wx.CENTER, border=3 )
        stepList = ['1', '2', '5', '10', '20']
        defaultheight = stepList[2]
        self.scan_height = defaultheight
        self.combo_scanheight = wx.ComboBox( self, wx.ID_ANY, value=defaultheight, size=(60,25),
                                           choices=stepList )
        self.combo_scanheight.SetToolTip(wx.ToolTip("Select scan height in um from dropdown-list"))
        box_setheight.Add( self.combo_scanheight, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.combo_scanheight.Bind( wx.EVT_TEXT, self.On_combo_scanheight_Changed )

        box_setheight.Add( wx.StaticText( self, wx.ID_ANY, ",  # points:" ), flag=wx.ALL|wx.CENTER, border=3 )
        pointList = ['10', '15', '20', '25']
        defaultpoints = pointList[0]
        self.scan_width = defaultpoints
        self.combo_scanypoints = wx.ComboBox( self, wx.ID_ANY, value=defaultpoints, size=(60,25),
                                           choices=pointList )
        self.combo_scanypoints.SetToolTip(wx.ToolTip("Select number of points for height of scan"))
        box_setheight.Add( self.combo_scanypoints, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.combo_scanypoints.Bind( wx.EVT_TEXT, self.On_combo_scanypoints_Changed )

        box.Add( box_setheight,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=3 )
        


        """ Set the starting point for the scan.
        """
        box_setstart = wx.BoxSizer( wx.HORIZONTAL )
        box_setstart.Add( wx.StaticText( self, wx.ID_ANY, "Start at:" ), flag=wx.ALL|wx.CENTER, border=3 )
        corners = ['top left corner', 'top right corner', 'bottom left corner', 'bottom right corner']
        defaultstart = corners[0]
        self.scan_width = defaultstart
        self.choice_setstart = wx.Choice( self, wx.ID_ANY, size=(160,25), choices=corners )
        self.choice_setstart.SetToolTip(wx.ToolTip("Select starting corner of scan"))
        box_setstart.Add( self.choice_setstart, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.choice_setstart.Bind( wx.EVT_CHOICE, self.On_choice_setstart_Changed )

        box.Add( box_setstart,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=3 )



        """ Set the scan direction (rows or columns).
        """
        box_setdirection = wx.BoxSizer( wx.HORIZONTAL )
        box_setdirection.Add( wx.StaticText( self, wx.ID_ANY, "Sweep by:" ), flag=wx.ALL|wx.CENTER, border=3 )
        self.scan_direction_choices = ['rows', 'columns']
        self.scan_direction = self.scan_direction_choices[0]
        self.choice_setdirection = wx.Choice( self, wx.ID_ANY, size=(90,25), choices=self.scan_direction_choices )
        self.choice_setdirection.SetToolTip(wx.ToolTip("Select scan direction"))
        box_setdirection.Add( self.choice_setdirection, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.choice_setdirection.Bind( wx.EVT_CHOICE, self.On_choice_setdirection_Changed )

        box.Add( box_setdirection,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=3 )



        """ Set the behavior at the end of the row/column (reverse or jump across?).
        """
        box_setreverse = wx.BoxSizer( wx.HORIZONTAL )
        self.reverse_text = wx.StaticText( self, wx.ID_ANY, "" )
        if self.scan_direction == self.scan_direction_choices[0]:
            self.reverse_text.SetLabel('At end of each row,')
        else:
            self.reverse_text.SetLabel('At end of each column,')
        
        box_setreverse.Add( self.reverse_text, flag=wx.ALL|wx.CENTER, border=3 )
        directions = ['reverse direction for next line', 'jump across scan window']
        self.scan_reverse = directions[0]
        self.choice_setreverse = wx.Choice( self, wx.ID_ANY, size=(235,25), choices=directions )
        self.choice_setreverse.SetToolTip(wx.ToolTip("Reverse each line or not?"))
        box_setreverse.Add( self.choice_setreverse, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.choice_setreverse.Bind( wx.EVT_CHOICE, self.On_choice_setreverse_Changed )

        box.Add( box_setreverse,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=3 )



        """ Set the filename base.
        """
        boxSetFname = wx.BoxSizer( wx.HORIZONTAL )
        boxSetFname.Add( wx.StaticText( self, wx.ID_ANY, "Filename base:" ), flag=wx.ALL|wx.CENTER, border=3 )
        defaultFnameBase = "scan"
        self.FnameBase = defaultFnameBase
        self.text_fname = wx.TextCtrl( self, wx.ID_ANY, defaultFnameBase, style=TE_PROCESS_ENTER, size=(120,25) )
        boxSetFname.Add( self.text_fname, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.text_fname.Bind( wx.EVT_TEXT_ENTER, self.On_SetFname_Changed )
        self.text_fname.Bind( wx.EVT_TEXT, self.On_SetFname_Changed )
        box.Add( boxSetFname,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=3 )
        

        """ See example filename.
        """
        self.text_exampleFname = wx.StaticText( self, wx.ID_ANY, "" )
        self.On_SetFname_Changed( None )
        box.Add( self.text_exampleFname,  proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=10 )
        

        """ Disclaimer on directory
        """
        box.Add( wx.StaticText( self, wx.ID_ANY, 
                                "Files will get saved in the current WinSpec directory."),
                                proportion = 1, flag=wx.LEFT|wx.ALIGN_LEFT, border=5 )
        

        """ Start and Stop buttons
        """
        boxButtons = wx.BoxSizer( wx.HORIZONTAL )
        self.button_Start = wx.Button( self, wx.ID_ANY, 'Start' )
        boxButtons.Add( self.button_Start, proportion = 1, flag=wx.CENTER, border=10 )
        self.button_Start.Bind( wx.EVT_BUTTON, self.On_button_Start_Clicked )
        
        self.button_Stop = wx.Button( self, wx.ID_ANY, 'Stop' )
        boxButtons.Add( self.button_Stop, proportion = 1, flag=wx.CENTER, border=10 )
        self.button_Stop.Bind( wx.EVT_BUTTON, self.On_button_Stop_Clicked )
        box.Add( boxButtons,  proportion = 1, flag=wx.CENTER, border=10 )


        """ Indicator text
        """
        self.status = wx.StaticText(self, -1, '', pos=(0,100))
        box.Add( self.status,  proportion = 1, flag=wx.LEFT|wx.CENTER, border=10 )
        

        """ File dialog button
        """
        self.button_Directory = wx.Button( self, wx.ID_ANY, 'Find SPE Files' )
        box.Add( self.button_Directory, proportion = 1, flag=wx.CENTER, border=10 )
        self.button_Directory.Bind( wx.EVT_BUTTON, self.On_button_Directory_Clicked )

        self.SetSizer( box )

        # Set up event handler for any worker thread results
        EVT_RESULT( self, self.OnResult )
        EVT_UPDATE( self, self.OnThreadUpdate )

        # And indicate we don't have a worker thread yet
        self.worker = None
        
        
    def On_keyboard_pressed( self, event ):
        if event.GetKeyCode() == wx.WXK_LEFT:
            print "Left!"
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            print "Right!"
        elif event.GetKeyCode() == wx.WXK_UP:
            print "Up!"
        elif event.GetKeyCode() == wx.WXK_DOWN:
            print "Down!"
        event.Skip()

    def On_combo_scanwidth_Changed( self, event ):
        self.scan_width = float( self.combo_scanwidth.GetValue() )
        
    
    def On_combo_scanxpoints_Changed( self, event ):
        self.scan_xpoints = int( self.combo_scanxpoints.GetValue() )
        

    def On_combo_scanheight_Changed( self, event ):
        self.scan_height = float( self.combo_scanheight.GetValue() )
        
    
    def On_combo_scanypoints_Changed( self, event ):
        self.scan_ypoints = int( self.combo_scanypoints.GetValue() )
        
    
    def On_choice_setstart_Changed( self, event ):
        self.scan_start = self.choice_setstart.GetStringSelection()
        

    def On_choice_setdirection_Changed( self, event ):
        self.scan_direction = self.choice_setdirection.GetStringSelection()
        if self.scan_direction == self.scan_direction_choices[0]:
            self.reverse_text.SetLabel('At end of each row,')
        else:
            self.reverse_text.SetLabel('At end of each column,')
        self.Layout()


    def On_choice_setreverse_Changed( self, event ):
        self.scan_reverse = self.choice_setreverse.GetStringSelection()
        

    def On_SetFname_Changed( self, event ):
        self.FnameBase = self.text_fname.GetValue()
        self.text_exampleFname.SetLabel( "(e.g. " + self.FnameBase + "_x#_y#.SPE)" )
        
    
    def On_button_Start_Clicked( self, event ):
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            self.status.SetLabel('Starting scan.')
            self.worker = WorkerThread(self)
            self.worker.setDaemon( True ) # kill this thread if we close the main app
            self.worker.start()

            #self.fig = pylab.figure()
            #self.current_fignum = pylab.get_fignums()[-1]
            #self.axes = self.fig.add_subplot(111)
            #self.fig.show()
            

    def On_button_Stop_Clicked( self, event ):
        # Flag the worker thread to stop if running
        if self.worker:
            self.status.SetLabel('Trying to abort scan.')
            self.worker.abort()
        

    def On_button_Directory_Clicked( self, event ):
        dlg = wx.DirDialog(self, "To enable plotting, select directory where WinSpec is saving the SPE files:",
                          style=wx.DD_DEFAULT_STYLE,
                          defaultPath=self.DataPath
                           )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            self.DataPath = dlg.GetPath()
            #print 'You selected: %s\n' % self.DataPath
            if len( pylab.get_fignums() ) == 0 or pylab.get_fignums()[-1] != self.current_fignum:
                self.fig = pylab.figure()
                self.current_fignum = pylab.get_fignums()[-1]
                self.axes = self.fig.add_subplot(111)
                self.fig.show()
            
            if self.plotcolormap():
                self.fig.canvas.draw()
            

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()


    def OnThreadUpdate( self, event ):
        self.status.SetLabel( 'Done with acquisition #%s' % (event.data) )
        if len( pylab.get_fignums() ) > 0 and pylab.get_fignums()[-1] == self.current_fignum:
            if self.plotcolormap():
                self.fig.canvas.draw()


    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            self.status.SetLabel('Scan aborted.')
        elif event.data is True:
            self.status.SetLabel('Scan is done.')

        self.worker = None


    def SetFname(self):
        self.Fname = self.FnameBase + "_" + str(self.time_of_scan) + "s"
        

    def plotcolormap(self):
        files = glob.glob( self.DataPath + "\\" + self.FnameBase + '*.SPE' ) # get a list of all non-glued txt files
        
        # assume filename is of the format: timeseriesvacuum_2640.SPE
        # where 2640 is the time in seconds since the start of the series of scans
        try:
            files.sort( key=lambda x: int(os.path.split(x)[1].split('s.SPE')[0].split('_')[1]) ) # sort by acquisition start time
        except ValueError:
            # there was a file in there with the same filename base but that wasn't part of the series
            # (e.g. "timeseriesvacuum_after blocking laser 10mn.SPE") 
            for fname in files:
                if not os.path.split(fname)[1].split('s.SPE')[0].split('_')[1].isdigit():
                    files.remove( fname )
            files.sort( key=lambda x: int(os.path.split(x)[1].split('s.SPE')[0].split('_')[1]) ) # sort by acquisition start time
            
        if len(files) == 0:
            print "no SPE files found."
            return False
        
        if files == self.SPEFiles:
            # print "same list as last time."
            pass
        else:
            # presumably we could save some effort and not load the whole list every time,
            # but this program is meant to be used while taking spectra every 30sec or so,
            # which would give us plenty of time to refresh the plot each time.
            # but the plotting itself is probably the most expensive part, so this is moot...
            self.SPEFiles = files
                
            self.spectra = []
            self.time = []
            
            for fname in files:
                self.time.append( float( os.path.split(fname)[1].split('s.SPE')[0].split('_')[-1] ) )
                
                s = spe.Spectrum( fname )
                s.remove_linear_background( npoints=10 )
                s.normalize()
                
                self.spectra.append( s.lum )
            
            self.wavelen = s.wavelen
            
        wavelen_image = kc.centers_to_corners( self.wavelen )
        time_image = kc.centers_to_corners( self.time )/60.0
        spectra_image = pylab.array( self.spectra )
        
        self.axes.pcolormesh( time_image, wavelen_image, spectra_image.transpose(), cmap='copper' )
        self.axes.set_ylim( wavelen_image[0], wavelen_image[-1] )
        self.axes.set_xlim( time_image[0], time_image[-1] )
        self.axes.set_ylabel( 'Wavelength (nm)' )
        self.axes.set_xlabel( 'Time (min)' )
        self.axes.set_title( self.FnameBase )
        return True



if __name__== '__main__': 
    app = MainApp()

    app.MainLoop()

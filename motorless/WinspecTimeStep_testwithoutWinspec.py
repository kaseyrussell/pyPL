#!/usr/bin/python
""" 
    Here we have a window to control timestepping 
"""
import wx
from wx._controls import TE_PROCESS_ENTER
import matplotlib # this should get pulled in by wxmpl, so don't need it if you have wxmpl
matplotlib.use('WXAgg')
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
        wx.Frame.__init__( self, parent=None, id=wx.ID_ANY, title='WinSpec Time Step', size=wx.Size(330, 300) )
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
        
        box = wx.BoxSizer( wx.VERTICAL )
        
        self.DataPath = ""   # we don't yet know where the data is stored
        self.SPEFiles = None # a list of SPE files to plot
        
        """ Set the time.
        """
        boxSetTime = wx.BoxSizer( wx.HORIZONTAL )
        boxSetTime.Add( wx.StaticText( self, wx.ID_ANY, "Time between scans (sec.):" ), flag=wx.ALL|wx.CENTER, border=3 )
        stepList = ['10', '20', '30', '60', '120']
        defaulttimestep = stepList[0]
        self.timestepsize = defaulttimestep
        self.combo_stepsize = wx.ComboBox( self, wx.ID_ANY, value=defaulttimestep, size=(50,20),
                                           choices=stepList )
        self.combo_stepsize.SetToolTip(wx.ToolTip("Select step time in seconds from dropdown-list"))
        boxSetTime.Add( self.combo_stepsize, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.combo_stepsize.Bind( wx.EVT_TEXT, self.On_combo_stepsize_Changed )
        box.Add( boxSetTime,  proportion = 1, flag=wx.CENTER, border=10 )
        
        """ Set the filename base.
        """
        boxSetFname = wx.BoxSizer( wx.HORIZONTAL )
        boxSetFname.Add( wx.StaticText( self, wx.ID_ANY, "Filename base:" ), flag=wx.ALL|wx.CENTER, border=3 )
        defaultFnameBase = "timeseries"
        self.FnameBase = defaultFnameBase
        self.text_fname = wx.TextCtrl( self, wx.ID_ANY, defaultFnameBase, style=TE_PROCESS_ENTER )
        boxSetFname.Add( self.text_fname, proportion=0.1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.text_fname.Bind( wx.EVT_TEXT_ENTER, self.On_SetFname_Changed )
        self.text_fname.Bind( wx.EVT_TEXT, self.On_SetFname_Changed )
        box.Add( boxSetFname,  proportion = 1, flag=wx.CENTER, border=10 )
        
        """ See example filename.
        """
        self.text_exampleFname = wx.StaticText( self, wx.ID_ANY, "(e.g. " + self.FnameBase + "_XXXs.SPE)" )
        box.Add( self.text_exampleFname,  proportion = 1, flag=wx.LEFT|wx.CENTER, border=10 )
        
        """ Disclaimer on directory
        """
        box.Add( wx.StaticText( self, wx.ID_ANY, 
                                "Files will get saved in the current WinSpec directory."),
                                proportion = 1, flag=wx.LEFT|wx.CENTER, border=10 )
        
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
        
        
    def On_combo_stepsize_Changed( self, event ):
        self.timestepsize = float( self.combo_stepsize.GetValue() )
        #print 'stepsize changed:', self.timestepsize
    
    def On_SetFname_Changed( self, event ):
        self.FnameBase = self.text_fname.GetValue()
        self.text_exampleFname.SetLabel( "(e.g. " + self.FnameBase + "_XXXs.SPE)" )
        #print 'filename base:', self.FnameBase
    
    def On_button_Start_Clicked( self, event ):
        """Start Computation."""
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            self.status.SetLabel('Starting scan.')
            self.worker = WorkerThread(self)
            self.worker.setDaemon( True ) # kill this thread if we close the main app
            self.worker.start()

            self.fig = pylab.figure()
            self.current_fignum = pylab.get_fignums()[-1]
            self.axes = self.fig.add_subplot(111)
            self.fig.show()
            
    def On_button_Stop_Clicked( self, event ):
        """Stop Computation."""
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
        self.status.SetLabel( 'Done with acquisition #%s' % (event.data+1) )
        if len( pylab.get_fignums() ) > 0 and pylab.get_fignums()[-1] == self.current_fignum:
            if self.plotcolormap():
                self.fig.canvas.draw()
#            self.axes.plot( event.data, '-ob' )
#            self.fig.canvas.draw()

    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.status.SetLabel('Scan aborted.')
        elif event.data is True:
            # Process results here
            self.status.SetLabel('Scan is done.')
        # In either event, the worker is done
        self.worker = None

    def SetFname(self):
        self.Fname = self.FnameBase + "_" + str(self.time_of_scan) + "s"
        
    def plotcolormap(self):
        files = glob.glob( self.DataPath + "\\" + self.FnameBase + '_*.SPE' ) # get a list of all non-glued txt files
        
        # assume filename is of the format: timeseriesvacuum_2640.SPE
        # where 2640 is the time in seconds since the start of the series of scans
        try:
            files.sort( key=lambda x: int(os.path.split(x)[1].split('.SPE')[0].split('_')[1]) ) # sort by acquisition start time
        except ValueError:
            # there was a file in there with the same filename base but that wasn't part of the series
            # (e.g. "timeseriesvacuum_after blocking laser 10mn.SPE") 
            for fname in files:
                if not os.path.split(fname)[1].split('.SPE')[0].split('_')[1].isdigit():
                    files.remove( fname )
            files.sort( key=lambda x: int(os.path.split(x)[1].split('.SPE')[0].split('_')[1]) ) # sort by acquisition start time
            
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
                self.time.append( float( os.path.split(fname)[1].split('.SPE')[0].split('_')[-1] ) )
                
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


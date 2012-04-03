#!/usr/bin/python
""" 
   Program to control APT piezos and motors using a nicer interface than
   what was provided by APT (especially in the case of the piezos).
   
   Copyright 2010 Kasey Russell ( email: krussell _at_ post.harvard.edu )
   Distributed under the GNU General Public License
"""
import wx
from wx.lib.pubsub import Publisher

import matplotlib
if matplotlib.get_backend() != 'WXAgg':
    # this is actually just to check if it's loaded. if it already was loaded
    # and set to a different backend, then we couldn't change it anyway.
    matplotlib.use('WXAgg')

import pylab

from APTSystemControl import APTSystem
from APTPiezoControl import APTPiezo
from APTMotorControl import APTMotor

import time

import PositionLogger
import MainWindowFrame_ThreePiezos as pyPiezo
import ImageNavigation

from Wobble import wobble

# make some menu item ID's:
ID_File_Exit = wx.NewId()
ID_Window_Piezo = wx.NewId()
ID_Window_PositionLog = wx.NewId()
ID_Window_ImageNavigation = wx.NewId()
ID_Window_ManageMarkers = wx.NewId()
ID_Window_Raster = wx.NewId()
ID_Window_WinSpec = wx.NewId()
ID_Window_Wobble = wx.NewId()
ID_Joystick_Reinitialize = wx.NewId()
ID_PositionLog_Erase = wx.NewId()
ID_MarkerLog_Erase = wx.NewId()

class MainApp( wx.App ): 
    def __init__( self, redirect=False, filename=None ):
        wx.App.__init__( self, redirect, filename )
        
        self.x_log = []
        self.y_log = []
        self.markers = []
        self.initialize_dict_positioners()
        
        """ The parent frame aptcontrols holds the controls provided by APT/ThorLabs
        """
        self.frame_aptcontrols = wx.Frame( None, wx.ID_ANY, title='pyPL -- APT Controls', size=wx.Size(1400,220) )
        self.panel_aptcontrols = wx.Panel( self.frame_aptcontrols, wx.ID_ANY )
        self.frame_aptcontrols.Bind( wx.EVT_CLOSE, self.on_close_frame_aptcontrols )

        """ initframe will popup temporarily during initialization of motors, but it may not
            display its innards because we don't run MainLoop until after the initialization. see
            http://www.keyongtech.com/4889688-wxpython-before-mainloop
        """
        self.initframe = wx.Frame( self.frame_aptcontrols, wx.ID_ANY, title='pyPosition is initializing...', size=wx.Size(550, 70) )
        self.initpanel = wx.Panel( self.initframe, wx.ID_ANY )
        self.hsizer = wx.BoxSizer( wx.HORIZONTAL )
        self.inittext = wx.StaticText( self.initpanel, 
                                  label='Initializing piezos & motors, takes a few seconds... MAKE SURE ALL ARE HOMED/ZEROED!')
        self.hsizer.Add( self.inittext, flag=wx.ALL|wx.CENTER, border=3 )
        self.button_HideInitWindow = wx.Button( self.initpanel, wx.ID_ANY, 'Dismiss' )
        self.hsizer.Add( self.button_HideInitWindow, flag=wx.ALL|wx.CENTER, border=3 )
        self.button_HideInitWindow.Bind( wx.EVT_BUTTON, self.on_button_clicked_hide_init_window )
        self.initpanel.SetSizer( self.hsizer )
        self.initframe.Center()
        #self.initframe.Show()
        
        # create pubsub receivers to monitor events from daemon threads
        Publisher().subscribe( self.on_moved_joystick, "joystick-moved" )
        Publisher().subscribe( self.on_moved_motor, "motor-moved" )


    def add_menu_bar(self):
        """ File menu
        """
        file_menu = wx.Menu()
        file_menu.Append( ID_File_Exit, "E&xit", "Terminate the program" )
        wx.EVT_MENU( self, ID_File_Exit, self.on_menu_file_exit )

        menuBar = wx.MenuBar()
        menuBar.Append( file_menu, "&File" )

        """ Window menu
        """
        window_menu = wx.Menu()
        if self.numpiezo > 0:
            window_menu.Append( ID_Window_Piezo, "py&Piezos", "Custom piezo controls" )
            wx.EVT_MENU( self, ID_Window_Piezo, self.on_menu_window_pypiezo )
    
        if self.nummotor > 0:
            window_menu.Append( ID_Window_PositionLog, "Position Log", "A graphical log of motor positions" )
            wx.EVT_MENU( self, ID_Window_PositionLog, self.on_menu_window_position_log )
    
            window_menu.Append( ID_Window_ImageNavigation, "Image Navigation", "Move relative to a picture of the sample" )
            wx.EVT_MENU( self, ID_Window_ImageNavigation, self.on_menu_window_image_navigation )
    
        window_menu.Append( ID_Window_Raster, "&Raster", "Raster scan using piezos" )
        wx.EVT_MENU( self, ID_Window_Raster, self.on_menu_window_raster )
        
        window_menu.Append( ID_Window_WinSpec, "Win&Spec Time Step", "Acquire spectra every ## seconds" )
        wx.EVT_MENU( self, ID_Window_WinSpec, self.on_menu_window_winspec )
        
        window_menu.Append( ID_Window_Wobble, "&Wobbler", "Adjust wobbler settings" )
        wx.EVT_MENU( self, ID_Window_Wobble, self.on_menu_window_wobble )
        
        menuBar.Append( window_menu, "&Window" )

        """ Misc menu
        """
        misc_menu = wx.Menu()

        misc_menu.Append( ID_Joystick_Reinitialize, "Reset Joystick", "Re-initialize joystick(s)")
        wx.EVT_MENU( self, ID_Joystick_Reinitialize, self.on_menu_misc_reinitialize_joystick )

        menuBar.Append( misc_menu, "&Misc" )
        
        self.frame_aptcontrols.SetMenuBar( menuBar )


    def initialize_dict_positioners(self):
        """ they're all None by default and
            will only acquire a value if the
            appropriate positioner is detected.
        """
        self.positioners = dict()
        self.positioners['piezoX'] = None
        self.positioners['piezoY'] = None
        self.positioners['piezoZ'] = None
        self.positioners['motorX'] = None
        self.positioners['motorY'] = None
        self.positioners['motorZ'] = None


    def make_pypiezoframe(self):
        if self.numpiezo > 0:
            self.pypiezoframe = wx.Frame( None, id=wx.ID_ANY, title='pyPiezos', size=wx.Size(350, 320) )
            pyPiezo.MainPanel( self.pypiezoframe, positioners=self.positioners )
            self.pypiezoframe.Centre()
            self.pypiezoframe.Show(True)
        

    def on_button_clicked_hide_init_window( self, event ):
        self.initframe.Hide()
        

    def on_close_frame_aptcontrols( self, event ):
        try:
            self.position_monitor_thread.abort()
        except:
            pass
        
        try:
            self.pypiezoframe.Close()
        except:
            pass

        try:
            self.rasterframe.Close()
        except:
            pass

        try:
            self.position_log.Close()
        except:
            pass

        try:
            self.image_navigation.Close()
        except:
            pass

        for positioner in self.positioners:
            if self.positioners[positioner] is not None:
                try:
                    self.positioners[positioner]['control'].ctrl.StopCtrl()
                except:
                    pass
        
        try:
            self.apt_system.ctrl.StopCtrl()
        except:
            pass

        print "done."
        self.frame_aptcontrols.Destroy()
        
       
    def on_menu_file_exit( self, evt ):
        """
        This is executed when the user clicks the 'Exit' option
        under the 'File' menu.  We ask the user if they *really*
        want to exit, then close everything down if they do.
        """
        dlg = wx.MessageDialog( self.frame_aptcontrols, 'Exit Program?', 
            self.frame_aptcontrols.GetTitle()+" --> Exit", wx.YES_NO | wx.ICON_QUESTION )
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.frame_aptcontrols.Close( True )
        else:
            dlg.Destroy()

            
    def on_menu_misc_reinitialize_joystick( self, event ):
        if self.joystick_thread.isAlive():
            pass
        else:
            import pygame
            pygame.quit()
            self.joystick_thread = JoystickThread( self )
            

    def on_menu_window_image_navigation( self, event ):
        try:
            if not self.image_navigation.Show( True ): 
                self.image_navigation.Raise()
        except:
            if self.nummotor > 1:
                self.image_navigation = ImageNavigation.MainFrame( parent=self )
        
        
    def on_menu_window_position_log( self, event ):
        try:
            if not self.position_log.Show( True ): 
                self.position_log.Raise()
        except:
            if self.nummotor > 1:
                self.position_log = PositionLogger.MainFrame( parent=self )
                

    def on_menu_window_pypiezo( self, event ):
        try:
            if not self.pypiezoframe.Show( True ): 
                self.pypiezoframe.Raise()
        except:
            self.make_pypiezoframe()


    def on_menu_window_raster( self, event ):
        try:
            if not self.rasterframe.Show( True ): 
                self.rasterframe.Raise()
        except:
            if self.numpiezo > 0:
                import pyRaster
                self.rasterframe = pyRaster.Raster( self )
            

    def on_menu_window_winspec( self, event ):
        try:
            if not self.WinspecTimeStepFrame.Show( True ):
                self.WinspecTimeStepFrame.Raise()
        except:
            import WinspecTimeStep
            self.WinspecTimeStepFrame = WinspecTimeStep.MakeMainWindow()
    

    def on_menu_window_wobble( self, event ):
        try:
            if not self.wobbleAdjustmentWindow.Show( True ): 
                self.wobbleAdjustmentWindow.Raise()
        except:
            try:
                app.wobbler
                self.wobbleAdjustmentWindow = app.wobbler.wobbleParametersAdjustmentWindow( self.frame_aptcontrols )
            except NameError:
                print "no wobbler"


    def on_moved_joystick( self, msg ):
        """
        receives data from the thread controlling the joystick and updates position log accordingly
        """
        if False:
            # position is now monitored continuously with a separate thread.
        #if msg.data is 'motors':
            if self.nummotor > 0:
                if self.positioners['motorX'] is not None:
                    self.x_log.append( self.positioners['motorX']['control'].GetPosition() )

                if self.positioners['motorY'] is not None:
                    self.y_log.append( self.positioners['motorY']['control'].GetPosition() )
                
                try:
                    if self.position_log:
                        self.position_log.update_plot()
                except ( NameError, AttributeError ):
                    """ haven't yet made a figure"""
                    pass
    

    def on_moved_motor( self, msg ):
        """ receives info from the thread monitoring the motor positions, then updates position log
        """
        try:
            if self.position_log:
                self.position_log.update_plot()
        except ( NameError, AttributeError ):
            """ haven't yet made a figure"""
            pass

        
        
import threading
class JoystickThread( threading.Thread ):
    """ We spawn a separate thread for the joystick because pygame (the module we use
        to monitor the joystick) has its own event loop.
    """ 
    def __init__( self, app, positioners ):
        threading.Thread.__init__(self)
        self.app = app
        self.positioners = positioners
        self.setDaemon( True )
        self.start()
        
    def run( self ):
        import JoystickControl
        JoystickControl.StartControl( self.app, self.positioners )
        

class MotorPositionMonitorThread( threading.Thread ):
    """ I need to monitor the position with a separate thread so that we just check
        every x milliseconds. That way it will track when the user moves via the
        apt controls.
    """
    def __init__( self, app, positioners ):
        threading.Thread.__init__(self)
        self.app = app
        self.positioners = positioners
        self.x_log = app.x_log
        self.y_log = app.y_log
        self._want_abort = False
        self.setDaemon( True )
        self.start()
        
    def run(self):
        movement_threshold = 0.001 # threshold for updating (mm)
        time_interval = 0.3 # check this often (seconds)
        
        if self._want_abort:
            return

        if len( self.x_log ) == 0:
            self.x_log.append( self.positioners['motorX']['control'].GetPosition() )
            self.y_log.append( self.positioners['motorY']['control'].GetPosition() )

        prev_position = pylab.array([ self.x_log[-1], self.y_log[-1] ])

        while True:
            if self._want_abort:
                return

            current_position = pylab.array([self.positioners['motorX']['control'].GetPosition(),
                                            self.positioners['motorY']['control'].GetPosition() ])
            if any( abs(current_position-prev_position) > movement_threshold ):
                self.x_log.append( current_position[0] )
                self.y_log.append( current_position[1] )
                
                Publisher().sendMessage("motor-moved", 'True')

            prev_position = current_position
            time.sleep( time_interval )

    def abort(self):
        self._want_abort = True
            

if __name__== '__main__': 
    app = MainApp()

    """ Add motor and piezo controls to the panel_aptcontrols
    """
    
    """ 
    I included the 'direction' flag in the positioners dict in case the stage axis was inverted w.r.t. the camera:
    that way we could flip the direction of the slider so that, e.g., dragging the slider
    to the right made the sample move to the right on the camera.
    
    The serial numbers here are actually the serial numbers of the controller cards, 
    not the motors/piezos themselves.
    """
    box_allcontrols = wx.BoxSizer( wx.HORIZONTAL )

    box_system = wx.BoxSizer( wx.VERTICAL )
    app.apt_system = APTSystem( app.panel_aptcontrols, style=wx.SUNKEN_BORDER )
    #box_system.Add( app.apt_system )
    box_allcontrols.Add( app.apt_system, proportion=0 )
    
    """ Initialize piezos:
    """
    numpiezo = app.apt_system.GetNumPiezoControllerCards()
    app.numpiezo = numpiezo
    print "num piezo controller cards detected:", numpiezo

    if numpiezo > 0:
        box_piezos = wx.BoxSizer( wx.VERTICAL )
        serialnums = app.apt_system.GetPiezoSerialNumbers()
        if numpiezo == 2:
            detected_piezoX_serialnum, detected_piezoY_serialnum = serialnums
        elif numpiezo == 3:
            detected_piezoX_serialnum, detected_piezoY_serialnum, detected_piezoZ_serialnum = serialnums
        
        hard_coded_piezoX_SerialNum = 91823861
        if detected_piezoX_serialnum != hard_coded_piezoX_SerialNum:
            print "PiezoX is not familiar (s/n: %d); direction/polarity may be off. See source code." % detected_piezoX_serialnum
            
        piezoX = APTPiezo( app.panel_aptcontrols, HWSerialNum=detected_piezoX_serialnum, style=wx.SUNKEN_BORDER )
        piezoX.SetToDisplayPosition()
        piezoX.SetToClosedLoopMode()
        #print "piezoX position:", piezoX.GetPosition() # FIX THIS!!! Why doesn't this method work?
        #box_piezos.Add( piezoX, proportion=1, flag=wx.EXPAND )
        box_allcontrols.Add( piezoX, proportion=1, flag=wx.EXPAND )
        app.positioners['piezoX'] = dict( control=piezoX, direction=-1 )
        
        hard_coded_piezoY_SerialNum = 91823862
        if detected_piezoY_serialnum != hard_coded_piezoY_SerialNum:
            print "PiezoY is not familiar (s/n: %d); direction/polarity may be off. See source code." % detected_piezoY_serialnum
        
        piezoY = APTPiezo( app.panel_aptcontrols, HWSerialNum=detected_piezoY_serialnum, style=wx.SUNKEN_BORDER )
        piezoY.SetToDisplayPosition()
        piezoY.SetToClosedLoopMode()
        #box_piezos.Add( piezoY, proportion=1, flag=wx.EXPAND )
        box_allcontrols.Add( piezoY, proportion=1, flag=wx.EXPAND )
        app.positioners['piezoY'] = dict( control=piezoY, direction=1 )
        
    if numpiezo == 3:
        hard_coded_piezoZ_SerialNum = 91823863
        if detected_piezoZ_serialnum != hard_coded_piezoZ_SerialNum:
            print "PiezoZ is not familiar (s/n: %d); direction/polarity may be off. See source code." % detected_piezoZ_serialnum
    
        piezoZ = APTPiezo( app.panel_aptcontrols, HWSerialNum=detected_piezoZ_serialnum, style=wx.SUNKEN_BORDER )
        piezoZ.SetToDisplayPosition()
        piezoZ.SetToClosedLoopMode()
        #box_piezos.Add( piezoZ, proportion=1, flag=wx.EXPAND )
        box_allcontrols.Add( piezoZ, proportion=1, flag=wx.EXPAND )
        app.positioners['piezoZ'] = dict( control=piezoZ, direction=1 )





    """ Initialize motors:
    """
    nummotor = app.apt_system.GetNumMotorControllerCards()
    app.nummotor = nummotor
    print "num motor controller cards detected:", nummotor

    if nummotor > 0:
        box_motors = wx.BoxSizer( wx.VERTICAL )

        motorserialnums = app.apt_system.GetMotorSerialNumbers()
        
        if nummotor == 1:
            detected_motorX_serialnum = motorserialnums
        elif nummotor == 2:
            detected_motorX_serialnum, detected_motorY_serialnum = motorserialnums
        elif nummotor == 3:
            detected_motorX_serialnum, detected_motorY_serialnum, detected_motorZ_serialnum = motorserialnums

        hard_coded_motorX_SerialNum = 90823946
        if detected_motorX_serialnum != hard_coded_motorX_SerialNum:
            print "MotorX is not familiar (s/n: %d); direction/polarity may be off. See source code." % detected_motorX_serialnum
        motorX = APTMotor( app.panel_aptcontrols, HWSerialNum=detected_motorX_serialnum, style=wx.SUNKEN_BORDER )
        motorX.SetStageAxisInfo( minpos=0.0, maxpos=50.0 )
        motorX.SetHomeParams()
        motorX.SetBLashDist( backlash=0.001 )
        motorX.SetVelParams()
        #box_motors.Add( motorX, proportion=1, flag=wx.EXPAND )
        box_allcontrols.Add( motorX, proportion=1, flag=wx.EXPAND )
        app.positioners['motorX'] = dict( control=motorX, direction=1 )
    
        if nummotor > 1:
            hard_coded_motorY_SerialNum = 90823947
            if detected_motorY_serialnum != hard_coded_motorY_SerialNum:
                print "MotorY is not familiar (s/n: %d); direction/polarity may be off. See source code." % detected_motorY_serialnum
            motorY = APTMotor( app.panel_aptcontrols, HWSerialNum=detected_motorY_serialnum, style=wx.SUNKEN_BORDER )
            motorY.SetStageAxisInfo( minpos=0.0, maxpos=49.0 )
            motorY.SetHomeParams()
            motorY.SetBLashDist( backlash=0.001 )
            motorY.SetVelParams()
            #box_motors.Add( motorY, proportion=1, flag=wx.EXPAND )
            box_allcontrols.Add( motorY, proportion=1, flag=wx.EXPAND )
            app.positioners['motorY'] = dict( control=motorY, direction=-1 )

        if nummotor == 3:
            hard_coded_motorZ_SerialNum = 90823948
            if detected_motorZ_serialnum != hard_coded_motorZ_SerialNum:
                print "MotorZ is not familiar (s/n: %d); direction/polarity may be off. See source code." % detected_motorZ_serialnum
            motorZ = APTMotor( app.panel_aptcontrols, HWSerialNum=detected_motorZ_serialnum, style=wx.SUNKEN_BORDER )
            motorZ.SetStageAxisInfo( minpos=0.0, maxpos=12.0 ) # I haven't actually adjusted this one yet; not used.
            motorZ.SetHomeParams()
            motorZ.SetBLashDist( backlash=0.001 )
            motorZ.SetVelParams()
            #box_motors.Add( motorZ, proportion=1, flag=wx.EXPAND )
            box_allcontrols.Add( motorZ, proportion=1, flag=wx.EXPAND )
            app.positioners['motorZ'] = dict( control=motorZ, direction=1 )

    
    if nummotor == 0 and numpiezo == 0:
        print " you have nothing connected... quitting. "
        quit()

    #if numpiezo > 0:
    #    box_allcontrols.Add( box_piezos )
    #if nummotor > 0:
    #    box_allcontrols.Add( box_motors )

    app.panel_aptcontrols.SetSizer( box_allcontrols )

    if numpiezo > 0:
        app.make_pypiezoframe()

    app.numpiezo = numpiezo
    app.nummotor = nummotor
    app.add_menu_bar()
    app.frame_aptcontrols.Show()

    app.wobbler = wobble( app.positioners['piezoZ'] )

    app.joystick_thread = JoystickThread( app, app.positioners )
    app.position_monitor_thread = MotorPositionMonitorThread( app, app.positioners )
    
    app.MainLoop()

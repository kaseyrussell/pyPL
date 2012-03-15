""" In an ideal world, this will be a complete working library
    for the APTPiezo
"""
import wx.lib.activex
import comtypes.client as cc
from ctypes import byref, pointer, c_long, c_float, c_bool
from wx.lib.pubsub import Publisher

##cc.GetModule( ('{9460A175-8618-4753-B337-61D9771C4C14}', 1, 0) )
##progID_system = 'MG17SYSTEM.MG17SystemCtrl.1'
##import comtypes.gen.MG17SystemLib as MGsys

cc.GetModule( ('{E2D00F25-2208-493D-87D4-7D9369EA5F06}', 1, 0) )
progID_piezo = 'MGPIEZO.MGPiezoCtrl.1'
import comtypes.gen.MG17PiezoLib as APTPiezoLib
channel1 = APTPiezoLib.CHAN1_ID
channel2 = APTPiezoLib.CHAN2_ID
display_position = APTPiezoLib.DISP_POS
control_mode_position = APTPiezoLib.POSCONTROLMODE
closed_loop_mode = APTPiezoLib.CLOSED_LOOP

class APTPiezo( wx.lib.activex.ActiveXCtrl ):
    """The Piezo class derives from wx.lib.activex.ActiveXCtrl, which
       is where all the heavy lifting with COM gets done."""
    
    def __init__( self, parent, HWSerialNum, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name='Piezo' ):
        wx.lib.activex.ActiveXCtrl.__init__(self, parent, progID_piezo,
                                            id, pos, size, style, name)
        self.ctrl.HWSerialNum = HWSerialNum
        self.ctrl.StartCtrl()
        self.ctrl.EnableHWChannel( channel1 )
        
        """ Global variables:"""
        self.StepSize = 0.05 # initial step size (microns)
        self.max_position = 20.0 # microns
        self.min_position = 0.0 # microns
        self.PositionCh1 = 0.0
        self.PositionCh2 = 0.0
        self.SetPosition( position=0.0 )
    
    def __del__(self):
        self.ctrl.StopCtrl()

    def GetPosition( self, channel=channel1 ):
        """ returns position in microns """
        position = c_float()
        self.ctrl.GetPosOutput( channel, byref(position) )
        if channel==channel1: self.PositionCh1 = position.value
        return position.value
        
#    def SetToPositionControlMode( self, channel=channel1 ):
#        return self.ctrl.SetHWMode( channel, control_mode_position )
        
    def SetToClosedLoopMode( self, channel=channel1 ):
        return self.ctrl.SetControlMode( channel, closed_loop_mode )
        
    def SetPosition( self, channel=channel1, position=0.0 ):
        """sets position in microns, only set up for channel1 at this point."""
        if ( channel==channel1 and
             position < self.max_position and
             position > self.min_position ): 
            self.PositionCh1 = position
            return self.ctrl.SetPosOutput( channel, position )

    def SetPositionSmooth( self, channel=channel1, position=0.0, step=0.25 ):
        """Sets position in microns, only set up for channel1 at this point.
           Moves to final position in steps. Just runs SetPosition over a while loop.
        """
        if ( channel == channel2 or
            position > self.max_position or
            position < self.min_position ):
            return
        
        if position > self.PositionCh1:
            direction = 1
        else:
            direction = -1
        
        while abs(self.PositionCh1 - position) > step:
            self.SetPosition( channel, position=self.PositionCh1+step*direction )
            
        return self.SetPosition( channel, position=position )

    def SetStepSize( self, stepsize ):
        """ step size is in microns """
        self.StepSize = stepsize
    
    def SetToDisplayPosition( self, channel=channel1 ):
        return self.ctrl.SetVoltPosDispMode( channel, display_position )
    
    def StepUp( self, channel=channel1, direction=1.0, stepsize='default' ):
        """ I didn't call this Jog because 
            this is a hack that sets the position absolutely using a global step variable. """
        if stepsize == 'default': stepsize = self.StepSize
        if channel==channel1: self.PositionCh1 = self.GetPosition(channel)+stepsize*direction
        self.SetPosition( channel, self.PositionCh1 )
        
    def StepDown( self, channel=channel1, direction=1.0, stepsize='default' ):
        """ I didn't call this Jog because 
            this is a hack that sets the position absolutely using a global step variable. """
        if stepsize == 'default': stepsize = self.StepSize
        if channel==channel1: self.PositionCh1 = self.GetPosition(channel)-stepsize*direction
        self.SetPosition( channel, self.PositionCh1 )

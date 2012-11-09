""" In an ideal world, this will be a complete working library
    for the APTMotor
"""
import wx.lib.activex
import comtypes.client as cc
from ctypes import byref, pointer, c_long, c_float, c_bool

##cc.GetModule( ('{9460A175-8618-4753-B337-61D9771C4C14}', 1, 0) )
##progID_system = 'MG17SYSTEM.MG17SystemCtrl.1'
##import comtypes.gen.MG17SystemLib as MGsys

cc.GetModule( ('{2A833923-9AA7-4C45-90AC-DA4F19DC24D1}', 1, 0) )
progID_motor = 'MGMOTOR.MGMotorCtrl.1'
import comtypes.gen.MG17MotorLib as APTMotorLib
channel1 = APTMotorLib.CHAN1_ID
channel2 = APTMotorLib.CHAN2_ID
break_type_switch = APTMotorLib.HWLIMSW_BREAKS
units_mm = APTMotorLib.UNITS_MM
home_rev = APTMotorLib.HOME_REV
homelimsw_rev = APTMotorLib.HOMELIMSW_REV_HW
motor_moving_bits =  -2147478512
motor_stopped_not_homed_bits = -2147479552
motor_stopped_and_homed_bits = -2147478528

class APTMotor( wx.lib.activex.ActiveXCtrl ):
    """The Motor class derives from wx.lib.activex.ActiveXCtrl, which
       is where all the heavy lifting with COM gets done."""
    
    def __init__( self, parent, HWSerialNum, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name='Stepper Motor' ):
        wx.lib.activex.ActiveXCtrl.__init__(self, parent, progID_motor,
                                            id, pos, size, style, name)
        self.ctrl.HWSerialNum = HWSerialNum
        self.ctrl.StartCtrl()
        self.ctrl.EnableHWChannel( channel1 )
        
        """ Global variables:"""
        self.StepSize = 0.05 # initial step size (mm)
        self.PositionCh1 = 0.0
        self.PositionCh2 = 0.0
    
    def __del__(self):
        self.ctrl.StopCtrl()

    def MotorIsNotMoving( self, channel=channel1 ):
        """
        checks if the status bits of the motor indicate that the motor is stopped
        """
        return self.GetStatusBits_Bits( channel ) in [ motor_stopped_not_homed_bits, motor_stopped_and_homed_bits]
    
    def GetJogStepSize( self, channel=channel1 ):
        stepsize = c_float()
        self.ctrl.GetJogStepSize( channel, byref( stepsize ) )
        return stepsize.value
    
    def GetPosition( self, channel=channel1 ):
        position = c_float()
        self.ctrl.GetPosition(channel, byref(position))
        if channel==channel1: self.PositionCh1 = position.value
        return position.value
    
    def GetStageAxisInfo( self, channel=channel1 ):
        """Returns a tuple of:
            min position, max position, units, pitch, and direction"""
        min_position = c_float()
        max_position = c_float()
        units = c_long()
        pitch = c_float()
        direction = c_long()
        self.ctrl.GetStageAxisInfo(channel, byref(min_position),
                                          byref(max_position), byref(units),
                                          byref(pitch), byref(direction))
        return min_position.value, max_position.value, units.value, pitch.value, direction.value

    def GetStageAxisInfo_MaxPos( self, channel=channel1 ):
        """Get the maximum position of the stage that is accessible using
            the MoveAbsoluteEx or MoveRelativeEx commands, although you
            may be able to exceed it by Jogging. I think this is a
            user-settable quantity. For the small stepper we have,
            the max travel is like 18mm. (Or should be ~25mm?) """
        return self.ctrl.GetStageAxisInfo_MaxPos( channel )

    def GetStageAxisInfo_MinPos( self, channel=channel1 ):
        """Get the minimum position of the stage that is accessible using
            the MoveAbsoluteEx or MoveRelativeEx commands, although you
            may be able to exceed it by Jogging. I think this is a
            user-settable quantity. For the small stepper we have, if
            it's been "homed" then it sets 0 to be the minimum position."""
        return self.ctrl.GetStageAxisInfo_MinPos( channel )
    
    def GetStatusBits_Bits( self, channel=channel1 ):
        """ Returns the status bits. """
        return self.ctrl.GetStatusBits_Bits( channel )
        
    def MoveAbsoluteEx( self, position_ch1=0.0, position_ch2=0.0,
                       channel=channel1, wait=True ):
        """
        Move motor to a specified position.

        *position_ch1*
            target position (in mm) of channel 1 (the default channel)
        
        *position_ch2*
            target position (in mm) of channel 2. I'm not sure what it
            means to have different channels...
        
        *channel*
            the channel you want to move. I always use default (channel1).
        
        *wait*
            Wait for the motor to finish moving? Default is True.

        """
        if ( channel==channel1 and 
                position_ch1 > self.GetStageAxisInfo_MinPos(channel) and
                position_ch1 < self.GetStageAxisInfo_MaxPos(channel) ): 
            self.PositionCh1 = position_ch1
            return self.ctrl.MoveAbsoluteEx( channel, position_ch1, position_ch2, wait )


    def MoveRelativeEx( self, relative_dist_ch1=0.0, relative_dist_ch2=0.0,
                       channel=channel1, wait=True ):
        """ I've never tried this function..."""
        return self.ctrl.MoveRelativeEx( channel, relative_dist_ch1, relative_dist_ch2, wait )
    

    def SetBLashDist( self, channel=channel1, backlash=0.01 ):
        """
        Sets the backlash distance in mm.

        *channel*
           channel1 by default

        *backlash*
           distance in mm, 0.01 by default
         """
        return self.ctrl.SetBLashDist( channel, backlash )
    

    def SetHomeParams( self, channel=channel1, direction=home_rev, switch=homelimsw_rev,
                       velocity=1.0, zero_offset=0.1 ):
        """
        Set the "home params". I forget what these actually mean.

        *channel*
            channel1 by default

        *direction*
            home_rev by default

        *switch*
            homelimsw_rev by default

        *velocity*
            1.0 by default

        *zero_offset*
            0.1 by default.

        """
        return self.ctrl.SetHomeParams( channel, direction, switch, velocity, zero_offset )
        
    def SetStageAxisInfo( self, channel=channel1, minpos=0.0, maxpos=12.0, pitch=1.0, units=units_mm ):
        """
        Set the stage axis info.

        *channel*
            channel1 by default

        *minpos*
            0.0 (mm) by default

        *maxpos*
            12.0 (mm) by default

        *pitch*
            1.0 by default

        *units*
            units_mm by default

        """
        return self.ctrl.SetStageAxisInfo( channel, minpos, maxpos, units, pitch, 1 )
        
    def SetStepSize( self, stepsize ):
        """
        Set the step size for the StepUp and StepDown methods.

        *stepsize*
            step size in mm.
        """
        self.StepSize = stepsize
    
    def SetSWPosLimits( self, channel=channel1, minpos=0.0, maxpos=12.0, limitmode=break_type_switch ):
        """ I don't quite understand what this does."""
        return self.ctrl.SetSWPosLimits( channel, minpos, maxpos, limitmode )

    def SetVelParams( self, channel=channel1, minvelocity=0.0, maxvelocity=2.0, acceleration=4.0 ):
        """ what is minvelocity? doesn't seem to be in the panel control options..."""
        return self.ctrl.SetVelParams( channel, minvelocity, acceleration, maxvelocity)
    
    def StepUp( self, channel=channel1, wait=True, polarity=1.0, stepsize='default' ):
        """
        I didn't call this Jog because I couldn't get the SetJogStepSize method to work.
        This is a hack that sets the position absolutely using a global step variable.

        *channel*
            channel1 by default.

        *wait*
            wait for motor to finish moving? True by default.

        *polarity*
            "Up" is a relative term, but the motor position is absolute, so this
            parameter can be used to invert what you mean by "up".

        *stepsize*
            By default, use the value set by the SetStepSize method.

        """
        if stepsize == 'default': stepsize = self.StepSize
        newlocation = self.GetPosition(channel)+stepsize*polarity
        if ( channel==channel1 and 
                newlocation > self.GetStageAxisInfo_MinPos(channel) and
                newlocation < self.GetStageAxisInfo_MaxPos(channel) ): 
            self.PositionCh1 = newlocation
            self.MoveAbsoluteEx( self.PositionCh1, self.PositionCh2, channel, wait )
        
    def StepDown( self, channel=channel1, wait=True, polarity=1.0, stepsize='default' ):
        """
        I didn't call this Jog because I couldn't get the SetJogStepSize method to work.
        This is a hack that sets the position absolutely using a global step variable.

        *channel*
            channel1 by default.

        *wait*
            wait for motor to finish moving? True by default.

        *polarity*
            "Down" is a relative term, but the motor position is absolute, so this
            parameter can be used to invert what you mean by "down".

        *stepsize*
            By default, use the value set by the SetStepSize method.

        """
        if stepsize == 'default': stepsize = self.StepSize
        newlocation = self.GetPosition(channel)-stepsize*polarity
        if ( channel==channel1 and 
                newlocation > self.GetStageAxisInfo_MinPos(channel) and
                newlocation < self.GetStageAxisInfo_MaxPos(channel) ): 
            self.PositionCh1 = newlocation
            self.MoveAbsoluteEx( self.PositionCh1, self.PositionCh2, channel, wait )
        
    def StopImmediate( self, channel=channel1 ):
        """ Stops the motor from moving (although this won't overcome the strange ActiveX
        phantom-motor-moving issue where the control says it is moving but actually isn't. """
        return self.ctrl.StopImmediate( channel )

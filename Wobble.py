""" module for implementing focus wobble
"""
import wx
from wx._controls import TE_PROCESS_ENTER

class wobble:
    """ 
        This will contain all info about the current state of the wobbler (on/off)
        as well as where it should go next (iterator)
        and whether there is a valid focus-piezo attached
    """
    def __init__( self, piezo, amplitude=1.0, steps=3 ):
        self.piezo = piezo
        self.amplitude = amplitude
        
        if piezo is not None:
            self.validpiezo = True
            self.wobbleZero = self.piezo['control'].PositionCh1
        else:
            self.validpiezo = False
            self.wobbleZero = 10.0
            
        self.wobbling = False
        self.initWobbler( amplitude, steps )

    def initWobbler( self, amplitude, steps ):
        """ amplitude is relative to focus; 2*amplitude is peak-to-peak swing (in microns) """
        self.stepsize = amplitude/steps
        
    def isPossible(self):
        if self.validpiezo is True:
            return True
        else:
            return False
        
    def isWobbling(self):
        return self.wobbling
    
    def wobbleOn(self):
        self.wobbling = True
        
    def wobbleOff(self):
        self.wobbling = False
        
    def wobbleToggle(self):
        if self.wobbling is True:
            self.wobbling = False
        else:
            self.wobbling = True

    def wobbleIncrement(self):
        """
        If wobbling is on, this will get called once per iteration of the joystick monitoring loop (every ~30ms)
        """
        if self.validpiezo is True:
            if abs( self.piezo['control'].PositionCh1 - self.wobbleZero) >= self.amplitude :
                self.stepsize *= -1 # reverse direction
            self.piezo['control'].StepUp( stepsize=self.stepsize )

    def wobbleParametersAdjustmentWindow( self, parentframe ):
        """
        popup a window to adjust the amplitude and step of the wobble
        """
        if type(parentframe) is not wx._windows.Frame:
            raise TypeError("Must pass a wx.Frame instance to wobbleParametersAdjustmentWindow as its parent frame.")
        
        self.wobbleframe = wx.Frame( parentframe, id=wx.ID_ANY, title='Wobble Adjustment', size=wx.Size(350, 100) )

        self.panel = wx.Panel( self.wobbleframe )
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        
        box.Add( wx.StaticText( self.panel, wx.ID_ANY, "Amplitude (um):" ), flag=wx.LEFT|wx.CENTER, border=3 )
 
        self.text_amplitude = wx.TextCtrl( self.panel, wx.ID_ANY, str(self.amplitude), style=TE_PROCESS_ENTER )
        box.Add( self.text_amplitude, flag=wx.LEFT|wx.CENTER, border=2 )
#        self.text_amplitude.Bind( wx.EVT_TEXT_ENTER, self.On_text_amplitude_Changed )
       
        self.OkButton = wx.Button( self.panel, wx.ID_ANY, "OK" )
        box.Add( self.OkButton, flag=wx.LEFT|wx.CENTER, border=2 )
        self.OkButton.Bind( wx.EVT_BUTTON, self.On_OkButton_Pressed )

        self.panel.SetSizer( box )
        self.wobbleframe.Centre()
        self.wobbleframe.Show(True)

    def On_text_amplitude_Changed( self, event ):
        self.amplitude = float(self.text_amplitude.GetValue())
        
    def On_OkButton_Pressed( self, event ):
        self.amplitude = float(self.text_amplitude.GetValue())
        self.wobbleframe.Destroy()
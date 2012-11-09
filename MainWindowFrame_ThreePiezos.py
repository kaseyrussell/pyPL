#!/usr/bin/python
""" This module creates the panel for the main window of the program.
    KJR 20 Aug 2010
"""
import wx
from wx.lib.pubsub import Publisher
from wx._controls import TE_PROCESS_ENTER

class FakeEvent:
    """make a holder for passing a string to an event handler"""
    def __init__(self, string):
        self.data = string

class MainPanel( wx.Panel ):
    """ The window with sliders for controlling the piezos. """
    def __init__( self, parent, positioners, id=wx.ID_ANY ):
        wx.Panel.__init__( self, parent, id, style=wx.WANTS_CHARS )
        self.piezoX = positioners['piezoX']
        self.piezoY = positioners['piezoY']
        self.piezoZ = positioners['piezoZ']
        
        self.PiezoMin = self.piezoX['control'].min_position * 1000 # (nm) 
        self.PiezoMax = self.piezoX['control'].max_position * 1000 # (nm) 
        self.MedRange = self.PiezoMax / 2
        self.SmRange = self.PiezoMax / 10
        self.jogsize = 50 # jog size in nm

        """ Top-level sizer, will be three row
        """
        box = wx.BoxSizer( wx.VERTICAL )

        """ Top row is button and step size selector for arrow-key jogging
        """
        boxJog = wx.BoxSizer( wx.HORIZONTAL )
        self.button_jog = wx.Button( self, wx.ID_ANY, "Jog w/ keypad" )
        self.button_jog.Bind( wx.EVT_CHAR, self.On_keyboard_jog )
        boxJog.Add( self.button_jog, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=2 )
        
        boxJog.Add( wx.StaticText( self, wx.ID_ANY, "Step size (nm):"), proportion=0, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2 )
        
        self.txtctrl_jogsize = wx.TextCtrl( self, wx.ID_ANY, "50", size=(40,20), style=TE_PROCESS_ENTER )
        self.txtctrl_jogsize.Bind( wx.EVT_TEXT_ENTER, self.On_txtctrl_jogsize_Changed ) 
        boxJog.Add( self.txtctrl_jogsize, proportion=0.1, flag=wx.ALIGN_CENTER_VERTICAL, border=2 )
        
        box.Add( boxJog,  proportion=0.2, flag=wx.ALIGN_CENTER|wx.ALL, border=5 )

        """ Y and focus are in second row, 4col: focus slider, focus selectors, Y selectors, Y slider
        """
        boxYandfocus = wx.BoxSizer( wx.HORIZONTAL ) # top-level Y box
        
        """ Focus Slider: actually in nm (b/c is easier in integer), then convert to um
        """
        boxZslider = wx.BoxSizer( wx.VERTICAL )
        if self.piezoZ['direction']==1: 
            sliderZ_style = wx.SL_VERTICAL|wx.SL_INVERSE
        elif self.piezoZ['direction']==-1:
            sliderZ_style = wx.SL_VERTICAL
        else:
            raise ValueError('Improper value for direction of piezoZ.')
        self.ZsliderMax = wx.StaticText( self, wx.ID_ANY, str(self.PiezoMax/1000.0) )
        self.Zslider = wx.Slider( self, wx.ID_ANY, self.piezoZ['control'].PositionCh1*1000, self.PiezoMin, self.PiezoMax,
                                  pos=(0, 0), size=(20, 150),
                                  style=sliderZ_style )
        self.Zslider.SetLineSize( self.PiezoMax/50.0 ) # number it moves by if you use arrow keys
        self.Zslider.Bind( wx.EVT_SLIDER, self.On_Zslider_Changed )
        self.ZsliderMin = wx.StaticText( self, wx.ID_ANY, str(self.PiezoMin/1000.0) )

        if self.piezoZ['direction']==1: 
            boxZslider.Add( self.ZsliderMax, proportion=1, flag=wx.CENTER, border=2 )
            boxZslider.Add( self.Zslider,  proportion=.1, flag=wx.CENTER, border=1 )
            boxZslider.Add( self.ZsliderMin, proportion=1, flag=wx.CENTER, border=2 )
        elif self.piezoZ['direction']==-1:
            boxZslider.Add( self.ZsliderMin, proportion=1, flag=wx.CENTER, border=2 )
            boxZslider.Add( self.Zslider,  proportion=.1, flag=wx.CENTER, border=1 )
            boxZslider.Add( self.ZsliderMax, proportion=1, flag=wx.CENTER, border=2 )

        boxYandfocus.Add( boxZslider, proportion=0.9, flag=wx.CENTER|wx.LEFT, border=2 )

        """ Focus Indicator and Range selectors:
        """
        boxZrange = wx.BoxSizer( wx.VERTICAL )

        boxZrange.Add( wx.StaticText( self, wx.ID_ANY, "Focus (um):", style=wx.ALIGN_CENTER ), flag=wx.ALL|wx.CENTER, border=2 )

        self.Zlocation = wx.TextCtrl( self, wx.ID_ANY, str(self.piezoZ['control'].PositionCh1), 
                                      size=(50,20), style=TE_PROCESS_ENTER )
        self.Zlocation.Bind( wx.EVT_TEXT_ENTER, self.On_text_Zlocation_Changed ) 
        boxZrange.Add( self.Zlocation, flag=wx.ALL|wx.CENTER, border=2 )

        boxZrange.Add( wx.StaticText( self, wx.ID_ANY, "Select range:" ), proportion=1, flag=wx.TOP|wx.CENTER, border=2 )

        self.ZrangeSmall = wx.Button( self, wx.ID_ANY, str(self.SmRange/1000)+' um')
        boxZrange.Add( self.ZrangeSmall, proportion=1, flag=wx.CENTER, border=2 )
        self.ZrangeSmall.Bind( wx.EVT_BUTTON, self.On_button_ZrangeSmall_Clicked )

        self.ZrangeMed = wx.Button( self, wx.ID_ANY, str(self.MedRange/1000)+' um')
        boxZrange.Add( self.ZrangeMed, proportion=1, flag=wx.CENTER, border=2 )
        self.ZrangeMed.Bind( wx.EVT_BUTTON, self.On_button_ZrangeMed_Clicked )

        self.ZrangeLg = wx.Button( self, wx.ID_ANY, str(self.PiezoMax/1000)+' um')
        boxZrange.Add( self.ZrangeLg, proportion=1, flag=wx.CENTER, border=2 )
        self.ZrangeLg.Bind( wx.EVT_BUTTON, self.On_button_ZrangeLg_Clicked )
        
        boxYandfocus.Add( boxZrange,  proportion = 1, flag=wx.CENTER|wx.RIGHT, border=10 )

        """ Y Indicator and Range selectors:
        """
        boxYrange = wx.BoxSizer( wx.VERTICAL )

        boxYrange.Add( wx.StaticText( self, wx.ID_ANY, "Y (um):", style=wx.ALIGN_CENTER ), flag=wx.ALL|wx.CENTER, border=2 )

        self.Ylocation = wx.TextCtrl( self, wx.ID_ANY, str(self.piezoY['control'].PositionCh1),
                                      size=(50,20), style=TE_PROCESS_ENTER )
        self.Ylocation.Bind( wx.EVT_TEXT_ENTER, self.On_text_Ylocation_Changed ) 
        boxYrange.Add( self.Ylocation, flag=wx.ALL|wx.CENTER, border=2 )

        boxYrange.Add( wx.StaticText( self, wx.ID_ANY, "Select range:" ), proportion=1, flag=wx.TOP|wx.CENTER, border=2 )

        self.YrangeSmall = wx.Button( self, wx.ID_ANY, str(self.SmRange/1000)+' um')
        boxYrange.Add( self.YrangeSmall, proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.YrangeSmall.Bind( wx.EVT_BUTTON, self.On_button_YrangeSmall_Clicked )

        self.YrangeMed = wx.Button( self, wx.ID_ANY, str(self.MedRange/1000)+' um')
        boxYrange.Add( self.YrangeMed, proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.YrangeMed.Bind( wx.EVT_BUTTON, self.On_button_YrangeMed_Clicked )

        self.YrangeLg = wx.Button( self, wx.ID_ANY, str(self.PiezoMax/1000)+' um')
        boxYrange.Add( self.YrangeLg, proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.YrangeLg.Bind( wx.EVT_BUTTON, self.On_button_YrangeLg_Clicked )
        
        boxYandfocus.Add( boxYrange,  proportion = 1, flag=wx.LEFT|wx.ALIGN_CENTER, border=10 )

        """ Y Slider: actually in nm (b/c is easier in integer), then convert to um
        """
        boxYslider = wx.BoxSizer( wx.VERTICAL )
        if self.piezoY['direction']==1: 
            sliderY_style = wx.SL_VERTICAL|wx.SL_INVERSE
        elif self.piezoY['direction']==-1:
            sliderY_style = wx.SL_VERTICAL
        else:
            raise ValueError('Improper value for direction of piezoY.')
        self.YsliderMax = wx.StaticText( self, wx.ID_ANY, str(self.PiezoMax/1000.0) )
        self.Yslider = wx.Slider( self, wx.ID_ANY, self.piezoY['control'].PositionCh1*1000, self.PiezoMin, self.PiezoMax,
                                  pos=(0, 0), size=(20, 150),
                                  style=sliderY_style )
        self.Yslider.SetLineSize( self.PiezoMax/50.0 ) # number it moves by if you use arrow keys
        self.Yslider.Bind( wx.EVT_SLIDER, self.On_Yslider_Changed )
        self.YsliderMin = wx.StaticText( self, wx.ID_ANY, str(self.PiezoMin/1000.0) )

        if self.piezoY['direction']==1: 
            boxYslider.Add( self.YsliderMax, proportion=1, flag=wx.CENTER, border=2 )
            boxYslider.Add( self.Yslider,  proportion=.1, flag=wx.CENTER, border=1 )
            boxYslider.Add( self.YsliderMin, proportion=1, flag=wx.CENTER, border=2 )
        elif self.piezoY['direction']==-1:
            boxYslider.Add( self.YsliderMin, proportion=1, flag=wx.CENTER, border=2 )
            boxYslider.Add( self.Yslider,  proportion=.1, flag=wx.CENTER, border=1 )
            boxYslider.Add( self.YsliderMax, proportion=1, flag=wx.CENTER, border=2 )

        boxYandfocus.Add( boxYslider, proportion=0.9, flag=wx.CENTER, border=2 )

        box.Add( boxYandfocus,  proportion=0.1, flag=wx.CENTER, border=2 )
        
        """ X is on bottom, 2col: indicator, range selectors above slider
        """
        boxX = wx.BoxSizer( wx.HORIZONTAL ) # top-level Y box
        
        """ Indicator:
        """
        boxXloc = wx.BoxSizer( wx.VERTICAL ) # left column

        boxXloc.Add( wx.StaticText( self, wx.ID_ANY, "X (um):", style=wx.ALIGN_CENTER ), flag=wx.ALL|wx.CENTER, border=2 )
        
        self.Xlocation = wx.TextCtrl( self, wx.ID_ANY, str(self.piezoX['control'].PositionCh1),
                                      size=(50,20), style=TE_PROCESS_ENTER )
        self.Xlocation.Bind( wx.EVT_TEXT_ENTER, self.On_text_Xlocation_Changed ) 
        
        boxXloc.Add( self.Xlocation, flag=wx.ALL|wx.CENTER, border=2 )
        boxX.Add( boxXloc, flag=wx.ALL|wx.CENTER, border=10 )
        
        """ Range selectors:
        """
        boxXallranges = wx.BoxSizer( wx.VERTICAL )
        boxXallranges.Add( wx.StaticText( self, wx.ID_ANY, "Select range:" ), proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )

        boxXrange = wx.BoxSizer( wx.HORIZONTAL )
        self.XrangeSmall = wx.Button( self, wx.ID_ANY, str(self.SmRange/1000)+' um')
        boxXrange.Add( self.XrangeSmall, proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.XrangeSmall.Bind( wx.EVT_BUTTON, self.On_button_XrangeSmall_Clicked )
        self.XrangeMed = wx.Button( self, wx.ID_ANY, str(self.MedRange/1000)+' um')
        boxXrange.Add( self.XrangeMed, proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.XrangeMed.Bind( wx.EVT_BUTTON, self.On_button_XrangeMed_Clicked )
        self.XrangeLg = wx.Button( self, wx.ID_ANY, str(self.PiezoMax/1000)+' um')
        boxXrange.Add( self.XrangeLg, proportion=1, flag=wx.LEFT|wx.CENTER, border=2 )
        self.XrangeLg.Bind( wx.EVT_BUTTON, self.On_button_XrangeLg_Clicked )

        
        boxXallranges.Add( boxXrange, proportion=1, flag=wx.CENTER, border=2 )
        
        """ Slider: actually in nm (b/c is easier in integer), then convert to um
        """
        boxXslider = wx.BoxSizer( wx.HORIZONTAL )
        if self.piezoX['direction']==1: 
            sliderX_style = wx.SL_HORIZONTAL
        elif self.piezoX['direction']==-1:
            sliderX_style = wx.SL_HORIZONTAL|wx.SL_INVERSE
        else:
            raise ValueError('Improper value for direction of piezoY.')

        self.XsliderMin = wx.StaticText( self, wx.ID_ANY, str(self.PiezoMin/1000.0) )
        #self.Xslider = wx.Slider( self, wx.ID_ANY, piezoX['control'].GetPosition()*1000,
        self.Xslider = wx.Slider( self, wx.ID_ANY, self.piezoX['control'].PositionCh1*1000,
                                  self.PiezoMin, self.PiezoMax, pos=(0, 0), size=(200, 20),
                                  style=sliderX_style )
        self.Xslider.SetLineSize( self.PiezoMax/50.0 )
        self.Xslider.Bind( wx.EVT_SLIDER, self.On_Xslider_Changed )
        self.XsliderMax = wx.StaticText( self, wx.ID_ANY, str(self.PiezoMax/1000.0) )

        if self.piezoX['direction']==1: 
            boxXslider.Add( self.XsliderMin, proportion=1, flag=wx.CENTER, border=2 )
            boxXslider.Add( self.Xslider,  proportion=.1, flag=wx.CENTER, border=1 )
            boxXslider.Add( self.XsliderMax, proportion=1, flag=wx.CENTER, border=2 )
        elif self.piezoX['direction']==-1:
            """ flip the ordering """
            boxXslider.Add( self.XsliderMax, proportion=1, flag=wx.CENTER, border=2 )
            boxXslider.Add( self.Xslider,  proportion=.1, flag=wx.CENTER, border=1 )
            boxXslider.Add( self.XsliderMin, proportion=1, flag=wx.CENTER, border=2 )

        boxXallranges.Add( boxXslider, proportion=1, flag=wx.CENTER, border=2 )
        boxX.Add( boxXallranges,  proportion=1, flag=wx.CENTER, border=2 )
        box.Add( boxX,  proportion=1, flag=wx.CENTER, border=2 )
        
        self.SetSizer( box )
        
        # create a pubsub receiver to monitor events from the thread controlling the joystick
        Publisher().subscribe( self.On_joystick_moved, "joystick-moved" )

        # create a pubsub receiver to monitor piezo movement
        Publisher().subscribe( self.On_piezos_moved, "piezos-moved" )

    def On_piezos_moved( self, msg ):
        """
        Handler for updating the GUI in response to changes in piezo position.
        """
        if msg.data == 'raster':
            self.On_button_XrangeLg_Clicked( None )
            Xloc = self.piezoX['control'].PositionCh1
            self.Xslider.SetValue( Xloc*1000 )
            self.Xlocation.SetValue( "%.3f" % Xloc )

            self.On_button_YrangeLg_Clicked( None )
            Yloc = self.piezoY['control'].PositionCh1
            self.Yslider.SetValue( Yloc*1000 )
            self.Ylocation.SetValue( "%.3f" % Yloc )

        if msg.data == 'focus':
            self.On_button_ZrangeLg_Clicked( None )
            Zloc = self.piezoZ['control'].PositionCh1
            self.Zslider.SetValue( Zloc*1000 )
            self.Zlocation.SetValue( "%.3f" % Zloc )

            

    def On_joystick_moved( self, msg ):
        """
        Receives data from the thread controlling the joystick and updates our sliders accordingly
        """
        if msg.data == 'piezos':
            self.On_button_YrangeLg_Clicked( None )
            Yloc = self.piezoY['control'].PositionCh1
            self.Yslider.SetValue( Yloc*1000 )
            self.Ylocation.SetValue( "%.3f" % Yloc )
            
            self.On_button_XrangeLg_Clicked( None )
            Xloc = self.piezoX['control'].PositionCh1
            self.Xslider.SetValue( Xloc*1000 )
            self.Xlocation.SetValue( "%.3f" % Xloc )
            
            self.On_button_ZrangeLg_Clicked( None )
            Zloc = self.piezoZ['control'].PositionCh1
            self.Zslider.SetValue( Zloc*1000 )
            self.Zlocation.SetValue( "%.3f" % Zloc )
            
    def On_keyboard_jog( self, event ):
        """
        Handler for updating the piezo position in respose to keyboard press.
        """
        event.Skip()
        code = event.GetKeyCode()
        if ((code == wx.WXK_LEFT and self.piezoX['direction']==1) or
                (code == wx.WXK_RIGHT and self.piezoX['direction']==-1)):
            newposition = self.piezoX['control'].PositionCh1*1000 - self.jogsize
            newposition = self.PiezoMin if newposition < self.PiezoMin else newposition
            self.piezoX['control'].SetPosition( position=newposition/1000 )
            self.On_piezos_moved(FakeEvent('raster'))
            
        elif ((code == wx.WXK_LEFT and self.piezoX['direction']==-1) or
                (code == wx.WXK_RIGHT and self.piezoX['direction']==1)):
            newposition = self.piezoX['control'].PositionCh1*1000 + self.jogsize
            newposition = self.PiezoMax if newposition > self.PiezoMax else newposition
            self.piezoX['control'].SetPosition( position=newposition/1000 )
            self.On_piezos_moved(FakeEvent('raster'))
            
        elif ((code == wx.WXK_UP and event.AltDown() and self.piezoZ['direction']==1) or
                (code == wx.WXK_DOWN and event.AltDown() and self.piezoZ['direction']==-1)):
            newposition = self.piezoZ['control'].PositionCh1*1000 + self.jogsize
            newposition = self.PiezoMax if newposition > self.PiezoMax else newposition
            self.piezoZ['control'].SetPosition( position=newposition/1000 )
            self.On_piezos_moved(FakeEvent('focus'))

        elif ((code == wx.WXK_UP and event.AltDown() and self.piezoZ['direction']==-1) or
                (code == wx.WXK_DOWN and event.AltDown() and self.piezoZ['direction']==1)):
            newposition = self.piezoZ['control'].PositionCh1*1000 - self.jogsize
            newposition = self.PiezoMin if newposition < self.PiezoMin else newposition
            self.piezoZ['control'].SetPosition( position=newposition/1000 )
            self.On_piezos_moved(FakeEvent('focus'))

        elif ((code == wx.WXK_UP and self.piezoY['direction']==1) or
                (code == wx.WXK_DOWN and self.piezoY['direction']==-1)):
            newposition = self.piezoY['control'].PositionCh1*1000 + self.jogsize
            newposition = self.PiezoMax if newposition > self.PiezoMax else newposition
            self.piezoY['control'].SetPosition( position=newposition/1000 )
            self.On_piezos_moved(FakeEvent('raster'))

        elif ((code == wx.WXK_UP and self.piezoY['direction']==-1) or
                (code == wx.WXK_DOWN and self.piezoY['direction']==1)):
            newposition = self.piezoY['control'].PositionCh1*1000 - self.jogsize
            newposition = self.PiezoMin if newposition < self.PiezoMin else newposition
            self.piezoY['control'].SetPosition( position=newposition/1000 )
            self.On_piezos_moved(FakeEvent('raster'))
        
            
    def On_text_Zlocation_Changed( self, event ):
        """
        Handler for updating the z-piezo position in response to text entry.
        """
        Zloc = float(self.Zlocation.GetValue())*1000
        if Zloc > self.Zslider.GetMax() or Zloc < self.Zslider.GetMin():
            # jump to full-scale
            self.Zslider.SetMin( self.PiezoMin )
            self.ZsliderMin.SetLabel( str(self.PiezoMin/1000.0) )
            self.Zslider.SetMax( self.PiezoMax )
            self.ZsliderMax.SetLabel( str(self.PiezoMax/1000.0) )
            if Zloc > self.PiezoMax:
                self.Zslider.SetValue( self.PiezoMax )
                self.piezoZ['control'].SetPosition( position=self.PiezoMax/1000 )
            elif Zloc < self.PiezoMin:
                self.Zslider.SetValue( self.PiezoMin )
                self.piezoZ['control'].SetPosition( position=self.PiezoMin/1000 )
            else:
                self.Zslider.SetValue( Zloc )
                self.piezoZ['control'].SetPosition( position=Zloc/1000.0 )
        else:
            self.Zslider.SetValue( Zloc )
            self.piezoZ['control'].SetPosition( position=Zloc/1000.0 )
    
    
    def On_txtctrl_jogsize_Changed( self, event ):
        """
        Handler for updating the keyboard step size in response to text entry.
        """
        event.Skip()
        try:
            jogsize = int(self.txtctrl_jogsize.GetValue())
            if jogsize < 0 or jogsize > 1000: jogsize = 50
            self.jogsize = jogsize
        except ValueError:
            pass
        
        
    def On_button_ZrangeSmall_Clicked( self, event ):
        """
        Handler for rescaling z-piezo slider range.
        """
        Zloc = self.Zslider.Value
        if Zloc > self.SmRange/2 and Zloc < self.PiezoMax-self.SmRange/2:
            self.Zslider.SetMin( Zloc-self.SmRange/2 )
            self.Zslider.SetMax( Zloc+self.SmRange/2 )
        elif Zloc<self.SmRange/2:
            self.Zslider.SetMin( self.PiezoMin )
            self.Zslider.SetMax( self.SmRange )
        else:
            self.Zslider.SetMin( self.PiezoMax-self.SmRange )
            self.Zslider.SetMax( self.PiezoMax )

        self.Zslider.SetLineSize( self.SmRange/50.0 )
        self.Zslider.SetValue(Zloc)
        self.ZsliderMax.SetLabel( str(self.Zslider.GetMax()/1000.0) )
        self.ZsliderMin.SetLabel( str(self.Zslider.GetMin()/1000.0) )
        #print 'Z range small'
        
    def On_button_ZrangeMed_Clicked( self, event ):
        """
        Handler for rescaling z-piezo slider range.
        """
        Zloc = self.Zslider.Value
        if Zloc > self.MedRange/2 and Zloc < self.PiezoMax-self.MedRange/2:
            self.Zslider.SetMin( Zloc-self.MedRange/2 )
            self.Zslider.SetMax( Zloc+self.MedRange/2 )
        elif Zloc<self.MedRange/2:
            self.Zslider.SetMin( self.PiezoMin )
            self.Zslider.SetMax( self.MedRange )
        else:
            self.Zslider.SetMin( self.PiezoMax-self.MedRange )
            self.Zslider.SetMax( self.PiezoMax )
        
        self.Zslider.SetLineSize( self.MedRange/50.0 )
        self.Zslider.SetValue(Zloc)
        self.ZsliderMax.SetLabel( str(self.Zslider.GetMax()/1000.0) )
        self.ZsliderMin.SetLabel( str(self.Zslider.GetMin()/1000.0) )
        #print 'Z range medium'
        
    def On_button_ZrangeLg_Clicked( self, event ):
        """
        Handler for rescaling z-piezo slider range.
        """
        Zloc = self.Zslider.Value
        self.Zslider.SetMin( self.PiezoMin )
        self.ZsliderMin.SetLabel( str(self.PiezoMin/1000.0) )
        self.Zslider.SetMax( self.PiezoMax )
        self.ZsliderMax.SetLabel( str(self.PiezoMax/1000.0) )
        self.Zslider.SetValue(Zloc)
        self.Zslider.SetLineSize( self.PiezoMax/50.0 )
        #print 'Y range large'
        
    def On_Zslider_Changed( self, event ):
        """
        Handler for responding to slider input.
        """
        Zloc = self.Zslider.Value/1000.0
        self.Zlocation.SetValue( str(Zloc) )
        self.piezoZ['control'].SetPosition( position=Zloc )
        
    def On_text_Ylocation_Changed( self, event ):
        """
        Handler for updating the y-piezo position in response to text entry.
        """
        Yloc = float(self.Ylocation.GetValue())*1000
        if Yloc > self.Yslider.GetMax() or Yloc < self.Yslider.GetMin():
            # jump to full-scale
            self.Yslider.SetMin( self.PiezoMin )
            self.YsliderMin.SetLabel( str(self.PiezoMin/1000.0) )
            self.Yslider.SetMax( self.PiezoMax )
            self.YsliderMax.SetLabel( str(self.PiezoMax/1000.0) )
            if Yloc > self.PiezoMax:
                self.Yslider.SetValue( self.PiezoMax )
                self.piezoY['control'].SetPositionSmooth( position=self.PiezoMax/1000, step=0.25 )
            elif Yloc < self.PiezoMin:
                self.Yslider.SetValue( self.PiezoMin )
                self.piezoY['control'].SetPositionSmooth( position=self.PiezoMin/1000, step=0.25 )
            else:
                self.Yslider.SetValue( Yloc )
                self.piezoY['control'].SetPositionSmooth( position=Yloc/1000.0, step=0.25 )
        else:
            self.Yslider.SetValue( Yloc )
            self.piezoY['control'].SetPositionSmooth( position=Yloc/1000.0, step=0.25 )
    
    def On_button_YrangeSmall_Clicked( self, event ):
        """
        Handler for rescaling y-piezo slider range.
        """
        Yloc = self.Yslider.Value
        if Yloc > self.SmRange/2 and Yloc < self.PiezoMax-self.SmRange/2:
            self.Yslider.SetMin( Yloc-self.SmRange/2 )
            self.Yslider.SetMax( Yloc+self.SmRange/2 )
        elif Yloc<self.SmRange/2:
            self.Yslider.SetMin( self.PiezoMin )
            self.Yslider.SetMax( self.SmRange )
        else:
            self.Yslider.SetMin( self.PiezoMax-self.SmRange )
            self.Yslider.SetMax( self.PiezoMax )

        self.Yslider.SetLineSize( self.SmRange/50.0 )
        self.Yslider.SetValue(Yloc)
        self.YsliderMax.SetLabel( str(self.Yslider.GetMax()/1000.0) )
        self.YsliderMin.SetLabel( str(self.Yslider.GetMin()/1000.0) )
        #print 'Y range small'
        
    def On_button_YrangeMed_Clicked( self, event ):
        """
        Handler for rescaling y-piezo slider range.
        """
        Yloc = self.Yslider.Value
        if Yloc > self.MedRange/2 and Yloc < self.PiezoMax-self.MedRange/2:
            self.Yslider.SetMin( Yloc-self.MedRange/2 )
            self.Yslider.SetMax( Yloc+self.MedRange/2 )
        elif Yloc<self.MedRange/2:
            self.Yslider.SetMin( self.PiezoMin )
            self.Yslider.SetMax( self.MedRange )
        else:
            self.Yslider.SetMin( self.PiezoMax-self.MedRange )
            self.Yslider.SetMax( self.PiezoMax )
        
        self.Yslider.SetLineSize( self.MedRange/50.0 )
        self.Yslider.SetValue(Yloc)
        self.YsliderMax.SetLabel( str(self.Yslider.GetMax()/1000.0) )
        self.YsliderMin.SetLabel( str(self.Yslider.GetMin()/1000.0) )
        #print 'Y range medium'
        
    def On_button_YrangeLg_Clicked( self, event ):
        """
        Handler for rescaling y-piezo slider range.
        """
        Yloc = self.Yslider.Value
        self.Yslider.SetMin( self.PiezoMin )
        self.YsliderMin.SetLabel( str(self.PiezoMin/1000.0) )
        self.Yslider.SetMax( self.PiezoMax )
        self.YsliderMax.SetLabel( str(self.PiezoMax/1000.0) )
        self.Yslider.SetValue(Yloc)
        self.Yslider.SetLineSize( self.PiezoMax/50.0 )
        #print 'Y range large'
        
    def On_Yslider_Changed( self, event ):
        """
        Handler for responding to slider input.
        """
        Yloc = self.Yslider.Value/1000.0
        self.Ylocation.SetValue( str(Yloc) )
        self.piezoY['control'].SetPosition( position=Yloc )
        
    def On_text_Xlocation_Changed( self, event ):
        """
        Handler for updating the z-piezo position in response to text entry.
        """
        Xloc = float(self.Xlocation.GetValue())*1000
        if Xloc > self.Xslider.GetMax() or Xloc < self.Xslider.GetMin():
            # jump to full-scale
            self.Xslider.SetMin( self.PiezoMin )
            self.XsliderMin.SetLabel( str(self.PiezoMin/1000.0) )
            self.Xslider.SetMax( self.PiezoMax )
            self.XsliderMax.SetLabel( str(self.PiezoMax/1000.0) )
            if Xloc > self.PiezoMax:
                self.Xslider.SetValue( self.PiezoMax )
                self.piezoX['control'].SetPositionSmooth( position=self.PiezoMax/1000, step=0.25 )
            elif Xloc < self.PiezoMin:
                self.Xslider.SetValue( self.PiezoMin )
                self.piezoX['control'].SetPositionSmooth( position=self.PiezoMin/1000, step=0.25 )
            else:
                self.Xslider.SetValue( Xloc )
                self.piezoX['control'].SetPositionSmooth( position=Xloc/1000.0, step=0.25 )
        else:
            self.Xslider.SetValue( Xloc )
            self.piezoX['control'].SetPositionSmooth( position=Xloc/1000.0, step=0.25 )
    
    def On_button_XrangeSmall_Clicked( self, event ):
        """
        Handler for rescaling x-piezo slider range.
        """
        Xloc = self.Xslider.Value
        if Xloc > self.SmRange/2 and Xloc < self.PiezoMax-self.SmRange/2:
            self.Xslider.SetMin( Xloc-self.SmRange/2 )
            self.Xslider.SetMax( Xloc+self.SmRange/2 )
        elif Xloc<self.SmRange/2:
            self.Xslider.SetMin( self.PiezoMin )
            self.Xslider.SetMax( self.SmRange )
        else:
            self.Xslider.SetMin( self.PiezoMax-self.SmRange )
            self.Xslider.SetMax( self.PiezoMax )

        self.Xslider.SetLineSize( self.SmRange/50.0 )
        self.Xslider.SetValue(Xloc)
        self.XsliderMax.SetLabel( str(self.Xslider.GetMax()/1000.0) )
        self.XsliderMin.SetLabel( str(self.Xslider.GetMin()/1000.0) )
        #print 'X range small'
        
    def On_button_XrangeMed_Clicked( self, event ):
        """
        Handler for rescaling x-piezo slider range.
        """
        Xloc = self.Xslider.Value
        if Xloc > self.MedRange/2 and Xloc < self.PiezoMax-self.MedRange/2:
            self.Xslider.SetMin( Xloc-self.MedRange/2 )
            self.Xslider.SetMax( Xloc+self.MedRange/2 )
        elif Xloc<self.MedRange/2:
            self.Xslider.SetMin( self.PiezoMin )
            self.Xslider.SetMax( self.MedRange )
        else:
            self.Xslider.SetMin( self.PiezoMax-self.MedRange )
            self.Xslider.SetMax( self.PiezoMax )
        
        self.Xslider.SetLineSize( self.MedRange/50.0 )
        self.Xslider.SetValue(Xloc)
        self.XsliderMax.SetLabel( str(self.Xslider.GetMax()/1000.0) )
        self.XsliderMin.SetLabel( str(self.Xslider.GetMin()/1000.0) )
        #print 'X range medium'
        
    def On_button_XrangeLg_Clicked( self, event ):
        """
        Handler for rescaling x-piezo slider range.
        """
        Xloc = self.Xslider.Value
        self.Xslider.SetMin( self.PiezoMin )
        self.XsliderMin.SetLabel( str(self.PiezoMin/1000.0) )
        self.Xslider.SetMax( self.PiezoMax )
        self.XsliderMax.SetLabel( str(self.PiezoMax/1000.0) )
        self.Xslider.SetValue(Xloc)
        self.Xslider.SetLineSize( self.PiezoMax/50.0 )
        #print 'X range large'
        
    def On_Xslider_Changed( self, event ):
        """
        Handler for responding to slider input.
        """
        Xloc = self.Xslider.Value/1000.0
        self.Xlocation.SetValue( str(Xloc) )
        self.piezoX['control'].SetPosition( position=Xloc )
        

if __name__ == "__main__":
    """Test the appearance of the frame.
    Running stand-alone has no actual piezo functionality."""
    
    class FakePiezoController:
        """No actual functionality, just says and does all the right things..."""
        def __init__(self):
            self.PositionCh1 = 0.0
            self.min_position = 0.0
            self.max_position = 20.0
            
        def SetPosition( self, position ):
            self.PositionCh1 = position
            
    class MainApp(wx.App): 
        def __init__(self, redirect=False, filename=None):
            wx.App.__init__(self, redirect, filename)
            self.Bind( wx.EVT_CLOSE, self.on_close )
            self.mainframe = MakeMainWindow()

        def on_close( self, event ):
            self.Destroy()
            
    class MakeMainWindow( wx.Frame ):
        def __init__( self, parent=None, id=wx.ID_ANY ):
            wx.Frame.__init__( self, parent=None, id=wx.ID_ANY, title='pyPiezos', size=wx.Size(350, 320) )
            self.fake_positioners()
            self.mainpanel = MainPanel( self, positioners=self.positioners )
            self.Centre()
            self.Show(True)
            
        def fake_positioners( self ):
            piezoX = dict( control=FakePiezoController(), direction=1 )
            piezoY = dict( control=FakePiezoController(), direction=1 )
            piezoZ = dict( control=FakePiezoController(), direction=1 )
            self.positioners = dict( piezoX=piezoX, piezoY=piezoY, piezoZ=piezoZ )


    app = MainApp()
    app.MainLoop()

""" In an ideal world, this will be a complete working library
    for the APTMotor
"""
import wx.lib.activex
import comtypes.client as cc
from ctypes import byref, pointer, c_long, c_float, c_bool

cc.GetModule( ('{9460A175-8618-4753-B337-61D9771C4C14}', 1, 0) )
progID_system = 'MG17SYSTEM.MG17SystemCtrl.1'
import comtypes.gen.MG17SystemLib as APTSystemLib

motorcontrollercard = APTSystemLib.CARD_SCC101 
piezocontrollercard = APTSystemLib.CARD_PCC101 

class APTSystem( wx.lib.activex.ActiveXCtrl ):
    """The System class derives from wx.lib.activex.ActiveXCtrl, which
       is where all the heavy lifting with COM gets done."""
    
    def __init__( self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name='APTSystem' ):
        wx.lib.activex.ActiveXCtrl.__init__(self, parent, progID_system,
                                            id, pos, size, style, name)
        self.ctrl.StartCtrl()
    
    def GetNumMotorControllerCards( self ):
        """ runs the activeX command *GetNumHWUnitsEx* to return
        the number of stepper motor controller cards in the system. """
        numcards = c_long()
        self.ctrl.GetNumHWUnitsEx( motorcontrollercard, byref( numcards ) )
        return numcards.value

    def GetNumPiezoControllerCards( self ):
        """ runs the activeX command *GetNumHWUnitsEx* to return
        the number of piezo controller cards in the system. """
        numcards = c_long()
        self.ctrl.GetNumHWUnitsEx( piezocontrollercard, byref( numcards ) )
        return numcards.value

    def GetMotorSerialNumbers( self ):
        """ runs the activeX command *GetHWSerialNumEx* to return
        a list of serial numbers for all of the motor controller cards."""
        serialnumber = c_long()
        numberlist = None
        numcards = self.GetNumMotorControllerCards()
        if numcards > 0:
            numberlist = []
            for card in range(numcards):
                self.ctrl.GetHWSerialNumEx( motorcontrollercard, card, byref(serialnumber) )
                numberlist.append( serialnumber.value )
        return numberlist
    
    def GetPiezoSerialNumbers( self ):
        """ runs the activeX command *GetHWSerialNumEx* to return
        a list of serial numbers for all of the piezo controller cards."""
        serialnumber = c_long()
        numberlist = None
        numcards = self.GetNumPiezoControllerCards()
        if numcards > 0:
            numberlist = []
            for card in range(numcards):
                self.ctrl.GetHWSerialNumEx( piezocontrollercard, card, byref(serialnumber) )
                numberlist.append( serialnumber.value )
        return numberlist
    
    def GetHWUnits( self ):
        """ runs the activeX command *GetNumHWUnitsEx* to return
        the number of hardware units connected."""
   
        hwtypes = range(11,44)
        types = []
        for hw in hwtypes:
            numunit = c_long()
            self.ctrl.GetNumHWUnitsEx( hw, byref( numunit ) )
            print hw, numunit.value
            types.append( numunit.value )
        return types

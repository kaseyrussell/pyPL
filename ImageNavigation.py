""" Navigate to points on your sample by clicking on a picture of it.
    This is part of the pyPL/pyPositioning program.

    Copyright 2010 Kasey Russell ( email: krussell _at_ post.harvard.edu )
    Distributed under the GNU General Public License
"""
from __future__ import division
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
import Image

ID_Image_Load = wx.NewId()
ID_Help = wx.NewId()

stage_image_flipped = False # is your PL visualization flipped wrt actual?

class MainApp( wx.App ):
    """ ... """
    def __init__( self, redirect=False, filename=None ):
        wx.App.__init__( self, redirect, filename )
        
        self.mainframe = MainFrame()
        
class MainFrame( wx.Frame ):
    """Main image navigation window. """
    def __init__( self, parent=None, id=wx.ID_ANY, title='Image Navigation',
                 size=wx.Size(500,500) ):
        wx.Frame.__init__( self, None, id=id, title=title, size=size )
        
        if parent is not None:
            self.positioners = parent.positioners
        else:
            # include this for motor-less testing
            self.positioners = dict( motorX=None, motorY=None )
        
        self.p1 = None
        self.p2 = None
        self.calibrated = [False, False]
        self.calibrate_p1 = False
        self.calibrate_p2 = False
        self.moveto = False
        self.cid = None
        
        self.plotpanel = wx.Panel( self, id=wx.ID_ANY )
        box = wx.BoxSizer( wx.VERTICAL )

        #self.fig = pylab.figure( facecolor='white' )
        self.fig = Figure( facecolor='white' )
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_off()
        
        self.canvas = FigureCanvas( parent=self.plotpanel, id=wx.ID_ANY,
                                   figure=self.fig )
        box.Add( self.canvas, proportion = 1, flag=wx.EXPAND, border=10 )

        ######## toolbar sizer; includes marker making button and text entry field
        boxToolbar = wx.BoxSizer( wx.HORIZONTAL )
        mpl_toolbar = MPLToolbar( self.fig.canvas )
        boxToolbar.Add( mpl_toolbar, proportion = .2, flag=wx.BOTTOM, border=5 )
        
        boxToolbar.AddStretchSpacer(1)
        
        self.txt_move_indicator = wx.StaticText( parent=self.plotpanel,
                                            id=wx.ID_ANY,
                                            label="Image not yet calibrated.",
                                            size=(150,15) )
        boxToolbar.Add( self.txt_move_indicator, flag=wx.CENTER )
        
        self.button_move = wx.Button( self.plotpanel, wx.ID_ANY, '' )
        boxToolbar.Add( self.button_move, flag=wx.CENTER|wx.RIGHT, border=2 )
        self.button_move.Bind( wx.EVT_BUTTON, self.on_button_clicked_move )

        box.Add( boxToolbar, 0, wx.EXPAND )
        
        # calibration information:
        #
        # point 1:
        box_p1 = wx.BoxSizer( wx.HORIZONTAL )
        box_p1.Add( wx.StaticText( parent=self.plotpanel, id=wx.ID_ANY,
                                  label="Point 1: " ),
                    flag=wx.CENTER|wx.ALL, border=5 )
        self.button_calibrate_p1 = wx.Button( self.plotpanel, wx.ID_ANY, 'set' )
        box_p1.Add( self.button_calibrate_p1, flag=wx.CENTER )
        self.button_calibrate_p1.Bind( wx.EVT_BUTTON,
                                      self.on_button_clicked_calibrate_p1 )
        self.info_calibration_p1 = wx.StaticText( parent=self.plotpanel,
                                                  id=wx.ID_ANY,
                                                  label='(uncalibrated)' )
        box_p1.Add( self.info_calibration_p1, flag=wx.CENTER|wx.ALL, border=5 )
        box.Add( box_p1, proportion=0, flag=wx.EXPAND )

        # point 2:
        box_p2 = wx.BoxSizer( wx.HORIZONTAL )
        box_p2.Add( wx.StaticText( parent=self.plotpanel, id=wx.ID_ANY,
                                  label="Point 2: " ),
                    flag=wx.CENTER|wx.ALL, border=5 )
        self.button_calibrate_p2 = wx.Button( self.plotpanel, wx.ID_ANY, 'set' )
        box_p2.Add( self.button_calibrate_p2, flag=wx.CENTER )
        self.button_calibrate_p2.Bind( wx.EVT_BUTTON,
                                      self.on_button_clicked_calibrate_p2 )
        self.info_calibration_p2 = wx.StaticText( parent=self.plotpanel,
                                                  id=wx.ID_ANY,
                                                  label='(uncalibrated)' )
        box_p2.Add( self.info_calibration_p2, flag=wx.CENTER|wx.ALL, border=5 )
        box.Add( box_p2, proportion=0, flag=wx.EXPAND )

        # image flipped?:
        self.choices = dict( flipped="this image is flipped with respect to the sample",
                             notflipped="this image is NOT flipped with respect to the sample" )
        self.flip_dropdown = wx.ComboBox( parent=self.plotpanel, id=wx.ID_ANY,
                                          choices=[ self.choices['flipped'],
                                                    self.choices['notflipped'] ],
                                          style=wx.CB_DROPDOWN|wx.CB_READONLY )
        self.flip_dropdown.SetValue( self.choices['notflipped'] )
        self.flip_dropdown.Bind( wx.EVT_COMBOBOX, self.on_flip_dropdown_changed )
        box.Add( self.flip_dropdown, proportion=0, flag=wx.ALL, border=4 )
        self.plotpanel.SetSizer( box )

        self.add_menu_bar()
        self.Show( True )


    def add_menu_bar(self):
        """ Add menu bar to the window. """
        menuBar = wx.MenuBar()

        """ Image menu
        """
        image_menu = wx.Menu()
        image_menu.Append( ID_Image_Load, "Load Image",
                          "Load a picture of your sample" )
        wx.EVT_MENU( self, ID_Image_Load, self.on_image_menu_load_image )
    
        menuBar.Append( image_menu, "&Image" )

        """ Help menu
        """
        help_menu = wx.Menu()
        help_menu.Append( ID_Help, "Help", "How does image navigation work?" )
        wx.EVT_MENU( self, ID_Help, self.on_help_menu_help )
    
        menuBar.Append( help_menu, "&Help" )

        self.SetMenuBar( menuBar )

    def calculate_calibration(self):
        """ 
            the calibration finds the difference in angle and length
            between the vectors from p1 to p2 in the image and
            on the stage
        """
        dx_image = self.p2['image'][0] - self.p1['image'][0] 
        if dx_image == 0:
            dx_image = 1.0e-15 # prevent a divide-by-zero error
        dy_image = self.p2['image'][1] - self.p1['image'][1] 
        r_image = pylab.sqrt(dx_image**2 + dy_image**2)
        theta_image = pylab.arctan( dy_image/dx_image )
        if dx_image < 0:
            theta_image += pylab.pi
            
        dx_stage = self.p2['stage'][0] - self.p1['stage'][0] 
        if dx_stage == 0:
            dx_stage = 1.0e-15 # prevent a divide-by-zero error
        dy_stage = self.p2['stage'][1] - self.p1['stage'][1] 
        r_stage = pylab.sqrt(dx_stage**2 + dy_stage**2)
        theta_stage = pylab.arctan( dy_stage/dx_stage )
        if dx_stage < 0:
            theta_stage += pylab.pi
            
        if self.flip_dropdown.GetValue() == self.choices['notflipped']:
            theta_stage *= -1

        if stage_image_flipped:
            theta_stage *= -1
            
        self.calibration = dict( rotation = theta_stage - theta_image,
                                 dilation = r_stage/r_image )
        

    def calculate_target_position( self, x_image, y_image ):
        """
            The target position is calculated relative to p1, using
            the rotation and dilation 
        """
        dx_image = x_image - self.p1['image'][0] 
        dy_image = y_image - self.p1['image'][1] 
        r_image = pylab.sqrt(dx_image**2 + dy_image**2)
        theta_image = pylab.arctan( dy_image/dx_image )
        if dx_image < 0:
            theta_image += pylab.pi
            
        r_stage = r_image * self.calibration['dilation']
        theta_stage = theta_image + self.calibration['rotation']
            
        if self.flip_dropdown.GetValue() == self.choices['notflipped']:
            theta_stage *= -1

        if stage_image_flipped:
            theta_stage *= -1
            
        x_stage = r_stage * pylab.cos( theta_stage ) + self.p1['stage'][0]
        y_stage = r_stage * pylab.sin( theta_stage ) + self.p1['stage'][1]
        return x_stage, y_stage
        

    def on_button_clicked_calibrate_p1( self, event ):
        """ Handler for button click. """
        if self.calibrate_p1 == False:
            self.calibrate_p1 = True
            self.info_calibration_p1.SetLabel("The next point you click on the picture will be recorded.")
            if self.cid is not None:
                if self.calibrate_p2:
                    self.on_button_clicked_calibrate_p2( None )
                elif self.moveto:
                    self.on_button_clicked_move( None )
            self.cid = self.fig.canvas.mpl_connect( 'button_press_event', self.on_mouse_clicked )
            self.button_calibrate_p1.SetLabel( "cancel" )
        else:
            # then we've already clicked this button and are trying to cancel the set
            self.fig.canvas.mpl_disconnect( self.cid )
            self.cid = None
            self.button_calibrate_p1.SetLabel( "set" )
            self.info_calibration_p1.SetLabel( "aborted" )
            self.calibrate_p1 = False
        
        
    def on_button_clicked_calibrate_p2( self, event ):
        """ Handler for button click. """
        if self.calibrate_p2 == False:
            self.calibrate_p2 = True
            self.info_calibration_p2.SetLabel("The next point you click on the picture will be recorded.")
            if self.cid is not None:
                if self.calibrate_p1:
                    self.on_button_clicked_calibrate_p1( None )
                elif self.moveto:
                    self.on_button_clicked_move( None )
            self.cid = self.fig.canvas.mpl_connect( 'button_press_event', self.on_mouse_clicked )
            self.button_calibrate_p2.SetLabel( "cancel" )
        else:
            # then we've already clicked this button and are trying to cancel the set
            self.fig.canvas.mpl_disconnect( self.cid )
            self.cid = None
            self.button_calibrate_p2.SetLabel( "set" )
            self.info_calibration_p2.SetLabel( "aborted" )
            self.calibrate_p2 = False
        
        
    def on_button_clicked_move( self, event ):
        """ Handler for button click. """
        if self.moveto == False:
            self.moveto = True
            if self.cid is not None:
                self.fig.canvas.mpl_disconnect( self.cid )
            self.cid = self.fig.canvas.mpl_connect( 'button_press_event', self.on_mouse_clicked )
            self.button_move.SetLabel( "cancel" )
        else:
            # then we're trying to cancel the move-to
            self.fig.canvas.mpl_disconnect( self.cid )
            self.cid = None
            self.button_move.SetLabel( "move to click" )
            self.moveto = False
            self.txt_move_indicator.SetLabel( "move aborted." )

    
    def on_flip_dropdown_changed( self, event ):
        """ Handler for changing the flip/don't flip dropdown chooser. """
        if all( self.calibrated ):
            self.calculate_calibration()
    

    def on_help_menu_help( self, event ):
        """ Handler dealing with selection of the help menu. """
        pass
    
    
    def on_image_menu_load_image( self, event ):
        """ Handler. """
        filters = 'All files (*.*)|*.*|PNG files (*.png)|*.png|JPEG files (*.jpg,*.jpeg)|*.jpg;*.jpeg|TIFF files (*.tif,*.tiff)|*.tif;*.tiff'
        dialog = wx.FileDialog ( None, message = 'Open something....',
                                wildcard = filters, style = wx.OPEN )

        if dialog.ShowModal() == wx.ID_OK:
            self.fname = dialog.GetPath()
            device_image = Image.open( self.fname )
            self.fig.clf()
            self.axes = self.fig.add_axes( [0,0,1,1], frameon=False )
            self.axes.imshow( device_image, origin='lower' )
            self.axes.axis('image')
            self.axes.axis('off')
            self.fig.canvas.draw()
            
            self.p1 = None
            self.p2 = None
            self.info_calibration_p1.SetLabel('(uncalibrated)')
            self.info_calibration_p2.SetLabel('(uncalibrated)')
            self.calibrated = [False, False]
            self.txt_move_indicator.SetLabel( "Image not yet calibrated." )
            
        dialog.Destroy()


    def on_mouse_clicked( self, event ):
        """ Event handler. """
        if not event.inaxes:
            return
        
        self.fig.canvas.mpl_disconnect( self.cid )
        self.cid = None

        if self.calibrate_p1:
            if self.positioners['motorX'] is not None:
                x_stage = self.positioners['motorX']['control'].GetPosition()

            if self.positioners['motorY'] is not None:
                y_stage = self.positioners['motorY']['control'].GetPosition()
                
            self.p1 = dict( image=(event.xdata, event.ydata) )
            if self.positioners['motorX'] is not None and self.positioners['motorY'] is not None:
                self.p1['stage']=(x_stage, y_stage)
            else:
                # just fill in dummy data
                self.p1['stage']=(0.0, 0.0)
                
            self.info_calibration_p1.SetLabel( 
                  "image: (%d, %d)  stage: x: %.3f mm, y: %.3f mm" % (event.xdata, event.ydata, self.p1['stage'][0], self.p1['stage'][1])
                  )
            self.calibrated[0] = True
            self.calibrate_p1 = False
            self.button_calibrate_p1.SetLabel( "set" )

        elif self.calibrate_p2:
            if self.positioners['motorX'] is not None:
                x_stage = self.positioners['motorX']['control'].GetPosition()
                
            if self.positioners['motorY'] is not None:
                y_stage = self.positioners['motorY']['control'].GetPosition()
                
            self.p2 = dict( image=(event.xdata, event.ydata) )
            if self.positioners['motorX'] is not None and self.positioners['motorY'] is not None:
                self.p2['stage']=(x_stage, y_stage)
            else:
                # just fill in dummy data
                self.p2['stage']=(1.0, 1.0)
                
            self.info_calibration_p2.SetLabel( 
                  "image: (%d, %d)  stage: x: %.3f mm, y: %.3f mm" % (event.xdata, event.ydata, self.p2['stage'][0], self.p2['stage'][1])
                  )
            self.calibrated[1] = True
            self.calibrate_p2 = False
            self.button_calibrate_p2.SetLabel( "set" )
        
        if all( self.calibrated ) and self.moveto==False:
            self.txt_move_indicator.SetLabel( "Image calibrated." )
            self.button_move.SetLabel( "move to click" )
            self.calculate_calibration()
        
        elif self.moveto:
            self.moveto = False
            self.button_move.SetLabel( "move to click" )
            x_stage, y_stage = self.calculate_target_position( event.xdata, event.ydata )
            
            if self.positioners['motorX'] is not None:
                self.positioners['motorX']['control'].MoveAbsoluteEx( x_stage, wait=False )
                
            if self.positioners['motorY'] is not None:
                self.positioners['motorY']['control'].MoveAbsoluteEx( y_stage, wait=False )

            self.txt_move_indicator.SetLabel( "x: %.3f mm, y: %.3f mm" % (x_stage, y_stage) )
        

if __name__== '__main__': 
    app = MainApp()

    app.MainLoop()


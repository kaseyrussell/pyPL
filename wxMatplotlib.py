import wx
import matplotlib
if matplotlib.get_backend() != 'WXAgg':
    # this is actually just to check if it's loaded. if it already was loaded
    # and set to a different backend, then we couldn't change it anyway.
    matplotlib.use('WXAgg')

from matplotlib.figure import Figure as MatplotlibFigure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as MatplotlibFigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as MatplotlibToolbar


class Figure():
    """ WxAgg version of the Matplotlib figure.
        Pass it a wx.Panel as a parent, and then you can
        access axes, etc.
        I tried directly inheriting from MatplotlibFigure but
        I kept getting an error about the axes not being iterable...
    """
    def __init__( self, parent, **kwargs ):
        self.fig = MatplotlibFigure( facecolor=(0.94117,0.92156,0.88627), figsize=(4,4) )
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)
        
        if 'xlabel' in kwargs.keys():
            self.axes.set_xlabel( kwargs['xlabel'] )

        if 'ylabel' in kwargs.keys():
            self.axes.set_ylabel( kwargs['ylabel'] )

        self.canvas = MatplotlibFigureCanvas( parent=parent, id=wx.ID_ANY,
                        figure=self.fig )

class Toolbar( MatplotlibToolbar ):
    """ An inherited class of the WxAgg version of the Matplotlib toolbar.
        Just pass it a matplotlib canvas.
    """
    def __init__( self, canvas ):
        MatplotlibToolbar.__init__( self, canvas )


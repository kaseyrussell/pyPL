# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Apr 11 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wxMatplotlib
import wx.grid

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"pyRaster", pos = wx.DefaultPosition, size = wx.Size( 1300,650 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.mainframe_menubar = wx.MenuBar( 0 )
		self.menu_file = wx.Menu()
		self.menu_file_open = wx.MenuItem( self.menu_file, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL )
		self.menu_file.AppendItem( self.menu_file_open )
		
		self.mainframe_menubar.Append( self.menu_file, u"File" ) 
		
		self.menu_scan = wx.Menu()
		self.menu_scan_3D = wx.MenuItem( self.menu_scan, wx.ID_ANY, u"3D Scan", wx.EmptyString, wx.ITEM_CHECK )
		self.menu_scan.AppendItem( self.menu_scan_3D )
		
		self.mainframe_menubar.Append( self.menu_scan, u"Scan" ) 
		
		self.SetMenuBar( self.mainframe_menubar )
		
		self.statusbar = self.CreateStatusBar( 3, wx.ST_SIZEGRIP, wx.ID_ANY )
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.mainpanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		sizer_controls = wx.BoxSizer( wx.VERTICAL )
		
		sizer_controls.SetMinSize( wx.Size( 50,-1 ) ) 
		self.m_staticText6 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Scan parameters:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		sizer_controls.Add( self.m_staticText6, 0, wx.ALL, 5 )
		
		self.m_staticline5 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_controls.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText2 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Width (um):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		bSizer6.Add( self.m_staticText2, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )
		
		self.txtctrl_scan_width = wx.TextCtrl( self.mainpanel, wx.ID_ANY, u"5", wx.DefaultPosition, wx.Size( 50,-1 ), wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		bSizer6.Add( self.txtctrl_scan_width, 1, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		sizer_controls.Add( bSizer6, 1, wx.EXPAND, 0 )
		
		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText4 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"# x points:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		bSizer8.Add( self.m_staticText4, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )
		
		self.txtctrl_scan_num_xpoints = wx.TextCtrl( self.mainpanel, wx.ID_ANY, u"11", wx.DefaultPosition, wx.Size( 40,-1 ), wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		bSizer8.Add( self.txtctrl_scan_num_xpoints, 1, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		sizer_controls.Add( bSizer8, 1, wx.EXPAND, 0 )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText61 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Res. (um/pt):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText61.Wrap( -1 )
		bSizer10.Add( self.m_staticText61, 0, wx.ALL, 5 )
		
		self.txtlabel_scan_width_resolution = wx.StaticText( self.mainpanel, wx.ID_ANY, u"0.500", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txtlabel_scan_width_resolution.Wrap( -1 )
		bSizer10.Add( self.txtlabel_scan_width_resolution, 0, wx.ALL, 5 )
		
		sizer_controls.Add( bSizer10, 1, wx.EXPAND, 5 )
		
		self.m_staticline61 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_controls.Add( self.m_staticline61, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText3 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Height (um):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		bSizer7.Add( self.m_staticText3, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )
		
		self.txtctrl_scan_height = wx.TextCtrl( self.mainpanel, wx.ID_ANY, u"5", wx.DefaultPosition, wx.Size( 30,-1 ), wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		bSizer7.Add( self.txtctrl_scan_height, 1, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		sizer_controls.Add( bSizer7, 1, wx.EXPAND, 5 )
		
		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText5 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"# y points:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		bSizer9.Add( self.m_staticText5, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )
		
		self.txtctrl_scan_num_ypoints = wx.TextCtrl( self.mainpanel, wx.ID_ANY, u"11", wx.DefaultPosition, wx.Size( 30,-1 ), wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		bSizer9.Add( self.txtctrl_scan_num_ypoints, 1, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		sizer_controls.Add( bSizer9, 1, wx.EXPAND, 5 )
		
		bSizer101 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText611 = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Res. (um/pt):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText611.Wrap( -1 )
		bSizer101.Add( self.m_staticText611, 0, wx.ALL, 5 )
		
		self.txtlabel_scan_height_resolution = wx.StaticText( self.mainpanel, wx.ID_ANY, u"0.500", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txtlabel_scan_height_resolution.Wrap( -1 )
		bSizer101.Add( self.txtlabel_scan_height_resolution, 0, wx.ALL, 5 )
		
		sizer_controls.Add( bSizer101, 1, wx.EXPAND, 5 )
		
		self.staticline_z = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_controls.Add( self.staticline_z, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.txtlabel_zrange = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Z range (um):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txtlabel_zrange.Wrap( -1 )
		bSizer12.Add( self.txtlabel_zrange, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )
		
		self.txtctrl_scan_zrange = wx.TextCtrl( self.mainpanel, wx.ID_ANY, u"5", wx.DefaultPosition, wx.Size( 30,-1 ), wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		bSizer12.Add( self.txtctrl_scan_zrange, 1, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		sizer_controls.Add( bSizer12, 1, wx.EXPAND, 5 )
		
		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.txtlabel_zpoints = wx.StaticText( self.mainpanel, wx.ID_ANY, u"# z points:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txtlabel_zpoints.Wrap( -1 )
		bSizer13.Add( self.txtlabel_zpoints, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )
		
		self.txtctrl_scan_num_zpoints = wx.TextCtrl( self.mainpanel, wx.ID_ANY, u"11", wx.DefaultPosition, wx.Size( 30,-1 ), wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		bSizer13.Add( self.txtctrl_scan_num_zpoints, 1, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5 )
		
		sizer_controls.Add( bSizer13, 1, wx.EXPAND, 5 )
		
		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.txtlabel_zres = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Res. (um/pt):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txtlabel_zres.Wrap( -1 )
		bSizer14.Add( self.txtlabel_zres, 0, wx.ALL, 5 )
		
		self.txtlabel_scan_z_resolution = wx.StaticText( self.mainpanel, wx.ID_ANY, u"0.500", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.txtlabel_scan_z_resolution.Wrap( -1 )
		bSizer14.Add( self.txtlabel_scan_z_resolution, 0, wx.ALL, 5 )
		
		sizer_controls.Add( bSizer14, 1, wx.EXPAND, 5 )
		
		self.m_staticline8 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_controls.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )
		
		choice_Winspec_or_APDsChoices = [ u"Winspec", u"APDs" ]
		self.choice_Winspec_or_APDs = wx.Choice( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_Winspec_or_APDsChoices, 0 )
		self.choice_Winspec_or_APDs.SetSelection( 0 )
		sizer_controls.Add( self.choice_Winspec_or_APDs, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.button_start = wx.Button( self.mainpanel, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_controls.Add( self.button_start, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.button_stop = wx.Button( self.mainpanel, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_controls.Add( self.button_stop, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.button_save = wx.Button( self.mainpanel, wx.ID_ANY, u"Save at end", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_controls.Add( self.button_save, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		self.m_staticline7 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizer_controls.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.button_move_to_click = wx.Button( self.mainpanel, wx.ID_ANY, u"-----", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.button_move_to_click.SetToolTipString( u"Move piezos to the place you click on the plot" )
		
		sizer_controls.Add( self.button_move_to_click, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		bSizer2.Add( sizer_controls, 0, 0, 5 )
		
		self.m_staticline1 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.LI_VERTICAL )
		bSizer2.Add( self.m_staticline1, 0, wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.fig1 = wxMatplotlib.Figure(self.mainpanel, xlabel='Position ($\mu$m)', ylabel='Position ($\mu$m)')
		bSizer3.Add( self.fig1.canvas, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		
		self.fig1_toolbar = wxMatplotlib.Toolbar( self.fig1.canvas )
		bSizer3.Add( self.fig1_toolbar, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT, 5 )
		
		bSizer2.Add( bSizer3, 4, wx.EXPAND, 5 )
		
		self.m_staticline3 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer2.Add( self.m_staticline3, 0, wx.EXPAND, 5 )
		
		bSizerSpectrum = wx.BoxSizer( wx.VERTICAL )
		
		self.grid = wx.grid.Grid( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL )
		
		# Grid
		self.grid.CreateGrid( 0, 3 )
		self.grid.EnableEditing( True )
		self.grid.EnableGridLines( True )
		self.grid.EnableDragGridSize( False )
		self.grid.SetMargins( 0, 0 )
		
		# Columns
		self.grid.EnableDragColMove( False )
		self.grid.EnableDragColSize( True )
		self.grid.SetColLabelSize( 30 )
		self.grid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.grid.EnableDragRowSize( True )
		self.grid.SetRowLabelSize( 80 )
		self.grid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizerSpectrum.Add( self.grid, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticline4 = wx.StaticLine( self.mainpanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizerSpectrum.Add( self.m_staticline4, 0, wx.EXPAND, 5 )
		
		self.slider_integration_min = wx.Slider( self.mainpanel, wx.ID_ANY, 0, 0, 1339, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizerSpectrum.Add( self.slider_integration_min, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 65 )
		
		self.slider_integration_max = wx.Slider( self.mainpanel, wx.ID_ANY, 1339, 0, 1339, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizerSpectrum.Add( self.slider_integration_max, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 65 )
		
		self.fig2 = wxMatplotlib.Figure(self.mainpanel, xlabel='Wavelength (nm)', ylabel='Intensity (arb. units)')
		bSizerSpectrum.Add( self.fig2.canvas, 2, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		
		self.fig2_toolbar = wxMatplotlib.Toolbar( self.fig2.canvas )
		bSizerSpectrum.Add( self.fig2_toolbar, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT, 5 )
		
		bSizer2.Add( bSizerSpectrum, 4, wx.EXPAND, 5 )
		
		self.mainpanel.SetSizer( bSizer2 )
		self.mainpanel.Layout()
		bSizer2.Fit( self.mainpanel )
		bSizer1.Add( self.mainpanel, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_close_MainFrame )
		self.Bind( wx.EVT_MENU, self.on_menu_file_open, id = self.menu_file_open.GetId() )
		self.Bind( wx.EVT_MENU, self.on_menu_scan_3D, id = self.menu_scan_3D.GetId() )
		self.txtctrl_scan_width.Bind( wx.EVT_TEXT, self.on_txtctrl_scan_width_changed )
		self.txtctrl_scan_num_xpoints.Bind( wx.EVT_TEXT, self.on_txtctrl_scan_num_xpoints_changed )
		self.txtctrl_scan_height.Bind( wx.EVT_TEXT, self.on_txtctrl_scan_height_changed )
		self.txtctrl_scan_num_ypoints.Bind( wx.EVT_TEXT, self.on_txtctrl_scan_num_ypoints_changed )
		self.txtctrl_scan_zrange.Bind( wx.EVT_TEXT, self.on_txtctrl_scan_zrange_changed )
		self.txtctrl_scan_num_zpoints.Bind( wx.EVT_TEXT, self.on_txtctrl_scan_num_zpoints_changed )
		self.button_start.Bind( wx.EVT_BUTTON, self.on_button_start_clicked )
		self.button_stop.Bind( wx.EVT_BUTTON, self.on_button_stop_clicked )
		self.button_save.Bind( wx.EVT_BUTTON, self.on_button_save_clicked )
		self.button_save.Bind( wx.EVT_LEAVE_WINDOW, self.on_button_save_mouseleave )
		self.button_save.Bind( wx.EVT_MOTION, self.on_button_save_mouseover )
		self.button_move_to_click.Bind( wx.EVT_BUTTON, self.on_button_move_to_click_clicked )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_grid_leftclick )
		self.grid.Bind( wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_grid_label_right_click )
		self.slider_integration_min.Bind( wx.EVT_SCROLL, self.on_slider_integration_min_moving )
		self.slider_integration_min.Bind( wx.EVT_SCROLL_THUMBRELEASE, self.on_slider_integration_min_changed )
		self.slider_integration_max.Bind( wx.EVT_SCROLL, self.on_slider_integration_max_moving )
		self.slider_integration_max.Bind( wx.EVT_SCROLL_THUMBRELEASE, self.on_slider_integration_max_changed )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_close_MainFrame( self, event ):
		event.Skip()
	
	def on_menu_file_open( self, event ):
		event.Skip()
	
	def on_menu_scan_3D( self, event ):
		event.Skip()
	
	def on_txtctrl_scan_width_changed( self, event ):
		event.Skip()
	
	def on_txtctrl_scan_num_xpoints_changed( self, event ):
		event.Skip()
	
	def on_txtctrl_scan_height_changed( self, event ):
		event.Skip()
	
	def on_txtctrl_scan_num_ypoints_changed( self, event ):
		event.Skip()
	
	def on_txtctrl_scan_zrange_changed( self, event ):
		event.Skip()
	
	def on_txtctrl_scan_num_zpoints_changed( self, event ):
		event.Skip()
	
	def on_button_start_clicked( self, event ):
		event.Skip()
	
	def on_button_stop_clicked( self, event ):
		event.Skip()
	
	def on_button_save_clicked( self, event ):
		event.Skip()
	
	def on_button_save_mouseleave( self, event ):
		event.Skip()
	
	def on_button_save_mouseover( self, event ):
		event.Skip()
	
	def on_button_move_to_click_clicked( self, event ):
		event.Skip()
	
	def on_grid_leftclick( self, event ):
		event.Skip()
	
	def on_grid_label_right_click( self, event ):
		event.Skip()
	
	def on_slider_integration_min_moving( self, event ):
		event.Skip()
	
	def on_slider_integration_min_changed( self, event ):
		event.Skip()
	
	def on_slider_integration_max_moving( self, event ):
		event.Skip()
	
	def on_slider_integration_max_changed( self, event ):
		event.Skip()
	


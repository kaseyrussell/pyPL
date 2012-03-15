import ctypes
phlib = ctypes.windll.phlib
b = c_char() #more awesome if string...
phlib.PH_GetLibraryVersion(byref(b))
serial = c_char_p('xxxxxx')
phlib.PH_OpenDevice( c_int(0), byref(serial) )
phlib.PH_Initialize( c_int(0), c_int(2) )
print 'resolution:', phlib.PH_GetBaseResolution( c_int(0) )
print 'Channel1 rate:', phlib.PH_GetCountRate( c_int(0), c_int(0) )
print 'Channel1 rate:', phlib.PH_GetCountRate( c_int(0), c_int(1) )
phlib.PH_CloseDevice( c_int(0) )


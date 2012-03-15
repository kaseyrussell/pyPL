import ctypes
from pylab import *
phlib = ctypes.windll.phlib

block_size = 32768
histogram_channels = 65536
TTREADMAX = 131072   # 128K event records
ranges = 8
buffer = (ctypes.c_long*TTREADMAX)()
ctypes.cast( buffer, ctypes.POINTER( ctypes.c_long ) )

device0 = ctypes.c_int(0)
channel0 = ctypes.c_int(0)
channel1 = ctypes.c_int(1)

Discr0 = ctypes.c_long(50)     # in mV
ZeroCross0 = ctypes.c_long(10) # in mV
sync_divider = 1
SyncDivider = ctypes.c_long(1) # 1 is "None"

b = ctypes.c_char() #more awesome if string...
phlib.PH_GetLibraryVersion( ctypes.byref(b) )

def shutdown( device, normal_operation=True ):
    print 'Closing device...'
    phlib.PH_CloseDevice( device )
    if not normal_operation: raise ValueError('done.')

print "opening device..."
serial = ctypes.c_char_p('xxxxxx')
if phlib.PH_OpenDevice( device0, ctypes.byref(serial) ) < 0: shutdown( device0, normal_operation=False )

print "initializing device..."
if phlib.PH_Initialize( device0, ctypes.c_int(2) ) < 0: shutdown( device0, normal_operation=False )

print 'setting sync divider to', sync_divider
if phlib.PH_SetSyncDiv( device0, ctypes.c_long(sync_divider) ) < 0: shutdown( device0, normal_operation=False )

print 'Channel0 rate:', phlib.PH_GetCountRate( device0, channel0 )

acquisition_time = 10 # acquisition time in ms. somehow answer only makes sense for acq. less than 150ms
if phlib.PH_StartMeas( device0, acquisition_time ) < 0: shutdown( device0, normal_operation=False )
    
import time
time.sleep( acquisition_time/1000.0 )

if phlib.PH_CTCStatus( device0 ):
    print 'done'
    print 'reading data'
    if phlib.PH_TTReadData( device0, ctypes.pointer(buffer), ctypes.c_long(block_size) ) < 0:
        shutdown( device0, normal_operation=False )
else:
    print 'not done'

g = array(buffer)
if len( find(g==0) ) == 0:
    print 'Filled buffer!'
else:
    print 'counts per second: ', 1000.0/float(acquisition_time)*find(g!=0)[-1]
shutdown( device0 )


import ctypes
import time
from pylab import *
phlib = ctypes.windll.phlib

block_size = ctypes.c_long(32768)
histogram_channels = 65536
TTREADMAX = 131072   # 128K event records
ranges = 8
buffer = (ctypes.c_long*TTREADMAX)()
ctypes.cast( buffer, ctypes.POINTER( ctypes.c_long ) )

device0 = ctypes.c_int(0)
channel0 = ctypes.c_int(0)
channel1 = ctypes.c_int(1)

ZeroCross0 = ctypes.c_long(9)  # in mV, for laser reference (not APD)
Discr0 = ctypes.c_long(15)     # in mV, for laser reference (not APD)
ZeroCross1 = ctypes.c_long(10) # in mV
Discr1 = ctypes.c_long(50)     # in mV

sync_divider = 8
SyncDivider = ctypes.c_long(sync_divider) # 1 is "None"

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

if phlib.PH_SetCFDLevel( device0, ctypes.c_long(0), Discr0 ) < 0: shutdown( device0, normal_operation=False )
if phlib.PH_SetCFDZeroCross( device0, ctypes.c_long(0), ZeroCross0 ) < 0: shutdown( device0, normal_operation=False )
if phlib.PH_SetCFDLevel( device0, ctypes.c_long(1), Discr1 ) < 0: shutdown( device0, normal_operation=False )
if phlib.PH_SetCFDZeroCross( device0, ctypes.c_long(1), ZeroCross1 ) < 0: shutdown( device0, normal_operation=False )

print 'Channel0 rate:', phlib.PH_GetCountRate( device0, channel0 )
print 'Channel1 rate:', phlib.PH_GetCountRate( device0, channel1 )

acquisition_time = 20 # acquisition time in ms. somehow answer only makes sense for acq. less than 150ms
num_acq = 100 # number of loops
cps = []
t0 = time.time()

def init_buffer():
    buffer = (ctypes.c_long*TTREADMAX)()
    ctypes.cast( buffer, ctypes.POINTER( ctypes.c_long ) )
    return buffer

def find_length( buffer ):
    """ find the length of the filled part of the buffer
    """
    lim = [0,TTREADMAX-1]
    ccc = -1
    while ccc==-1:
        if buffer[lim[0]+(lim[1]-lim[0])/2] == 0:
            if lim[1]-lim[0] == 1:
                ccc=lim[0]
            else:
                lim[1] = lim[0]+(lim[1]-lim[0])/2
        else:
            if lim[1]-lim[0] == 1:
                ccc=lim[0]
            else:
                lim[0] = lim[0]+(lim[1]-lim[0])/2
    return ccc

print 'Begin acquisition...'
for i in range(num_acq):
    if phlib.PH_StartMeas( device0, acquisition_time ) < 0: shutdown( device0, normal_operation=False )
    if acquisition_time > 10.0:
        # only add explicit delay if the acq. time is longer than, e.g., 20ms.
        # alternative: could just query PicoHarp to see when done using:
        # while not phlib.PH_CTCStatus( device0 ): pass
        # but it's faster to just add an explicit delay.
        time.sleep( (acquisition_time-10.0)/1000.0 )

    buffer = init_buffer()    
    if phlib.PH_TTReadData( device0, ctypes.byref(buffer), block_size ) < 0:
        shutdown( device0, normal_operation=False )

    cps.append( 1000.0/float(acquisition_time)*find_length(buffer) )
    
tf = time.time()
shutdown( device0 )
print 'acquisition time (ms):', acquisition_time
print 'additional processing time per acquisition (ms):', 1000*(tf-t0)/num_acq - acquisition_time
print 'cps:', cps

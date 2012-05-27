#!/usr/bin/env python
# I stole this from the following url and customized it to motion control. -- KJR 21Aug2010
# it's now meant as a stand-alone module to run within a child DAEMON thread and monitor the joystick.
#
# http://principialabs.com/joystick-control-of-a-servo/
# created 19 December 2007
# copyleft 2007 Brian D. Wendt
# http://principialabs.com/

import pygame
import time
from wx.lib.pubsub import Publisher


# control piezos at the start; trigger button will toggle between the two
piezos = 'piezos'
motors = 'motors'
motors_or_piezos = piezos

min_motor_step = 0.001 # mm
max_motor_step = 0.02   # mm
min_piezo_step = 0.05  # microns
max_piezo_step = 2.0   # microns
joystick_threshold = 0.15 # minimum joystick movement needed to trigger motion

# associate buttons: (take this value and add one to get the number actually printed on the joystick)
toggle_motors_piezos_button = 0
center_piezos_button = 1
focusing_button = 2
stop_button = 3
piezos_button = 4
WinSpecFocus_button = 7
CameraFocus_button = 8
toggle_coarse_fine_button = 9
toggle_wobble_button = 666 # just turn this off! 10

fine_control = True # this will only affect motors, not piezos.
focusing = False

def calc_stepsize( Z, motors_or_piezos, fine_control ):
    """ throttle position sets the step size... algorithm will likely need fine tuning """
    Z += 1.0 # this makes the minimum value 0.0 rather than -1
    if motors_or_piezos == motors:
        if fine_control:
            return Z*max_motor_step + min_motor_step
        else:
            return Z*max_motor_step*10 + min_motor_step
    else:
        return Z*max_piezo_step + min_piezo_step
    
def center_piezos( positioners ):
    piezoX = positioners['piezoX']
    piezoY = positioners['piezoY']
    if piezoX is not None:
        p = piezoX['control']
        p.SetPositionSmooth( position=p.min_position + (p.max_position - p.min_position)/2.0, step=0.25 )
    
    if piezoY is not None:
        p = piezoY['control']
        p.SetPositionSmooth( position=p.min_position + (p.max_position - p.min_position)/2.0, step=0.25 )
    
def get_joystick_position( joystick ):
    """ all three of these values should be in the range -1 to 1 """
    return dict( X=joystick.get_axis(0), Y=-joystick.get_axis(1), Z=-joystick.get_axis(2) )

def init_autoit():
    import os

    # Import the Win32 COM client
    try:
        import win32com.client
    except ImportError:
        raise ImportError, 'This program requires the pywin32 extensions for Python. See http://starship.python.net/crew/mhammond/win32/'
    
    import pywintypes # to handle COM errors.
    
    # Import AutoIT (first try)
    autoit = None
    try:
        autoit = win32com.client.Dispatch("AutoItX3.Control")
    except pywintypes.com_error:
        # If can't instanciate, try to register COM control again:
        os.system("regsvr32 /s AutoItX3.dll")
       
    # Import AutoIT (second try if necessary)
    if not autoit:
        try:
            autoit = win32com.client.Dispatch("AutoItX3.Control")
        except pywintypes.com_error:
            raise ImportError("Could not instanciate AutoIT COM module. Is AutoIT installed?")
       
    if not autoit:
        print "Could not instantiate AutoIT COM module."
        quit()
    
    return autoit

    
def toggle_fine_coarse_control():
    global fine_control
    if fine_control == True:
        fine_control = False
    else:
        fine_control = True

    print 'changing control to fine (T/F):', fine_control


def toggle_motor_piezo_control():
    global motors_or_piezos
    if motors_or_piezos == piezos:
        motors_or_piezos = motors
    else:
        motors_or_piezos = piezos


def update_position( positioners, xyz ):
    global fine_control
    global motors_or_piezos
    global focusing
    
    motorX = positioners['motorX']
    motorY = positioners['motorY']
    #motorZ = positioners['motorZ']

    piezoX = positioners['piezoX']
    piezoY = positioners['piezoY']
    piezoZ = positioners['piezoZ']
           
    stepsize = calc_stepsize( xyz['Z'], motors_or_piezos, fine_control )
    net_joy_X = xyz['X'] - joystick_threshold if xyz['X']>0 else xyz['X'] + joystick_threshold
    net_joy_Y = xyz['Y'] - joystick_threshold if xyz['Y']>0 else xyz['Y'] + joystick_threshold
    
    """ Use the current position of the joystick to step the motors. stepsize is set by throttle.""" 
    if motors_or_piezos == motors and focusing == False:
        if motorX is not None and motorX['control'].MotorIsNotMoving() and abs(xyz['X'])>joystick_threshold:
            time.sleep(0.1) # this is an attempt to keep the motor from locking
            motorX['control'].StepUp( polarity=motorX['direction'], stepsize=stepsize*net_joy_X, wait=False )
        
        if motorY is not None and motorY['control'].MotorIsNotMoving() and abs(xyz['Y'])>joystick_threshold:
            time.sleep(0.1) # this is an attempt to keep the motor from locking
            motorY['control'].StepUp( polarity=motorY['direction'], stepsize=stepsize*net_joy_Y, wait=False )
            #print motorY['control'].GetStatusBits_Bits()
            
        Publisher().sendMessage("joystick-moved", 'motors')
            
    elif motors_or_piezos == piezos and focusing == False:
        if piezoX is not None and abs(xyz['X'])>joystick_threshold:
            piezoX['control'].StepUp( direction=piezoX['direction'], stepsize=stepsize*net_joy_X )
            
        if piezoY is not None and abs(xyz['Y'])>joystick_threshold:
            piezoY['control'].StepUp( direction=piezoY['direction'], stepsize=stepsize*net_joy_Y )
            
        if piezoX is not None or piezoY is not None:
            Publisher().sendMessage("joystick-moved", 'piezos')
            
    elif focusing:
        if piezoZ is not None:
            piezoZ['control'].StepUp( direction=piezoZ['direction'], stepsize=stepsize*xyz['Y'] )
            Publisher().sendMessage("joystick-moved", 'piezos')
            
        
        
def handle_joystick_button_down( event, positioners, wobbler, autoit ):
    global fine_control
    global motors_or_piezos

    if ( event.dict['button'] == toggle_motors_piezos_button ):
        toggle_motor_piezo_control()
        #print "Toggle piezo/motor control. Now controlling %s." % ( motors_or_piezos )

    if ( event.dict['button'] == center_piezos_button ):
        #print "Centering X and Y piezos to middle of their range."
        center_piezos( positioners )
        Publisher().sendMessage("joystick-moved", 'piezos')

    if ( event.dict['button'] == focusing_button ):
        #print "focusing..."
        global focusing
#        focusing = True
        pass
        
    if ( event.dict['button'] == stop_button ):
        #print "Stop motors immediately!"

        if positioners['motorX'] is not None:
            positioners['motorX']['control'].StopImmediate()
            
        if positioners['motorY'] is not None:
            positioners['motorY']['control'].StopImmediate()

        if positioners['motorZ'] is not None:
            positioners['motorZ']['control'].StopImmediate()
        
        # and set this control to motors:
        motors_or_piezos = motors

    if ( event.dict['button'] == piezos_button ):
        # set to control piezos
        motors_or_piezos = piezos

    if ( event.dict['button'] == WinSpecFocus_button ):
        # in default mode, this will match the window title from start (similar to WinSpec*)
        # see AutoIt Help program for more info
        autoit.WinActivate("WinSpec")
    
    if ( event.dict['button'] == CameraFocus_button ):
        autoit.WinActivate("uc480")
    
    if ( event.dict['button'] == toggle_wobble_button ):
        wobbler.wobbleToggle()

    if ( event.dict['button'] == toggle_coarse_fine_button ):
        toggle_fine_coarse_control()
        

def handle_joystick_button_up( event ):
    if ( event.dict['button'] == focusing_button ):
        #print "focusing done."
        global focusing
        focusing = False


# wait for joystick input
def monitor_joystick( app, positioners, joysticks ):

    # initialize autoit to enable toggling between WinSpec and camera windows:
    autoit = init_autoit()
    prev_position = dict( X=0.0, Y=0.0, Z=0.0 )
    while True:
        if pygame.event.peek([pygame.JOYAXISMOTION,pygame.JOYBUTTONDOWN,pygame.JOYBUTTONUP]):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    handle_joystick_button_down( event, app.positioners, app.wobbler, autoit )
                elif event.type == pygame.JOYBUTTONUP:
                    handle_joystick_button_up( event )
        
        
        num_active_sticks = 0
        for stick in joysticks:
            pos = get_joystick_position( stick )
            if abs( pos['X'] ) > joystick_threshold or abs( pos['Y'] )>joystick_threshold:
                position = pos
                num_active_sticks += 1
                
        if num_active_sticks == 0 or num_active_sticks > 1:
            # trying to use more than one joystick at once is confusing, so
            # we'll just not move anything until you can make up your mind and use only one.
            position = dict( X=0.0, Y=0.0, Z=0.0 )

        if abs(position['X'])>joystick_threshold or abs(position['Y'])>joystick_threshold:
            update_position( positioners, position )
            #print positioners['motorY']['control'].GetStatusBits_Bits()
            
        elif abs(prev_position['X'])> joystick_threshold or abs(prev_position['Y'])>joystick_threshold:
            Publisher().sendMessage("joystick-moved", 'motors')
            
            if abs(prev_position['X'])> joystick_threshold and positioners['motorX'] is not None:
                positioners['motorX']['control'].StopImmediate()
                #print positioners['motorX']['control'].GetStatusBits_Bits()
            if abs(prev_position['Y'])> joystick_threshold and positioners['motorY'] is not None:
                positioners['motorY']['control'].StopImmediate()
        
        prev_position = position
        
#            if( events.type == pygame.JOYAXISMOTION or events.type == pygame.JOYBUTTONDOWN ):
#                handleJoyEvent( event, positioners, joysticks )
        if app.wobbler.isWobbling():
            app.wobbler.wobbleIncrement()        

        time.sleep( 0.03 )


        
def StartControl( app, positioners ):
    # initialize pygame
    
    pygame.init()

    pygame.joystick.init()
    if True: # needed to work on lab/XP computer, haven't tested on Vista yet.
        import os
        os.environ['SDL_VIDEODRIVER'] = 'windib'
    pygame.display.init()
    if not pygame.joystick.get_count():
        print "Did not detect a joystick. Attach joystick and restart program for joystick control."
        quit()
    print "\n%d joystick(s) detected." % pygame.joystick.get_count()

    # allow multiple joysticks
    joysticks = []

    for i in range(pygame.joystick.get_count()):
        myjoy = pygame.joystick.Joystick(i)
        myjoy.init()
        joysticks.append(myjoy)
        #print "Joystick %d: " % (i) + joy[i].get_name()
    #print "Press button 11 to quit.\n"
    print "Joystick controls %s by default.\n" % motors_or_piezos

    # run joystick listener loop
    monitor_joystick( app, positioners, joysticks )

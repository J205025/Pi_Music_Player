#!/usr/bin/env python3
import os
import RPi.GPIO as GPIO
import subprocess
import time
import glob
from threading import Thread
import threading
# Global variables with module-local scope (cannot export these dunders)
__process_running__ = False  
__max_list__ = 0
__return_code__ = None
__decimal__ = 0
__p__ = None
__dir__ = "/home/ubuntu/music/media/"
__pty_master__ = None
__pty_slave__ = None
__playing__ = False
__mp3_list__ = None
__mp3_list__z__ = None
__index__ = 4
__timer_running__ = False
__Number4d__ = [ 0, 0, 0, 0 ]
__t__ = None
class AudioEngineUnavailable(Exception):
    pass 

# Start a new process to run mpg123 to play the specified sound file / list

def play_file(mp3_file, pty):
    try:
        command = ['mpg123', '-C', '-q', mp3_file]
        p = subprocess.Popen( command, 
#                             ['mpg123', # The program to launch in the subprocess
#                             '-C',     # Enable commands to be read from stdin
#                             '-q',     # Be quiet
#                              mp3_file],
                              stdin=pty, # Pipe input via bytes
                              stdout=None,   
                              stderr=None
                              )
        return p
    except FileNotFoundError as e:
        raise AudioEngineUnavailable(f'AudioEngineUnavailable: {e}')

def play_list(mp3_list, pty):
    try:
        command = ['mpg123', '-C', '-q','-z'] + mp3_list
        p = subprocess.Popen( command,
#                              ['mpg123', # The program to launch in the subprocess
#                              '-C',     # Enable commands to be read from stdin
#                              '-q',     # Be quiet
#                              '-z']     # 
#                              +mp3_list,
                              stdin=pty,  # Pipe input via bytes
                              stdout=None,   
                              stderr=None
                              )
        return p
    except FileNotFoundError as e:
        raise AudioEngineUnavailable(f'AudioEngineUnavailable: {e}')

# Monitor a subprocess, record its state in global variables
# This function is intended to run in its own thread
def process_monitor(p):
    """
    Monitor a subprocess, recording state in global variables
    Parameter:
    p : subprocess.Popen
        The subprocess to monitor
    """
    global __process_running__
    global __return_code__
    # Indicate that the process is running at the start, it
    # should be
    __process_running__ = True

    # When a process exits, p.poll() returns the code it set upon
    # completion
    __return_code__ = p.poll()

    # See whether the process has already exited. This will cause a
    # value (i.e. not None) to return from p.poll()
    if __return_code__ == None:
        # Wait for the process to complete, get its return code directly
        # from the wait() call (i.e. do not use p.poll())
        __return_code__ = p.wait()

    # When we get here, the process has exited and set a return code
    __process_running__ = False
    
def is_running():
    """
    For readability-return value of a dunder-named global variable
    """
    return __process_running__

def get_return_code():
    """
    For readability-return value of a dunder-named global variable
    """
    return __return_code__
    
def pressedNumber(channel):
    if(channel ==12):
        Number = 1
        print("1 Pressed")
    elif(channel ==16):
        Number = 2
        print("2 Pressed")
    elif(channel ==18):
        Number = 3
        print("3 Pressed")
    elif(channel ==11):
        Number = 4
        print("4 Pressed")
    elif(channel ==13):
        Number = 5
        print("5 Pressed")
    elif(channel ==15):
        Number = 6
        print("6 Pressed")
    return Number
def playSelected():
    global __p__
    global __playing__
    global __dir__
    global __mp3_list__
    global __process_running__
    global __pty_master__
    global __Number4d__
    global __decimal__
    global __index__
    if (__process_running__ == True):
        __p__.terminate() 
        time.sleep(0.1)
    file = __dir__ + __mp3_list__[__decimal__]
    print("play:"+file)
    __p__ = play_file(file, __pty_master__)
    monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
    monitor_thread.start()
    __playing__ = True
    __timer_running__ = False
    __Number4d__ = [0, 0, 0, 0]
    __index__ = 4

def convert(list):
    res = sum(d * 10**i for i, d in enumerate(list[::-1]))
    return(res)

def handleSelectSong(channel):
    global __decimal__
    global __p__
    global __max_list__
    global __dir__
    global __playing__
    global __index__
    global __Number4d__
    global __timer_running__
    global __t__
    if (__timer_running__ == True):
        __t__.cancel()
    Number = pressedNumber(channel)
    __index__ = __index__ - 1
    print("__index__:"+ str(__index__))
    if(__index__ < 0):
        __index__ = 3 
    __Number4d__[0] = __Number4d__[1] 
    __Number4d__[1] = __Number4d__[2] 
    __Number4d__[2] = __Number4d__[3] 
    __Number4d__[3] = Number 
    print("__Number__4d[]:" + str(__Number4d__))
    res = convert(__Number4d__)
    print("res:"+str(res))
    __decimal__ = ( res % __max_list__) - 1
    if (__decimal__ == -1 ):
       __decimal__ = __decimal__ + __max_list__
    print("the NO."+str(__decimal__ + 1)+" mp3 will be played")
    __t__ = threading.Timer(3, playSelected)
    __t__.start()
    __timer_running__ = True

def handleButtonNext(channel):
    global __decimal__
    global __p__
    global __max_list__
    global __mp3_list__
    global __dir__
    global __process_running__
    global __playing__
    if (__playing__ == True):
        __p__.terminate()   
        __decimal__ = __decimal__ + 1
        if (__decimal__  > (__max_list__ -1 )):
            __decimal__= 0 
        else:
            pass
        file = __dir__ + __mp3_list__[__decimal__]
        print("play:"+file)
        __p__ = play_file(file, __pty_master__)
        time.sleep(0.1)
        monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
        monitor_thread.start()
    else:
        pass

def handleButtonPre(channel):
    global __decimal__
    global __p__
    global __max_liist__
    global __mp3_list__
    global __dir__
    global __process_running__
    global __playing__
    if (__playing__ == True):
        __p__.terminate()
        __decimal__ = __decimal__ - 1
        time.sleep(0.1) 
        if (__decimal__ < 0):
           __decimal__= __max_list__ - 1
        else:
            pass
        file = __dir__ + __mp3_list__[__decimal__]
        print("play:"+file)
        __p__ = play_file(file, __pty_master__)
        time.sleep(0.1)
        monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
        monitor_thread.start()
    else:
        pass
def handleButtonPlayPause(channel):
    global __decimal__
    global __playing__
    global __process_running__
    global __p__
    global __mp3_list__
    time.sleep(0.1)
    if (__process_running__ == True):
        time.sleep(0.1)
        os.write(__pty_slave__, b's')
        __playing__ = not __playing__
        #__p__.stdin.write(b's')
        #__p__.stdin.flush()
    else:
        file = __dir__ + __mp3_list__[__decimal__]
        __p__ = play_file(file, __pty_master__)
        print("play:"+file)
        time.sleep(0.1)
        monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
        monitor_thread.start()
        __playing__ = True
def handleButtonMute(channel):
    global __playing__
    if (__playing__ == True):
        os.write(__pty_slave__, b'u')
    else:
       pass

def handleButtonBack(channel):
    global __playing__
    if (__playing__ == True):
        os.write(__pty_slave__, b'b')
    else:
        pass
    #__p__.stdin.write(b'b')
    #__p__.stdin.flush()

def get_files(root):
    files = []
    def scan_dir(dir):
        for f in os.listdir(dir):
            #f = os.path.join(dir, f)
            if os.path.isdir(f):
                scan_dir(f)
            elif os.path.splitext(f)[1] == ".mp3":
                files.append(f)
    scan_dir(root)
    return files

def continuePlaying():
    global __playing__
    global __process_running__
    global __pty_master__
    global __mp3_list_z__ 
    global __p__
    if (( __process_running__ == False ) and (__playing__ == True )):
        print("******************************-")
        print("running:"+str(__process_running__))
        print("playing:"+str(__playing__))
        __p__ = play_list(__mp3_list_z__, __pty_master__)
        time.sleep(0.1)
        monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
        monitor_thread.start()
        __playing__ = True
#        print("playing:"+str(__playing__))
        threading.Timer( 5 , continuePlaying ).start()
    else:
#        print("playing:"+str(__playing__))
        threading.Timer( 5 , continuePlaying ).start()
        
if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
   # gpio binary  
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   # PLAY NEXT PRE BACK 
    GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    threading.Timer( 3 , continuePlaying ).start()
#file list Method 1
#    mp3_list = [ f for f in os.listdir('/home/ubuntu/music/media/.') if f[-4:] == '.mp3' ]
#    mp3_list.sort(key=lambda x:int(x[:-4]))
#file list Methos 2
    __mp3_list_z__ = glob.glob(r'/home/ubuntu/music/media/*.mp3')
#    __mp3_list_z__.sort(key=lambda x:int(x[25:-4]))
#file list Method 3
    __mp3_list__ = get_files(__dir__)
#    __mp3_list__.sort(key=lambda x:int(x[:-4]))

    if not (len(__mp3_list__) > 0):
        print ("No mp3 files found!")
    print ('--- Available mp3 files ---')
    print(__mp3_list__)
    print(__mp3_list_z__)
    __max_list__  = len(__mp3_list__) 
    
   # add openpty
    __pty_master__, __pty_slave__ = os.openpty()
  
   # We need a way to tell if a song is already playing. Start a 
   # thread that tells if the process is running and that sets
   # a global flag with the process running status.
   #    monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
   #    monitor_thread.start()
   #    time.sleep(0.1)
   #    os.write(__pty_slave__, b's')    
    __playing__ = False
    print ('--- Press button #play to start playing mp3 ---')

    GPIO.add_event_detect(12, GPIO.FALLING, callback=handleSelectSong, bouncetime=500)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=handleSelectSong, bouncetime=500)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=handleSelectSong, bouncetime=500)
    GPIO.add_event_detect(11, GPIO.FALLING, callback=handleSelectSong, bouncetime=500)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=handleSelectSong, bouncetime=500)
    GPIO.add_event_detect(15, GPIO.FALLING, callback=handleSelectSong, bouncetime=500)

    GPIO.add_event_detect(29, GPIO.FALLING, callback=handleButtonPlayPause, bouncetime=500)
    GPIO.add_event_detect(31, GPIO.FALLING, callback=handleButtonNext, bouncetime=500)
    GPIO.add_event_detect(33, GPIO.FALLING, callback=handleButtonPre, bouncetime=500)
    GPIO.add_event_detect(35, GPIO.FALLING, callback=handleButtonBack, bouncetime=500)
    GPIO.add_event_detect(37, GPIO.FALLING, callback=handleButtonMute, bouncetime=500)
   
    while True:
       time.sleep(0.1)
       pass


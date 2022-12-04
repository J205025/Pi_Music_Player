#!/usr/bin/env python3
import os
import RPi.GPIO as GPIO
import subprocess
import time
import glob
from threading import Thread

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

class AudioEngineUnavailable(Exception):
    pass 

# Start a new process to run mpg123 to play the specified sound file / list

def play_file(mp3_file, pty):
    try:
        command = ['mpg123', '-C', '-q', mp3_file]
        p = subprocess.Popen( command, 
#                             'mpg123', # The program to launch in the subprocess
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

def play_list(mp3_list):
    try:
        p = subprocess.Popen(['mpg123', # The program to launch in the subprocess
                              '-C',     # Enable commands to be read from stdin
                              '-q',     # Be quiet
                              '-z']     # 
                              +mp3_list,
                              stdin=subprocess.PIPE, # Pipe input via bytes
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
    
def handleFile(channel):
    global __decimal__
    global __p__
    global __max_list__
    global __dir__
    D0 = GPIO.input(12)
    D1 = GPIO.input(16)
    D2 = GPIO.input(18)
    D3 = GPIO.input(11)
    D4 = GPIO.input(13)
    D5 = GPIO.input(15)
    print('\n')
    print('D0= '+str(D0))
    print('D1= '+str(D1))
    print('D2= '+str(D2))
    print('D3= '+str(D3))
    print('D4= '+str(D4))
    print('D5= '+str(D5))
    __decimal__ = D0+(D1*2)+(D2*4)+(D3*8)+(D4*16)+(D5*32)
    __decimal__ = __decimal__ % __max_list__
    __p__.terminate() 
    time.sleep(0.3)
    file = __dir__ + mp3_list[__decimal__]
    print("play:"+file)
    __p__ = play_file(file, __pty_master__)

def handleButtonNext(channel):
    global __decimal__
    global __p__
    global __max_list__
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
 
        file = __dir__ + mp3_list[__decimal__]
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
        file = __dir__ + mp3_list[__decimal__]
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
    time.sleep(0.1)
    if (__process_running__ == True):
        time.sleep(0.1)
        os.write(__pty_slave__, b's')
        __playing__ = not __playing__
        #__p__.stdin.write(b's')
        #__p__.stdin.flush()
    else:
        file = __dir__ + mp3_list[__decimal__]
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
    #__p__.stdin.write(b'u')
    #__p__.stdin.flush()

def handleButtonBack(channel):
    global __playing__
    if (__playing__ == True):
        os.write(__pty_slave__, b'b')
    else:
        pass
    #__p__.stdin.write(b'b')
    #__p__.stdin.flush()
    #time.sleep(0.1)

def handlePlayNext(channel):
    global __decimal__
    global __p__
    global __max_list__
    global __dir__
    global __pty__
    global __process_running__
    if (__process_running__ == True):
        __p__.terminate()   
        time.sleep(0.1)
        __decimal__ = __decimal__ + 1
        if (__decimal__  > __max_list__):
            __decimal__=(__decimal__ % __max_list__)
        else:
            pass
        file = __dir__ + mp3_list[__decimal__]
        __p__ = play_file(file, __pty_master__)
    else:
        pass

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
#file list Method 1
#    mp3_list = [ f for f in os.listdir('/home/ubuntu/music/media/.') if f[-4:] == '.mp3' ]
#    mp3_list.sort(key=lambda x:int(x[:-4]))
#file list Methos 2
#    mp3_list = glob.glob(r'/home/ubuntu/music/media/*.mp3')
#    mp3_list.sort(key=lambda x:int(x[25:-4]))
#file list Method 3
    mp3_list = get_files(__dir__)
#    mp3_list.sort(key=lambda x:int(x[:-4]))

    if not (len(mp3_list) > 0):
        print ("No mp3 files found!")
    print ('--- Available mp3 files ---')
    print(mp3_list)
    __max_list__  = len(mp3_list) 
    
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

    GPIO.add_event_detect(12, GPIO.FALLING, callback=handleFile, bouncetime=500)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=handleFile, bouncetime=500)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=handleFile, bouncetime=500)
    GPIO.add_event_detect(11, GPIO.FALLING, callback=handleFile, bouncetime=500)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=handleFile, bouncetime=500)
    GPIO.add_event_detect(15, GPIO.FALLING, callback=handleFile, bouncetime=500)

    GPIO.add_event_detect(29, GPIO.FALLING, callback=handleButtonPlayPause, bouncetime=500)
    GPIO.add_event_detect(31, GPIO.FALLING, callback=handleButtonNext, bouncetime=500)
    GPIO.add_event_detect(33, GPIO.FALLING, callback=handleButtonPre, bouncetime=500)
    GPIO.add_event_detect(35, GPIO.FALLING, callback=handleButtonBack, bouncetime=500)
    GPIO.add_event_detect(37, GPIO.FALLING, callback=handleButtonMute, bouncetime=500)
    
#    t = threading.Timer(1, handlePlayNext) 
    
    while True:
       time.sleep(0.1)
       pass


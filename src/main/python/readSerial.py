#!/usr/bin/env python

import serial
import os.path
import time
import gphoto2 as gp
#import gphoto2cffi as gp
import sdnotify
import functions
from fractions import Fraction


#btSerial = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=0.5)

componentDictionnary = {
        'PWR': 'POWEROFF',
        'READSETTINGS':'READSETTINGS',
        'SHOOT':'SHOOT',
        'EV' : 'BRACKET_SIZE',
        'SP' : 'SPEED',
}

COMMAND_SEPARATOR = '#'

BT_FILE="/dev/rfcomm0"

SYS_NOTIFIER = sdnotify.SystemdNotifier()

def parseBluetoothInput( content ) :
    # Get list of commands
    cmds = content.split(COMMAND_SEPARATOR)
    print cmds
    lastCmd = cmds[-1]
    if(lastCmd == '') :
        lastCmd = cmds[-2]
    return lastCmd

def shoot ( btSerial ) : 
    sendMessage(btSerial, "Take a picture...")
    camera = getCamera()
    initCameraConfiguration(camera)
    
    sendMessage(btSerial, 'Capturing image')
    
    takePhoto(camera)

    sendMessage(btSerial, 'Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
    
    releaseCamera(camera)
    return

def readEV ( content ) :
    value = Fraction(int(content.split('EV')[-1]), 3) 
    print "EV : " + str(value)
    return value

def sendMessage ( btSerial, content ) : 
    btSerial.write( content ) 
    return

def readFile () :
    etcPasswd = open("/etc/passwd", "r")
    print etcPasswd.read() 

def dispatch ( btSerial, command ) :
    if( command.startswith('EV') ) :
        value = readEV( command ) 
        sendMessage ( btSerial, "*A" + str(value) + "*A" )
    elif (command.startswith('SHOOT') ) :
        shoot( btSerial ) 
    else : 
        return 

def action ( btSerial ) : 
    rcv = btSerial.read(512)
    if rcv:
        cmd = parseBluetoothInput(rcv) 
        print "Last command:" + cmd
        dispatch ( btSerial, cmd )
    return

def main() :

    SYS_NOTIFIER.notify("READY=1")
    isBtFileExists = False
    btSerial = None
    while True:
        if ( not isBtFileExists ) :
            if ( os.path.exists(BT_FILE) ) : 
                # Loadfile
                btSerial = serial.Serial(BT_FILE, baudrate=9600, timeout=0.5)
                print "Connection established"
                isBtFileExists = True
                action ( btSerial ) 
            else :
                btSerial = None
                isBtFileExists = False
                print "Wait 5s for BT connexion"
                time.sleep( 5 )
        else :
            if ( os.path.exists(BT_FILE) ) : 
                #print "Connection already established"
                action ( btSerial ) 
                isBtFileExists = True 
            else :
                btSerial = None
                isBtFileExists = False
                print "Wait 5s for BT connexion"
                time.sleep( 5 ) 
        
        SYS_NOTIFIER.notify("WATCHDOG=1")
                

main() 
#readFile()

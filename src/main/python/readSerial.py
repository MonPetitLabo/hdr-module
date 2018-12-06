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

photoParameter = {
    'NB' : 1,
    'EV' : 1,
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
    camera = functions.getCamera()
    functions.initCameraConfiguration(camera)
    
    sendMessage(btSerial, 'Capturing image')
    
    if (photoParameter['NB'] == 1) :
        functions.takePhoto(camera)
    else :
        functions.takePhotoHdr(camera, photoParameter['NB'], photoParameter['EV'])
    
    functions.releaseCamera(camera)
    return

def readEV ( content ) :
    logicalValue = int(content.split('EV')[-1])
    realvalue = Fraction(logicalValue, 3) 
    print "EV : " + str(realvalue)
    photoParameter['EV'] = logicalValue
    return realvalue

def readNbPictureToTake ( content ) :
    value = (int(content.split('NB')[-1]) * 2) + 1
    print "NB : " + str(value)
    photoParameter['NB'] = value
    return value

def getReadableSettings ( ) :
    camera = functions.getCamera()
    message = "D:" + functions.getValueOfSelectedParameter(camera, functions.CAPTURE_TARGET) + "\n"
    message = message + "S:" + functions.getValueOfSelectedParameter(camera, functions.SHUTTER_SPEED) + "\n"
    message = message + "A:" + functions.getValueOfSelectedParameter(camera, functions.APERTURE) + "\n"
    message = message + "ISO:" + functions.getValueOfSelectedParameter(camera, functions.ISO) + "\n"
    
    functions.releaseCamera(camera)
    return message

def sendMessage ( btSerial, content ) : 
    btSerial.write( content ) 
    return

def readFile () :
    etcPasswd = open("/etc/passwd", "r")
    print etcPasswd.read() 

def dispatch ( btSerial, command ) :
    if( command.startswith('EV') ) :
        readEV( command ) 
    elif (command.startswith('NB') ) :
        readNbPictureToTake( command ) 
    elif (command.startswith('SHOOT') ) :
        shoot( btSerial ) 
    else : 
        return 

def refreshSettings ( btSerial ) :
    settingsMessage = "*A%s*N%s*P%s*" % (Fraction(photoParameter['EV'], 3), photoParameter['NB'], getReadableSettings())
    sendMessage( btSerial, settingsMessage )    

def action ( btSerial ) : 
    rcv = btSerial.read(512)
    if rcv:
        cmd = parseBluetoothInput(rcv) 
        print "Last command:" + cmd
        dispatch ( btSerial, cmd )
    refreshSettings ( btSerial )
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

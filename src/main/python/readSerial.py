#!/usr/bin/env python

import serial
import os.path
import time
import gphoto2 as gp
#import gphoto2cffi as gp
import sdnotify
import functions
import subprocess
from fractions import Fraction


#btSerial = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=0.5)

componentDictionnary = {
        'PWR': 'POWEROFF',
        'READSETTINGS':'READSETTINGS',
        'SHOOT':'SHOOT',
        'EV' : 'BRACKET_SIZE',
        'SP' : 'SPEED',
        'BSP': 'SPEED_BULB',
}

photoParameter = {
    'NB' : 0,
    'EV' : 1,
    'BSP' : -1,
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
    
    if (photoParameter['BSP'] > -1) : 
        functions.takeLongPhoto(camera) 
    elif (photoParameter['NB'] == 1) :
        functions.takePhoto(camera)
    else :
        functions.takePhotoHdr(camera, photoParameter['NB'], photoParameter['EV'])
    
    functions.releaseCamera(camera)
    sendMessage(btSerial, "Done ! ") 
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
    message = message + "S:" + functions.getValueOfSelectedParameter(camera, functions.SHUTTER_SPEED)
    if ( photoParameter['BSP'] > -1 ) :
        message = message + "("+ photoParameter['BSP']  + ")"
    message = message + "\n"
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

def updateSpeed( btSerial, command ) :
    value = command.split('SP')[-1]
    camera = functions.getCamera()
    functions.initCameraConfiguration(camera) 
    if (functions.cameraConfiguration[functions.SHUTTER_SPEED].has_key(value)) :
        index = functions.cameraConfiguration[functions.SHUTTER_SPEED][value]
        functions.setPropertyTo(camera, functions.SHUTTER_SPEED, index)
        photoParameter['BSP'] = -1
    else :
        sendMessage(btSerial, "Unexpected value for speed : " + value + "\n")
    
    functions.releaseCamera(camera)
    return

def updateSpeedBulb( btSerial, command ) :
    value = command.split('BSP')[-1]
    updateSpeed(btSerial, 'SPbulb')
    photoParameter['BSP'] = value
    return

def updateAperture(btSerial, command) : 
    value = command.split('AP')[-1]
    camera = functions.getCamera()
    functions.initCameraConfiguration(camera)
    if(functions.cameraConfiguration[functions.APERTURE].has_key(value)) : 
        index = functions.cameraConfiguration[functions.APERTURE][value]
        functions.setPropertyTo(camera, functions.APERTURE, index)
    else : 
        sendMessage(btSerial, "Unexpected value for aperture : " + value + "\n")
    return

def updateIso(btSerial, command):
    value = command.split('ISO')[-1]
    camera = functions.getCamera()
    functions.initCameraConfiguration(camera)
    if(functions.cameraConfiguration[functions.ISO].has_key(value)) : 
        index = functions.cameraConfiguration[functions.ISO][value]
        functions.setPropertyTo(camera, functions.ISO, index)
    else : 
        sendMessage(btSerial, "Unexpected value for ISO : " + value + "\n")
    return

def poweroff() :
    cmdCommand = "sudo poweroff"
    process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
    return


def dispatch ( btSerial, command ) :
    if( command.startswith('EV') ) :
        readEV( command ) 
    elif (command.startswith('NB') ) :
        readNbPictureToTake( command ) 
    elif (command.startswith('SHOOT') ) :
        shoot( btSerial ) 
    elif (command.startswith('SP') ) :
        updateSpeed( btSerial, command )
    elif (command.startswith('BSP') ) :
        updateSpeedBulb( btSerial, command )
    elif (command.startswith('AP') ) :
        updateAperture( btSerial, command )
    elif (command.startswith('ISO') ) :
        updateIso( btSerial, command )
    elif (command.startswith('PWR')):
        poweroff()
    elif (command.startswith('READSETTINGS')) :
        refreshSettings(btSerial)
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

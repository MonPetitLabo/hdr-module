import serial
from fractions import Fraction

btSerial = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=0.5)

componentDictionnary = {
        'PWR': 'POWEROFF',
        'READSETTINGS':'READSETTINGS',
        'SHOOT':'SHOOT',
        'EV' : 'BRACKET_SIZE',
        'SP' : 'SPEED',
}

COMMAND_SEPARATOR = '#'

def parseBluetoothInput( content ) :
    # Get list of commands
    cmds = content.split(COMMAND_SEPARATOR)
    print cmds
    lastCmd = cmds[-1]
    if(lastCmd == '') :
        lastCmd = cmds[-2]
    return lastCmd



def readEV ( content ) :
    value = Fraction(int(content.split('EV')[-1]), 3) 
    print "EV : " + str(value)
    sendMessage ("*A" + str(value) + "*A")
    return 

def sendMessage ( content ) : 
    btSerial.write( content ) 
    return

def readFile () :
    etcPasswd = open("/etc/passwd", "r")
    print etcPasswd.read() 

def dispatch ( command ) :
    if( command.startswith('EV') ) :
        readEV( command ) 
    else : 
        return 

def main() :
    while True:
        rcv = btSerial.read(512)
        if rcv:
            cmd = parseBluetoothInput(rcv) 
            print "Last command:" + cmd
            dispatch (cmd) 


main() 
#readFile()

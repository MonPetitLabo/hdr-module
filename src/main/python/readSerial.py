import serial

btSerial = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=0.5)

def parseBluetoothInput( content ) :
    print content
    return content

def main() :
    while True:
        rcv = btSerial.read(512)
        rcv = parseBluetoothInput(rcv)
        if rcv:
            btSerial.write("OK!")
            print(rcv)


main() 
import serial
import subprocess
import time

# Thermocube accepts max 3 commands per second
# Refresh rate of thermocube status bits is 1Hz 

class ThermocubeInterface():
    def __init__(self, usbPort=None):
        self.ser = ThermocubeSerialLink(usbPort)

    def __del__(self):
        del self.ser

    # Starts/stops temperature control on the chiller
    def SetChillerStatus(self, chillerOn):
        time.sleep(0.5)
        command = self.__BinToAscii('1' + str(int(chillerOn)) + '000000')
        temperatureMeasured = self.ser.ExecuteCommand(command)

    # Sets the temperature in units of 0.1F
    def SetTemperature(self, temperatureInFahrenheit, chillerOn):
        time.sleep(0.5)
        if temperatureInFahrenheit < 0.
            raise InvalidArgumentException
        temperatureSettingLsb = int(temperatureInFahrenheit * 10.)%256
        temperatureSettingMsb = int(temperatureInFahrenheit * 10.)/256
        command = self.__BinToAscii('1' + str(int(chillerOn)) + '100001')
        data    = self.__IntToAscii(temperatureSettingMsb) + self.__IntToAscii(temperatureSettingLsb)
        self.ser.ExecuteCommand(data + command)

    # Gets the temperature setting in units of 0.1F
    def GetTemperatureSetting(self, chillerOn):
        time.sleep(0.5)
        command = self.__BinToAscii('1' + str(int(chillerOn)) + '000001')
        temperatureSetting = self.ser.ExecuteCommand(command, 2)
        temperatureInFahrenheit = (ord(temperatureSetting[1])*256 + ord(temperatureSetting[0]))/10.
        return temperatureInFahrenheit

    # Gets the temperature as measured at the chiller output
    def GetTemperatureMeasured(self, chillerOn):
        time.sleep(0.5)
        command = self.__BinToAscii('1' + str(int(chillerOn)) + '001001')
        temperatureMeasured = self.ser.ExecuteCommand(command, 2)
        temperatureInFahrenheit = (ord(temperatureMeasured[1])*256 + ord(temperatureMeasured[0]))/10.
        return temperatureInFahrenheit

    # Gets all chiller fault bits
    def GetChillerStatus(self, chillerOn):
        time.sleep(0.5)
        command = self.__BinToAscii('1' + str(int(chillerOn)) + '001000')
        status = self.ser.ExecuteCommand(command, 1) 
        return status

    # Gets a human readable description of the chiller status
    def GetDecodedChillerStatus(self, chillerOn):
        time.sleep(0.5)
        status = GetChillerStatus(chillerOn)
        if (ord(status) == 0):
            print "Thermocube is working fine"
            return
        else:
            print "The following issues were detected on thermocube:"
        if (ord(status) & 0x1):
            print "- Tank level is low"
        if (ord(status) & 0x2):
            print "- Fan failed"
        if (ord(status) & 0x8):
            print "- Pump failed"
        if (ord(status) & 0x10):
            print "- RTD is open"
        if (ord(status) & 0x20):
            print "- RTD is shorted"

    # Returns control of the chiller to chiller local interface (all the other commands take control of the chiller instead)
    def SetRemoteOff(self, chillerOn):
        time.sleep(0.5)
        command = self.__BinToAscii('0' + str(int(chillerOn)) + '000000')
        temperatureMeasured = self.ser.ExecuteCommand(command)

    def __BinToAscii(binString):
        return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(binString)]*8))

    def __IntToAscii(integer):
        return str(chr(integer)) 

class ThermocubeSerialLink():
    def __init__(self, usbPort=None):
        if usbPort == None:
           usbPort = self.__GetDevicePath()
        self.ser = serial.Serial(
            port=usbPort,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)
        self.timeout = 1. # [s]

    def __del__(self):
        self.ser.close()

    # Sends a command to power supply and collect the incoming data, strip and check ack ("OK" substring must be present)
    def ExecuteCommand(self, command, readbufferDepth = 0):
        self.ser.write(command) 
        readBuffer = self.ReadBuffer(readbufferDepth)
        return readBuffer

    # Reads a given number of bytes (bufferDepth) from the serial interface
    def ReadBuffer(self, readbufferDepth): 
        int(readbufferDepth)
        t = 0.
        while t < self.timeout:
            numBytesAvailable = self.ser.inWaiting()
            if numBytesAvailable == readbufferDepth:
                return self.ser.read(readbufferDepth)
            time.sleep(0.02)
            t = t + 0.02
        raise TimeoutException

    def __GetDevicePath(self):
        return "/dev/" + self.__GetDeviceUsbPort()

    def __GetDeviceUsbPort(self):
        listOfDevices = self.__GetListOfDevices()
        if len(listOfDevices) == 0:
            print "Power supply not connected to the computer, connect and retry"
            sys.exit()
        if len(listOfDevices) > 1:
            print "More than one device of the required type, disconnect one of them or switch to manual USB configuration"
            sys.exit()

        return listOfDevices[0]

    def __GetListOfDevices(self): # To check
        listOfUsbDevices = subprocess.Popen("find /sys/bus/usb/devices/usb*/ -name dev", shell = True, stdout=subprocess.PIPE)
        listOfDevices = []
        for path in listOfUsbDevices.stdout.readlines():
            path = path.split('\n')[0][0:-4]
            device = (subprocess.Popen("udevadm info -q name -p " + path, shell = True, stdout=subprocess.PIPE).stdout.readline()).split('\n')[0]
            model = subprocess.Popen("udevadm info -q property --export -p " + path + " | grep \"ID_MODEL=\'CP2102_USB_to_UART_Bridge_Controller\'\"", \
                                     shell = True, stdout=subprocess.PIPE).stdout.readline().split('\n')[0]
            if device.split('/')[0] == "bus" or not model:
               continue
            listOfDevices.append(device)
        return listOfDevices

# Typical errors
class InvalidArgumentException(Exception):
    pass

class TimeoutException(Exception):
    pass

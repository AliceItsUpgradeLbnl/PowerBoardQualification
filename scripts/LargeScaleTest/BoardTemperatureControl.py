from ThermocubeInterface import ThermocubeInterface

class PowerboardTemperatureControl(smartPlugId):
    def __init__(self):
        self.tcPower     = SmartPlugInterface(smartPlugId)
        self.tcInterface = TermocubeInterface()

    def StartChiller():
        self.tcPower.On()
        sleep(2)
        if ord(self.tcInterface.GetChillerStatus()):
            raise ChillerHasProblems
        self.tcInterface.SetTemperature(temperatureInFahrenheit = 20.0, chillerOn = True) 

    def StopChiller():
        self.tcInterface.SetChillerStatus(chillerOn = False)
        self.tcInterface.SetRemoteOff()
        self.tcPower.Off()
        sleep(2)

# Typical errors
class ChillerHasProblems(Exception):
    pass

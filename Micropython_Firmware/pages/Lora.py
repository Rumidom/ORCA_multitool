import Buttons
from Control import UserControl
import fontlib
import utime

class LoraMonitor(UserControl):
    def __init__(self,lcd,uart_,sx127x):
        self.lcd = lcd
        self.uart = uart_
        self.sx127x =sx127x
        self.PacketList = []
        self.PacketNum = 0
        self.PacketIndex = 0
        self.Pindex = 0
        self.scroll = 0
        self.MaxPacketsPerScreen = 4
        self.initTime = utime.ticks_ms()
        self.MaxCharsPerLine = 14
        self.AutoRoll = True
    def Ok_Func(self):
        pass
    
    def Left_Func(self):
        self.scroll = 0
        self.AutoRoll = False
        if self.PacketIndex > 0:
            self.PacketIndex -= 1
            if (self.PacketIndex == self.Pindex-1):
                self.Pindex -= 1
                
    def Right_Func(self):
        self.scroll = 0
        self.AutoRoll = False
        if self.PacketIndex < (len(self.PacketList)-1):
            self.PacketIndex += 1
            if self.PacketIndex > (self.MaxPacketsPerScreen-1)+self.Pindex:
                self.Pindex += 1
                
    def ESC_Func(self):
        return("ESCAPE")
    
    def DEL_Func(self):
        return("DELETE")
    
    def DrawLoraMonitor(self):
        self.lcd.fill(0)
        for i,packet in enumerate(self.PacketList[self.Pindex:self.Pindex+4]):
            icon = " "
            payload = packet[1]
            if packet[0] >= -40:
                icon = "k"
            elif packet[0] < -40 and packet[0] >-100:
                icon = "l"
            elif packet[0] <= -110:
                icon = "M"
            if (i == self.PacketIndex-self.Pindex):
                payload = packet[1][self.scroll:self.scroll+self.MaxCharsPerLine]
                if (utime.ticks_ms()-self.initTime > 500):
                    self.initTime = utime.ticks_ms()
                    self.scroll += 1
            if self.scroll > len(packet[1])-self.MaxCharsPerLine:
                self.scroll = 0
            j = i+self.Pindex
            Buttons.DrawIconIndexMenuOption(self.lcd,i,j,payload.decode(),icon=icon,posx=3,selected = (i == self.PacketIndex-self.Pindex))

        Buttons.DrawScrollBar(self.lcd,10,40,self.PacketIndex,self.PacketNum)
        self.lcd.show()

    def CallbackFunction(self,radio_Obj, payload):
            try:
                #payload = self.sx127x.readPayload()
                dcode = payload.decode()
                rssi = self.sx127x.packetRssi()
                self.PacketList.append((rssi,payload))
                self.PacketNum += 1
                self.DrawLoraMonitor()

                if self.AutoRoll:
                    self.PacketIndex = self.PacketNum-1
                    self.Pindex = self.PacketNum - self.MaxPacketsPerScreen
                    if self.Pindex < 0:
                        self.Pindex = 0
                print(self.PacketNum,"Payload: {} | RSSI: {}".format(dcode, rssi))
            except Exception as e:
                print(e)
                
    def receiveCallback(self):
        print("LoRa Receiver Callback")
        self.sx127x.onReceive(self.CallbackFunction)
        self.sx127x.receive()

        
    def Run(self):
        self.receiveCallback()
        while True:
            self.CheckKeyPress()
            self.DrawLoraMonitor()


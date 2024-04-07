import UI,Popups
from Control import UserControl
import fontlib
import utime
import Crypto

class LoraPacketWindow(UserControl):
    def __init__(self,lcd,uart_,eep,PacketIndex,PacketData,RSSI):
        self.lcd = lcd
        self.uart = uart_
        self.eep = eep
        self.PacketIndex = PacketIndex
        self.PacketLen = len(PacketData)
        self.TotalLines = self.PacketLen//7
        self.PacketData = PacketData
        self.PacketRSSI = RSSI
        self.lineindex = 0
        self.Decode = False
        self.ShowMenu = False
        self.MenuIndex = 0
        self.PossibleMenus = [["Export","Delete","Decode"],["Export","Delete","Hex"]]
        self.Menubuttons = self.PossibleMenus[0]
        self.MenuLen = 3
        
    def Ok_Func(self):
        if self.ShowMenu:
            if self.Decode:
                self.Menubuttons = self.PossibleMenus[1]
                Option = self.Menubuttons[self.MenuIndex]
            else:
                self.Menubuttons = self.PossibleMenus[0]
                Option = self.Menubuttons[self.MenuIndex]
            if Option == 'Export':
                return('Export')
            if Option == 'Delete':
                Q_Ans = Popups.OptionChoice(self.lcd,self.uart,("Are you sure?","Cant be reversed"),('Yep','Cancel'))
                if Q_Ans == 'Yep':
                    return("DELETE")
            if Option == 'Decode':
                self.Decode = True
            if Option == 'Hex':
                self.Decode = False
        else:
            self.ShowMenu = True
            
    def Left_Func(self):
        if self.ShowMenu:
            if self.MenuIndex > 0:
                self.MenuIndex -= 1
        else:     
            if self.lineindex > 0 :
                self.lineindex -= 1
            
    def Right_Func(self):
        if self.ShowMenu:
            if self.MenuIndex < self.MenuLen - 1:
                self.MenuIndex += 1        
        else:
            if self.lineindex < self.TotalLines and self.PacketLen > 7*4:
                self.lineindex += 1
            
    def ESC_Func(self):
        if self.ShowMenu:
            self.ShowMenu = False
        else:
            return("ESCAPE")
    
    def DEL_Func(self):
        Q_Ans = Popups.OptionChoice(self.lcd,self.uart,("Are you sure?","Cant be reversed"),('Yep','Cancel'))
        if Q_Ans == Delete:
            return("DELETE")

    def DrawKeyWindow(self):
        self.lcd.fill(0)
        UI.DrawPacketWindow(self.lcd,self.PacketData,self.PacketRSSI,self.PacketLen,self.lineindex,decode=self.Decode,MaxLines = 4)
        if self.ShowMenu:
            UI.BottomMenu(self.lcd,self.Menubuttons,self.MenuIndex)
        self.lcd.show()
            
    def Run(self):
        while True:
            self.DrawKeyWindow()
            r = self.CheckKeyPress()
            if r != None:
                return r
            
class LoraMonitor(UserControl):
    def __init__(self,lcd,uart_,i2c,sx127x):
        self.lcd = lcd
        self.uart = uart_
        self.i2c = i2c
        self.eep = Crypto.Geteep(self.lcd,self.i2c)
        self.sx127x = sx127x
        self.PacketList = []
        self.PacketNum = 0
        self.PacketIndex = 0
        self.Pindex = 0
        self.scroll = 0
        self.MaxPacketsPerScreen = 4
        self.initTime = utime.ticks_ms()
        self.AutoRoll = True
        self.ShowPacket = False
        
    def Ok_Func(self):
        PacketWindow = LoraPacketWindow(self.lcd,self.uart,self.eep,self.PacketIndex,self.PacketList[self.PacketIndex][1],self.PacketList[self.PacketIndex][0])
        resp = PacketWindow.Run()
        if resp == "DELETE":
            del self.PacketList[self.PacketIndex]
            if self.PacketIndex > 0:
                self.PacketIndex -= 1
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
        if (utime.ticks_ms()-self.initTime > 500):
            self.initTime = utime.ticks_ms()
            self.scroll += 1
        if self.scroll > 1000:
            self.scroll = 0
        self.lcd.fill(0)
        UI.DrawPacketMonitor(self.lcd,self.PacketList,self.PacketIndex,self.Pindex,self.scroll)
        self.lcd.show()
        
    def CallbackFunction(self,radio_Obj, payload):
            try:
                payload = self.sx127x.readPayload()
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
        self.sx127x.onLoraReceive(self.CallbackFunction)
        self.sx127x.receive()

        
    def Run(self):
        self.receiveCallback()
        while True:
            self.CheckKeyPress()
            self.DrawLoraMonitor()


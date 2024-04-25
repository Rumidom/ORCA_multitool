import time,os
import Crypto,Config
import Popups,UI
import fontlib
from Control import UserControl
import Helpers
class Notepad(UserControl):
    def __init__(self,lcd,uart_,sd,i2c,FilePath = None):
        self.eep = Crypto.Geteep(lcd,i2c)
        self.lcd = lcd
        self.uart = uart_
        self.sd = sd
        self.FilePath = FilePath
        self.DConfig = Config.GetDeviceConfig()
        self.keyslot = None
        self.key = None
        self.cursorPos = 0
        self.cursorLine = 0
        self.WindowPos_x = 0
        self.WindowPos_y = 0
        self.inittime = time.ticks_ms()
        self.cursorBlink = False
        self.lenList = []
        self.screen_maxchars = 16
        self.screen_maxlines = 7
        if sd:
            vfs = os.VfsFat(sd)
            os.mount(vfs, "/sd")
            
        if self.FilePath != None:
            try:
                self.keyslot = int(FilePath.split("[(")[1].split(")]")[0])
            except:
                self.keyslot = None
            if self.keyslot != None and self.keyslot < 1024:
                self.key = Crypto.GetKeyFromEEPROM(self.lcd,self.keyslot,self.eep)
                print(self.FilePath)
                f = open(self.FilePath,"rb")
                data = f.read()
                f.close
                self.LineList = Crypto.DecryptBytearraytoString(data,self.key).splitlines(True)
            else:
                f = open(self.FilePath)
                data = f.read()
                f.close
                self.LineList = data.splitlines(True)
        else:
            self.LineList = [""]
        for Line in self.LineList:
            self.lenList.append(len(Line))
            
    def Ok_Func(self):
        line = self.LineList[self.cursorLine]
        self.LineList[self.cursorLine] = line[0:self.cursorPos]+"\n"
        newline = line[self.cursorPos:]
        if newline == "":
            newline = "\n"
        self.LineList = self.LineList[0:self.cursorLine+1]+[newline]+self.LineList[self.cursorLine+1:]
        self.lenList = self.lenList[0:self.cursorLine+1]+[len(newline)]+self.lenList[self.cursorLine+1:]
        self.cursorPos = 0
        self.WindowPos_x = 0
        self.cursorLine += 1
        if self.cursorLine > (self.screen_maxlines-1):
            self.WindowPos_y += 1 
        #print(self.cursorPos,self.cursorLine,self.WindowPos_y)
        
    def Left_Func(self):
        if self.cursorPos > 0:
            self.cursorPos -= 1
            if ((self.WindowPos_x > 0) and (self.cursorPos == self.WindowPos_x-1)):
                self.WindowPos_x -= 1

        elif self.cursorLine > 0:
            self.cursorLine -= 1
            self.cursorPos = self.lenList[self.cursorLine]-1
            if self.cursorPos > self.screen_maxchars:
                self.WindowPos_x = self.lenList[self.cursorLine]-self.screen_maxchars
            if ((self.WindowPos_y > 0) and (self.cursorLine == self.WindowPos_y-1)):
                self.WindowPos_y -= 1 
        #print(self.cursorPos,self.cursorLine,self.WindowPos_y)
        
    def Right_Func(self):
        if self.cursorPos < self.lenList[self.cursorLine]:
            self.cursorPos += 1
            if self.cursorPos > self.screen_maxchars:
                self.WindowPos_x += 1
        else:
            if self.cursorLine < (len(self.LineList)-1):
                self.cursorPos = 0
                self.cursorLine += 1
                self.WindowPos_x = 0
                if self.cursorLine > (self.screen_maxlines-1):
                    self.WindowPos_y += 1
        #print(self.cursorPos,self.cursorLine,self.WindowPos_y)
    
    def BKSP_Func(self):
        #print(cursorPos,cursorLine,lenList[cursorLine])
        if self.cursorPos > 0:
            line = self.LineList[self.cursorLine]
            self.lenList[self.cursorLine] -= 1
            line = line[0:self.cursorPos-1]+line[self.cursorPos:]
            self.LineList[self.cursorLine] = line
            self.cursorPos -= 1
        elif (self.lenList[self.cursorLine] == 0) or (self.LineList[0] == "\n"):
            del self.LineList[self.cursorLine]
            del self.lenList[self.cursorLine]
        
    def ESC_Func(self):
        Save_Ans = Popups.OptionChoice(self.lcd,self.uart,(None,"Save file?"),("Yes","No"))
        if (Save_Ans == "No"):
            os.umount('/sd')
            return("ESCAPE")
        else:
            data = "".join(self.LineList).encode()
            if (self.FilePath == None):
                self.FilePath = Popups.TextInput(self.lcd,self.uart,["Choose a file","name/path:"])
                if self.DConfig["Save To"] == 0: #Card
                    self.FilePath = "sd/"+self.FilePath
                elif self.DConfig["Save To"] == 1: #Flash
                    self.FilePath = "files/"+self.FilePath     
            print("Save To: ", self.DConfig["Save To"])
            print(self.FilePath)
            if (self.DConfig["Encrypt"] != 1):
                Enc_ = "Yes"
                Use_Key_ = "Auto"
                
                if (self.DConfig["Encrypt"] == 2):#Ask
                    Enc_ = Popups.OptionChoice(self.lcd,self.uart,(None,"Encrypt file?"),("Yes","No"))
                if (self.DConfig["Use Key"] == 0):#Default
                    Use_Key_ = "Dfault"
                elif (self.DConfig["Use Key"] == 1):#Ask
                    if self.key != None:
                        Use_Key_=  Popups.OptionChoice(self.lcd,self.uart,("Which key should","be used?"),("Same","Dfault","Auto"))
                    else:
                        Use_Key_=  Popups.OptionChoice(self.lcd,self.uart,("Which key should","be used?"),("Dfault","Auto")) 
                if Enc_ == "Yes":
                    if Use_Key_ == "Auto":
                        self.key,self.keyslot = Crypto.AutoGenerateKeyOnEmptySlot(self.lcd,self.eep)
                    elif Use_Key_ == "Dfault":
                        self.keyslot = int(self.DConfig['DefaultKey'])
                        self.key = Crypto.GetKeyFromEEPROM(self.lcd,self.keyslot,self.eep)
                    Popups.Splash(self.lcd,["Encrypting With","key: "+str(self.keyslot)])
                    FileNdot = self.FilePath.split('[')[0].split('.')
                    self.FilePath = FileNdot[0] +"[({})]".format(self.keyslot)
                    if len(FileNdot) > 1:
                        self.FilePath+'.'+FileNdot[-1]
                    data = Crypto.EncryptBytearray(data,self.key)
            with open(self.FilePath, 'w') as f:
                print("Saving to: ",self.FilePath)
                f.write(data)
            os.umount('/sd')
        return("ESCAPE")
    def DEL_Func(self):
        return("DELETE")
        
    def Input_Func(self,w):
        
        if (w > b'\x0f') and (w != b'\x7f'):
            dcode = Helpers.ASCII_Decode(w)
            try:
                dcode = w.decode("utf-8")
            except Exception as e:
                print("Invalid unicode:",w)
            if dcode:
                line = self.LineList[self.cursorLine]
                self.lenList[self.cursorLine] += 1
                line = line[0:self.cursorPos]+dcode+line[self.cursorPos:]
                self.LineList[self.cursorLine] = line
                self.cursorPos += 1
                if self.cursorPos > self.screen_maxchars:
                    self.WindowPos_x += 1
    
    def DrawNotePad(self):
        self.lcd.fill(0)
        if ((time.ticks_ms() - self.inittime) > 500):
            self.cursorBlink = not self.cursorBlink
            self.inittime = time.ticks_ms()
        if self.cursorBlink:
            UI.Cursor(self.lcd,self.cursorPos-self.WindowPos_x,self.cursorLine-self.WindowPos_y)
        for i,Line in enumerate(self.LineList[self.WindowPos_y:self.screen_maxlines-self.WindowPos_y]):
            if Line != '':
                if Line[-1] == "\n":
                    Line = Line[:-1]
            fontlib.prt(Line[self.WindowPos_x:self.WindowPos_x+self.screen_maxchars],3,7*i,0,self.lcd.fbuf,UI.five_font,invert = False)   
        self.lcd.show()
        
    def Run(self):
        while True:
            self.DrawNotePad()
            r = self.CheckKeyPress()
            if r != None:
                return r


                    

        

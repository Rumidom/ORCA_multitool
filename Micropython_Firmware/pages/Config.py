import Buttons,Popups
import os,json
from Control import UserControl

def Defauts():
    Dft_Config = {"Save To":2,"Encrypt":0,"Use Key":2,"DefaultKey":"","AutoScroll":True}
    ConfigOptions = {"DefaultKey":"Num","Use Key":["Defaut","Ask","Auto"],"Encrypt":["Yes","No","Ask"],"Save To":["Card","Flash"],"AutoScroll":"Bool"}
    Configkeys = ["Save To","Encrypt","Use Key","DefaultKey","AutoScroll"] # could use ConfigOptions.keys but using this to set the order
    return((Dft_Config,ConfigOptions,Configkeys))

def GetDeviceConfig():
    Dft_Config = Defauts()[0]
    Config = Dft_Config
    noConfigFile = True
    for file in os.listdir("/"):
        if file == 'Device.conf':
            noConfigFile = False
            with open("Device.conf", 'r') as f:
                fileConfig = json.loads(f.read())
                for key in list(Dft_Config.keys()):
                    if not key in fileConfig:
                        fileConfig[key] = Dft_Config[key]
                Config = fileConfig
            break
    if noConfigFile:
        with open("Device.conf", 'w') as f:
            f.write(json.dumps(Config))
    return Config

class DeviceConfig(UserControl):
    def __init__(self,lcd,uart_):
        self.lcd = lcd
        self.uart = uart_
        self.numberskeys = ['q','w','e','r','t','y','u','i','o','p']
        self.ConfigOptions = Defauts()[1]
        self.Configkeys = Defauts()[2] # could use ConfigOptions.keys but using this to set the order
        self.Config = GetDeviceConfig()
        self.selected_index = 0
        self.change_config = False
        self.key = self.Configkeys[self.selected_index]
        print(self.Config )
    def Ok_Func(self):
        if self.ConfigOptions[self.key] == "Bool":
            self.Config[self.key] = not self.Config[self.key]
        else:
            self.change_config = not self.change_config
        
    def Left_Func(self):
        if self.change_config:
            if isinstance(self.ConfigOptions[self.key], list):
                if (self.Config[self.key] > 0):
                    self.Config[self.key] -= 1
        else:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.key = self.Configkeys[self.selected_index]
        
    def Right_Func(self):
        if self.change_config:
            if isinstance(self.ConfigOptions[self.key], list):
                if (self.Config[self.key] < len(self.ConfigOptions[self.key])-1):
                    self.Config[self.key] += 1
        else:
            if self.selected_index < (len(self.Configkeys)-1):
                self.selected_index += 1
                self.key = self.Configkeys[self.selected_index]
        
    def ESC_Func(self):
        if int(self.Config['DefaultKey']) > 1023:
            Popups.Splash(self.lcd,["Null DefaultKey","More than 1023"])
        else:
            Popups.Splash(self.lcd,[None,"Saving Config"])
            with open("Device.conf", 'w') as f:
                f.write(json.dumps(self.Config))
            print(self.Config )
            return("ESCAPE")
    
    def BKSP_Func(self):
        if self.ConfigOptions[self.key] == "Num" and self.change_config:
            self.Config[self.key] = self.Config[self.key][1:]
            
    def DEL_Func(self):
        if self.ConfigOptions[self.key] == "Num" and self.change_config:
            self.Config[self.key] = "" 
    
    def Input_Func(self,w):
        if self.ConfigOptions[self.key] == "Num" and self.change_config:
            decode = w.decode().lower()
            for i,c in enumerate(self.numberskeys):
                if (decode == str(i) or decode == c):
                    self.Config[self.key] = self.Config[self.key]+str(i)
                    if len(self.Config[self.key]) > 4:
                        self.Config[self.key] = self.Config[self.key][1:]
                        
    def DrawConfig(self):
        self.lcd.fill(0)
        SelectList = [x == self.selected_index for x in range(len(self.Configkeys))]
        for i,key in enumerate(self.Configkeys):
            if isinstance(self.ConfigOptions[key], list):
                Buttons.DrawMenuScrollOptions(self.lcd,i,key,self.ConfigOptions[key],self.Config[key],selected=SelectList[i],change = (self.selected_index == i and self.change_config))
            elif self.ConfigOptions[key] == "Num":
                Buttons.DrawMenuNumberInput(self.lcd,i,key,num = self.Config[key],selected=SelectList[i],change = (self.selected_index == i and self.change_config))
            elif self.ConfigOptions[key] == "Bool":
                Buttons.DrawMenuCheckBox(self.lcd,i,key,selected = SelectList[i],checked = self.Config[key])
        self.lcd.show()
    
    def Run(self):
        self.DrawConfig()
        while True:
            self.DrawConfig()
            r = self.CheckKeyPress()
            if r != None:
                return r
            



            

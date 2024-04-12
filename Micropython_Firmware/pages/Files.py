import UI,Popups
import os,utime
from machine import SDCard,Pin
from Control import UserControl

def isFolder(path):
    try:
        list = os.listdir(path)
        return(True)
    except:
        return(False)
    
def DeleteFile(sd,filepath):
    split = filepath.split("/")
    print("removing ", filepath)
    if len(split)>1:
        if split[0] == "sd" or split[1] == "sd":
            vfs = os.VfsFat(sd)
            os.mount(vfs, "/sd")
            os.remove(filepath)
            os.umount("/sd")
    else:
        os.remove(filepath)
        
class FileExplorer(UserControl):
    def __init__(self,lcd,uart_,sd):
        self.uart = uart_
        self.lcd = lcd
        self.sd = sd
        self.FileList = []
        self.initTime = utime.ticks_ms()
        self.fileSelectedFlag = False
        self.FileIndex = 0
        self.scroll = 0
        self.Menu_index = 0
        self.Pindex = 0
        self.extensionOptions = {"py":["Run","View","Edit"],"Default":["View","Edit"]}
        self.FileOptions = self.extensionOptions["Default"] + ["Move","Delete","Rename"]
        self.FileIcons = []
        self.MenuActive = False
        self.path = ""
        self.Dir_Ans = Popups.OptionChoice(self.lcd,self.uart,["Open Files From:"],("SD","Flash"))
        if self.Dir_Ans == "SD":
            if self.sd == None:
                Popups.Splash(self.lcd,['SD Card not found'])
            self.path = "/sd"
            vfs = os.VfsFat(self.sd)
            os.mount(vfs, "/sd")
        elif self.Dir_Ans == "Flash":
            self.path = "/files"
        
        
    def Ok_Func(self):
        extension = self.FileList[self.FileIndex].split(".")[-1]
        if extension in self.extensionOptions:
            self.FileOptions = self.extensionOptions[extension]+["Move","Delete","Rename"]
        else:
            self.FileOptions = self.extensionOptions["Default"]+["Move","Delete","Rename"]
        if self.MenuActive:
            if self.Dir_Ans == "SD":
                os.umount("/sd")
            return(self.FileOptions[self.Menu_index],self.path+"/"+self.FileList[self.FileIndex])
        else:
            self.MenuActive = True
    
    def Left_Func(self):
        self.scroll = 0
        if self.MenuActive:
            if self.Menu_index > 0:
                self.Menu_index -= 1
        else:
            if self.FileIndex > 0:
                self.FileIndex -= 1
                if (self.FileIndex == self.Pindex-1):
                    self.Pindex -= 1
                    
    def Right_Func(self):
        self.scroll = 0
        if self.MenuActive:
            if self.Menu_index < (len(self.FileOptions)-1) :
                self.Menu_index += 1
        else:
            if self.FileIndex < (len(self.FileList)-1):
                self.FileIndex += 1
                if self.FileIndex > 3:
                    self.Pindex += 1                
    def ESC_Func(self):
        print("ESCAPE")
        if self.MenuActive:
            self.MenuActive = False
        else:
            if self.Dir_Ans == "SD":
                os.umount("/sd")
            return(None,None)
    
    def DEL_Func(self):
        if self.Dir_Ans == "SD":
            os.umount("/sd")
        return(None,None)
    
    def DrawFileView(self):
        self.lcd.fill(0)
        for i,file in enumerate(self.FileList[self.Pindex:self.Pindex+4]):
            filetext = ""
            if (self.scroll != 0) and (i == self.FileIndex-self.Pindex):
                filetext = file[self.scroll:self.scroll+15]
            else:
                filetext = file
            UI.DrawIconMenuOption(self.lcd,i,filetext,icon = self.FileIcons[i+self.Pindex],selected = (i == self.FileIndex-self.Pindex))
        if self.MenuActive:
            UI.BottomMenu(self.lcd,self.FileOptions,self.Menu_index,MenuActive=self.MenuActive)
        self.lcd.show()
        
    def GetFileIcons(self):
        iconlist = []
        file_extensions = {"py":"!","txt":'"',"":"#","folder":"$"}
        for file in self.FileList:
            icon = "#"
            dotsplit = file.split(".")
            extension = dotsplit[-1]
            if len(dotsplit) == 1:
                if isFolder(self.path+"/"+file):
                    icon = file_extensions["folder"]
            elif extension in file_extensions:
                icon = file_extensions[extension]
            iconlist.append(icon)
        return iconlist
                
    def Run(self):
        self.FileList = os.listdir(self.path)
        if "System Volume Information" in self.FileList:
            self.FileList.remove("System Volume Information")
        self.FileIcons = self.GetFileIcons()

        while True:
            if (len(self.FileList[self.FileIndex]) > 15 and utime.ticks_ms()-self.initTime > 500):
                self.initTime = utime.ticks_ms()
                self.scroll += 1
                if (len(self.FileList[self.FileIndex]) - (15+self.scroll)) < 0:
                    self.scroll = 0
            r = self.CheckKeyPress()
            self.DrawFileView()
            if r:
                return r

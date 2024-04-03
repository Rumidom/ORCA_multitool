import framebuf,time,math,random,gc,utime,network
import pcd8544,fontlib
from machine import Pin,SPI,SoftSPI,I2S,I2C,UART,SDCard
from sx127x import SX127x
import Cryptography,Popups,Notes,Config,Files,Lora
import UI

spi  = SPI(2, sck=Pin(13), mosi=Pin(11), miso=Pin(12))
spi.init(baudrate=4000000, polarity=0, phase=0)
sd = None

try:
    sd = SDCard(slot=3, width=1,
             sck=Pin(39, pull=Pin.PULL_UP),
             miso=Pin(21, pull=Pin.PULL_UP),
             mosi=Pin(42, pull=Pin.PULL_UP),
             cs=Pin(15, pull=Pin.PULL_UP),
             cd=None,
             wp=None,
             freq=2000000)
except:
    print("no SD Card")


sx127x = SX127x(spi, pins={'dio_0':6,'ss':5,'reset':7})
uart1 = UART(1, baudrate=9600, tx=17, rx=18)

p17 = Pin(17,Pin.OPEN_DRAIN)
p18 = Pin(18,Pin.OPEN_DRAIN)

i2c = I2C(1,scl=Pin(9), sda=Pin(8),freq=400000)

lcd = pcd8544.PCD8544_FRAMEBUF(spi, Pin(1, Pin.OUT), Pin(2, Pin.OUT), Pin(3, Pin.OUT))

backlight = Pin(48, Pin.OUT)
backlight.off()

Lora_NSS = Pin(5, Pin.OUT)
Lora_NSS.on()
                
def DrawMenu(MenuOptions,SelectedIndex,maxrows = 7):
    lcd.fill(0)
    menupos = 0
    if (SelectedIndex > (maxrows-1)):
        menupos = SelectedIndex - (maxrows-1)
        SelectedIndex = (maxrows-1)
        
    for i,item in enumerate(MenuOptions[menupos:maxrows+menupos]):
        if i == SelectedIndex:
            fontlib.printstring(item,3,i*7,0,lcd.fbuf,font = "five",invert = True)
        else:
            fontlib.printstring(item,3,i*7,0,lcd.fbuf,font = "five")
    lcd.show()
    

def RunMenu(MenuOptions):
    MenuLen = len(MenuOptions)
    selected_index = 0
    while True:
        if (uart1.any()>0):
            w = uart1.read()
            if w == b'\xab': #>>
                if selected_index < (MenuLen-1):
                    selected_index += 1
            if w == b'\n': #Ok/Enter
                return(MenuOptions[selected_index])
            if w == b'\xbb': #<<
                if selected_index > 0:
                    selected_index -= 1
            if w == b'\x7f': #DEL
                return("DELETE")
            if w == b'\x1b': #ESC
                return("ESCAPE")
        DrawMenu(MenuOptions,selected_index)

def DisplayDeviceInfo():
    #print("Device info")
    lcd.fill(0)
    wlan=network.WLAN()
    MacAdr = wlan.config('mac').hex().upper()
    fs_stat = os.statvfs("/")
    KB = 1024
    MB = 1024 * 1024
    totalram = (gc.mem_free() + gc.mem_alloc())
    usedram = gc.mem_alloc()
    flashsize = fs_stat[1] * fs_stat[2]
    freeflash = fs_stat[1] * fs_stat[2]
    usedflash = flashsize - freeflash
    fontlib.printstring("Mpython "+ os.uname()[3].split(" ")[0],0,0,0,lcd.fbuf)
    fontlib.printstring("MAC:"+ MacAdr,0,10,0,lcd.fbuf)
    fontlib.printstring("Disk:{:.2f}|{:.2f}MB".format(usedflash / MB,flashsize / MB),0,20,0,lcd.fbuf)
    fontlib.printstring("Ram:{:.2f}|{:.2f}MB".format(usedram / MB,totalram / MB),0,30,0,lcd.fbuf)
    lcd.show()
    while True:
        if (uart1.any()>0): # exit on any key
            w = uart1.read()
            break
        

        

lcd.fill(0)
uart1.init()
#fontlib.printstring("ORCA MULTITOOL",0,10,1,lcd,font = "futuristic")

#RunKeyViewer()

#lcd.show()
#time.sleep(2)


MainMenuOptions = ["Serial Tools","I2C Tools","LORA Tools","Bluetooth Tools","ESP-now","NotePad","File Explorer","Cryptography","Device Config","Device Info","Remove SDCard"]
Serialtools = ["Serial Monitor","Serial Config"]
I2Ctools = ["I2C Scanner","I2C Screen Tester"]
LoratoolsOptions = ["LORA Monitor","LORA Mensager"]
CryptographyOptions = ["Key Viewer","Export Keyfile","Import Keyfile","Erase All Keys"]


#lcd.show()

while True:
    MainMenuSelected = RunMenu(MainMenuOptions)
    if (MainMenuSelected == "Serial Tools"):
        pass
    if (MainMenuSelected == "I2C Tools"):
        pass
    if (MainMenuSelected == "LORA Tools"):
        LORAtoolsSelected = RunMenu(LoratoolsOptions)
        if (LORAtoolsSelected == "LORA Monitor"):
            LoraMonitor = Lora.LoraMonitor(lcd,uart_,sx127x)
            LoraMonitor.Run()
    if (MainMenuSelected == "NotePad"):
        Notepad = Notes.Notepad(lcd,uart1,sd,i2c,FilePath = None)
        Notepad.Run()
    if (MainMenuSelected == "File Explorer"):
        FileExplorer = Files.FileExplorer(lcd,uart1,sd)
        fileAction,filepath = FileExplorer.Run()
        if fileAction == "Edit":
            Notepad = Notes.Notepad(lcd,uart1,sd,i2c,FilePath = filepath)
            Notepad.Run()
        if fileAction == "Delete":
            Files.DeleteFile(sd,filepath)
            
    if (MainMenuSelected == "Cryptography"):
        CryptographySelected = RunMenu(CryptographyOptions)
        if CryptographySelected == "Key Viewer":
            KeysBrowser = Cryptography.KeysBrowser(lcd,uart1,i2c)
            KeysBrowser.Run()
    if (MainMenuSelected == "Device Info"):
        DisplayDeviceInfo()
    if (MainMenuSelected == "Device Config"):
        DeviceConfig = Config.DeviceConfig(lcd,uart1)
        DeviceConfig.Run()
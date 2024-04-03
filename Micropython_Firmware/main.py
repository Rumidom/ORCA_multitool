import framebuf,time,math,random,gc,utime,network
import pcd8544,fontlib
from machine import Pin,SPI,SoftSPI,I2S,I2C,UART,SDCard
from sx127x import SX127x
import Menu,Crypto,Popups,Notes,Config,Files,Lora
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
        

lcd.fill(0)
uart1.init()
#fontlib.printstring("ORCA MULTITOOL",0,10,1,lcd,font = "futuristic")

#RunKeyViewer()

#lcd.show()
#time.sleep(2)


#MainMenuOptions = ["Serial Tools","I2C Tools","LORA Tools","Bluetooth Tools","ESP-now","NotePad","File Explorer","Crypto.graphy","Device Config","Device Info"]
MainMenuOptions = ["LORA Tools","NotePad","File Explorer","Cryptography","Device Config","Device Info"]
Serialtools = ["Serial Monitor","Serial Config"]
I2Ctools = ["I2C Scanner","I2C Screen Tester"]
LoratoolsOptions = ["LORA Monitor","LORA Mensager"]
CryptographyOptions = ["Key Viewer","Export Keyfile","Import Keyfile","Erase All Keys"]


#lcd.show()

while True:
    MainMenu = Menu.Menu(lcd,uart1,MainMenuOptions)
    MainMenuSelected = MainMenu.Run()
    
    if (MainMenuSelected == "Serial Tools"):
        pass
    
    if (MainMenuSelected == "I2C Tools"):
        pass
    
    if (MainMenuSelected == "LORA Tools"):
        LORAMenu = Menu.Menu(lcd,uart1,LoratoolsOptions)
        LORAtoolsSelected = LORAMenu.Run()
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
        CryptoMenu = Menu.Menu(lcd,uart1,CryptographyOptions)
        CryptographySelected = CryptoMenu.Run()
        if CryptographySelected == "Key Viewer":
            KeysBrowser = Cryptography.KeysBrowser(lcd,uart1,i2c)
            KeysBrowser.Run()
            
    if (MainMenuSelected == "Device Info"):
        Popups.DisplayDeviceInfo(lcd,uart1)
        
    if (MainMenuSelected == "Device Config"):
        DeviceConfig = Config.DeviceConfig(lcd,uart1)
        DeviceConfig.Run()
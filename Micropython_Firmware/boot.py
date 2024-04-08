import os,sys
from machine import SPI,Pin
import pcd8544
import fontlib
import asyncio

#Create Necessary folders and organizes all files on the device

FileList = os.listdir("/")
File_structure = {"/lib":["bdevice.py","eeprom_i2c.py","pcd8544.py","sx127x.py","fontlib.py","fonts_dictionary.py"],
                  "/pages":["Config.py","Crypto.py","Notes.py","Files.py","Lora.py","Menu.py"],
                  "/components":["UI.py","Popups.py","Control.py","Helpers.py"],
                  "/files":[],
                  "/sd":[]
                  }

folders = list(File_structure.keys())
for folder in folders:
    if folder not in sys.path:
        sys.path.append(folder)
        
import UI

spi  = SPI(2, sck=Pin(13), mosi=Pin(11), miso=Pin(12))
spi.init(baudrate=4000000, polarity=0, phase=0)
lcd = pcd8544.PCD8544_FRAMEBUF(spi, Pin(1, Pin.OUT), Pin(2, Pin.OUT), Pin(3, Pin.OUT))

lcd.fill(0)
fontlib.printstring("ORCA MULTITOOL",0,10,1,lcd.fbuf,font = "futuristic")
UI.DrawBitmap("JMPORCA 1.bmp",20,10,lcd.fbuf)
lcd.show()

for folder in folders:
    if not folder[1:] in FileList:
        os.mkdir(folder)

    for file in File_structure[folder]:
        if file in FileList:
            print(file,folder+"/"+file)
            os.rename(file, folder+"/"+file)
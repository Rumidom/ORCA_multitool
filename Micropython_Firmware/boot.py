import os,sys
from machine import SPI,Pin
import pcd8544
import fontlib

#Create Necessary folders and organizes all files on the device

FileList = os.listdir("/")
File_structure = {"/lib":["bdevice.py","eeprom_i2c.py","pcd8544.py","sx127x.py","fontlib.py","fonts_dictionary.py"],
                  "/pages":["Config.py","Crypto.py","Notes.py","Files.py","Lora.py","Menu.py"],
                  "/utils":["UI.py","Popups.py","Control.py","Helpers.py"],
                  "/files":[],
                  "/sd":[],
                  "/bitmaps":["JMPORCA 0.bmp","JMPORCA 1.bmp","JMPORCA 2.bmp","JMPORCA 3.bmp",
                              "JMPORCA 4.bmp","JMPORCA 5.bmp","JMPORCA 6.bmp","JMPORCA 7.bmp",
                              "ANTENNA.bmp"]
                  }

folders = list(File_structure.keys())
for folder in folders:
    if folder not in sys.path:
        sys.path.append(folder)

for folder in folders:
    if not folder[1:] in FileList:
        os.mkdir(folder)

    for file in File_structure[folder]:
        if file in FileList:
            print(file,folder+"/"+file)
            os.rename(file, folder+"/"+file)
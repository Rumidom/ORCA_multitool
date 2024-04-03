import os
import sys

#Create Necessary folders and organizes all files on the device

FileList = os.listdir("/")
File_structure = {"/lib":["bdevice.py","eeprom_i2c.py","pcd8544.py","sx127x.py","fontlib.py","fonts_dictionary.py"],
                  "/pages":["Config.py","Cryptography.py","Notes.py","Files.py","Lora.py"],
                  "/components":["UI.py","Popups.py","Control.py"],
                  "/files":[],
                  "/sd":[]
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
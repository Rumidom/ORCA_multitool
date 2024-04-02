import time,os
from Config import GetDeviceConfig
from Cryptography import GetKeyFromEEPROM,DecryptBytearraytoString,EncryptBytearray,AutoGenerateKeyOnEmptySlot
import Popups
import fontlib

def DrawCursor(lcd,xi,yi,charwidth = 5,lineheight=7,spce=0,selected = False):
    fontlib.printstring("|",(charwidth+spce)*xi+1,(lineheight*yi),0,lcd.fbuf,invert = selected)
    
def RunNotePad(lcd,uart_,sd,FilePath = None):
    DConfig = GetDeviceConfig()
    keynum = None
    key = None
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    if FilePath != None:
        try:
            keynum = int(FilePath.split("[(")[1].split(")]")[0])
        except:
            keynum = None
        if keynum != None and keynum < 1024:
            key = GetKeyFromEEPROM(keynum)
            print(FilePath)
            f = open(FilePath,"rb")
            data = f.read()
            f.close
            LineList = DecryptBytearraytoString(data,key).splitlines(True)
        else:
            f = open(FilePath)
            data = f.read()
            f.close
            LineList = data.splitlines(True)
            
    else:
        LineList = [""]
    
    cursorPos = 0
    cursorLine = 0
    WindowPos_x = 0
    WindowPos_y = 0
    inittime = time.ticks_ms()
    cursorBlink = False
    lenList = []
    screen_maxchars = 16
    screen_maxlines = 7
    for Line in LineList:
        lenList.append(len(Line))
    while True:
        lcd.fill(0)
        if ((time.ticks_ms() - inittime) > 500):
            cursorBlink = not cursorBlink
            inittime = time.ticks_ms()
        for i,Line in enumerate(LineList[WindowPos_y:screen_maxlines-WindowPos_y]):
            if Line != '':
                if Line[-1] == "\n":
                    Line = Line[:-1]
            fontlib.printstring(Line[WindowPos_x:WindowPos_x+screen_maxchars],3,7*i,0,lcd.fbuf,invert = False)
        if (uart_.any()>0):
            w = uart_.read()
            #print(w)
            if w == b'\xab': #>>
                if cursorPos < lenList[cursorLine]:
                    cursorPos += 1
                    if cursorPos > screen_maxchars:
                        WindowPos_x += 1
                else:
                    if cursorLine < (len(LineList)-1):
                        cursorPos = 0
                        cursorLine += 1
                        WindowPos_x = 0
                        if cursorLine > (screen_maxlines-1):
                            WindowPos_y += 1
                print(cursorPos,cursorLine,WindowPos_y)
            elif w == b'\n': #Ok/Enter

                line = LineList[cursorLine]
                LineList[cursorLine] = line[0:cursorPos]+"\n"
                newline = line[cursorPos:]
                if newline == "":
                    newline = "\n"
                LineList = LineList[0:cursorLine+1]+[newline]+LineList[cursorLine+1:]
                lenList = lenList[0:cursorLine+1]+[len(newline)]+lenList[cursorLine+1:]
                cursorPos = 0
                WindowPos_x = 0
                cursorLine += 1
                if cursorLine > (screen_maxlines-1):
                    WindowPos_y += 1 
                print(cursorPos,cursorLine,WindowPos_y)
            elif w == b'\xbb': #<<
                
                if cursorPos > 0:
                    cursorPos -= 1
                    if ((WindowPos_x > 0) and (cursorPos == WindowPos_x-1)):
                        WindowPos_x -= 1

                elif cursorLine > 0:
                    cursorLine -= 1
                    cursorPos = lenList[cursorLine]-1
                    if cursorPos > screen_maxchars:
                        WindowPos_x = lenList[cursorLine]-screen_maxchars
                    if ((WindowPos_y > 0) and (cursorLine == WindowPos_y-1)):
                        WindowPos_y -= 1 
                print(cursorPos,cursorLine,WindowPos_y)
            elif w == b'\x08': #BKSP
                #print(cursorPos,cursorLine,lenList[cursorLine])
                if cursorPos > 0:
                    line = LineList[cursorLine]
                    lenList[cursorLine] -= 1
                    line = line[0:cursorPos-1]+line[cursorPos:]
                    LineList[cursorLine] = line
                    cursorPos -= 1
                elif (lenList[cursorLine] == 0) or (LineList[0] == "\n"):
                    del LineList[cursorLine]
                    del lenList[cursorLine]
            elif w == b'\x1b': #ESC
                Save_Ans = Popups.OptionChoice(lcd,uart_,(None,"Save file?"),("Yes","No"))
                if (Save_Ans == "No"):
                    os.umount('/sd')
                    return("ESCAPE")
                else:
                    data = "".join(LineList).encode()
                    if (FilePath == None):
                        FilePath = Popups.TextInput(lcd,uart_,["Choose a file","name/path:"])
                        if DConfig["Save To"] == 1: #Flash
                            FilePath = "files/"+FilePath
                        elif DConfig["Save To"] == 0: #Card
                            FilePath = "sd/"+FilePath
                    print("Save To: ", DConfig["Save To"])
                    print(FilePath)
                    if (DConfig["Encrypt"] != 1):
                        Enc_Ans = "Yes"
                        Use_Key_Ans = "Auto"
                        if (DConfig["Encrypt"] == 2):#Ask
                            Enc_Ans = Popups.OptionChoice(lcd,uart_,(None,"Encrypt file?"),("Yes","No"))
                        if (DConfig["Use Key"] == 1):#Ask
                            Use_Key_Ans =  Popups.OptionChoice(lcd,uart_,("Which key should","be used?"),("Default","Auto"))
                        if Enc_Ans == "Yes":
                            key,keyslot = None,None
                            if Use_Key_Ans == "Auto":
                                key,keyslot = AutoGenerateKeyOnEmptySlot(lcd)
                            elif Use_Key_Ans == "Default":
                                keyslot = int(DConfig['DefaultKey'])
                                key = GetKeyFromEEPROM(keyslot)
                            Popups.Splash(lcd,["Encrypting With","key: "+str(keyslot)])
                            FileNdot = FilePath.split('.')
                            FilePath = FileNdot[0] +"[({})]".format(keyslot)
                            if len(FileNdot) > 1:
                                FilePath+'.'+FileNdot[-1]
                            data = EncryptBytearray(data,key)
                    with open(FilePath, 'w') as f:
                        f.write(data)
                    os.umount('/sd')
                    return("ESCAPE")
            elif (w > b'\x0f') and (w != b'\x7f'):
                dcode = w.decode("utf-8")
                if dcode:
                    line = LineList[cursorLine]
                    lenList[cursorLine] += 1
                    line = line[0:cursorPos]+dcode+line[cursorPos:]
                    LineList[cursorLine] = line
                    cursorPos += 1
                    if cursorPos > screen_maxchars:
                        WindowPos_x += 1
                    
        if cursorBlink:
            DrawCursor(lcd,cursorPos-WindowPos_x,cursorLine-WindowPos_y)
        lcd.show()

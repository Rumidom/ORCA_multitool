import fontlib,UI
import utime
import os,time,math,gc,utime,network

def DisplayCenteredLines(lcd,lines,ydist = 9):
    for i,line in enumerate(lines):
        if line != None:
            linelen = len(line)
            fontlib.printstring(line,42-((linelen*5)//2),ydist+7*i,0,lcd.fbuf)
            
def Progress(lcd,ratio,lines):
    lcd.fill(0)
    DisplayCenteredLines(lcd,lines)
    fontlib.printstring('{:.2f} %'.format(ratio*100),25,25,0,lcd.fbuf)
    lcd.show()

def Splash(lcd,lines,font = "five",time = 2000):
    lcd.fill(0)
    DisplayCenteredLines(lcd,lines)
    lcd.show()
    utime.sleep_ms(time)
    
def DrawOptionChoice(lcd,index,lines,Options):
    lcd.fill(0)
    pos = ((6,25),(43,25),(24,35))
    if len(Options) > 1:
        for i,Option in enumerate(Options):
            UI.DrawButton(lcd,pos[i][0],pos[i][1],Options[i],selected = (index == i))
    else:
        UI.DrawButton(lcd,24,25,Options[0],selected = (index == 0))
    DisplayCenteredLines(lcd,lines)
    lcd.show()
    
def OptionChoice(lcd,uart1,lines,Options):
    selected_index = 0
    while True:
        if (uart1.any()>0):
            w = uart1.read()
            if w == b'\xab' and Options[1] != None: #>>
                if selected_index < len(Options)-1:
                    selected_index += 1
            if w == b'\n': #ok
                return(Options[selected_index])
            if w == b'\xbb'and Options[1] != None: #<<
                if selected_index > 0:
                    selected_index -= 1
            if w == b'\x9b': #ESC
                return("ESCAPE")
        DrawOptionChoice(lcd,selected_index,lines,Options = Options)

def DrawTextInput(lcd,lines,Input=None):
    lcd.fill(0)
    Inputlen = len(Input)
    if ((Input != None) and (Input != "")): 
        fontlib.printstring(Input,42-((Inputlen*5)//2),25,0,lcd.fbuf)
    DisplayCenteredLines(lcd,lines)
    lcd.show()
    
def TextInput(lcd,uart1,lines):
    Input = ""
    while True:
        if (uart1.any()>0):
            w = uart1.read()
            try:
                if w == b'\n': #ok
                    return(Input)
                elif w == b'\x08': #BKSP
                    Input = Input[:-1]
                elif w == b'\x1b': #ESC
                    return("ESCAPE")
                else:
                    dcode = w.decode("utf-8")
                    if dcode:
                        Input += dcode

            except Exception as e:
                print("Not Unicode: ",e)
            
        DrawTextInput(lcd,lines,Input=Input)

def DisplayDeviceInfo(lcd,uart1):
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
import framebuf,time,math,random,gc,utime,network
import pcd8544,fontlib
from machine import Pin,SPI,SoftSPI,I2S,I2C,UART
from sx127x import SX127x
import Cryptography

bck_pin = Pin(14)  # Bit clock output
ws_pin = Pin(15)   # Word clock output
sdin_pin = Pin(16) # Serial data input

audio_in = I2S(0,
               sck=bck_pin, ws=ws_pin, sd=sdin_pin,
               mode=I2S.RX,
               bits=16,
               format=I2S.MONO,
               rate=16000,
               ibuf=16000)



spi  = SPI(2, sck=Pin(13), mosi=Pin(11), miso=Pin(12))
spi.init(baudrate=4000000, polarity=0, phase=0)
lora_pins = {
    'dio_0':6,
    'ss':5,
    'reset':7,
}


uart1 = UART(1, baudrate=9600, tx=17, rx=18)

p17 = Pin(17,Pin.OPEN_DRAIN)
p18 = Pin(18,Pin.OPEN_DRAIN)

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
            fontlib.printstring(item,5,i*7,0,lcd.fbuf,font = "five",invert = True)
        else:
            fontlib.printstring(item,5,i*7,0,lcd.fbuf,font = "five")
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
            if w == b'\xa0': #ok
                return(MenuOptions[selected_index])
            if w == b'\xbb': #<<
                if selected_index > 0:
                    selected_index -= 1
            if w == b'\xa1': #DEL
                return("DELETE")
            if w == b'\x9b': #ESC
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
        
def PrintWrapedText(text_string,Screen_Width,CharSize):
    Max_char = int(Screen_Width/CharSize)
    lcd.fill(0)
    lines = []
    current_line = ""
    for char in text_string:
        current_line += char
        if len(current_line) >= Max_char:
            lines.append(current_line)
            current_line = ""
    if len(current_line) > 0:
        lines.append(current_line)
    for i,line in enumerate(lines):
        #lcd.text(line, 0, i*10, 1)
        fontlib.printstring(line,0,i*6,0,lcd,font = "five")
    
    lcd.show()
        

lcd.fill(0)
uart1.init()
#fontlib.printstring("ORCA MULTITOOL",0,10,1,lcd,font = "futuristic")

#RunKeyViewer()

#lcd.show()
#time.sleep(2)


MainMenuOptions = ["Serial Tools","I2C Tools","LORA Tools","NotePad","Cryptography","Device Config","Device Info"]
Serialtools = ["Serial Monitor","Serial Config"]
I2Ctools = ["I2C Scanner","I2C Screen Tester"]
LoratoolsOptions = ["LORA Monitor","LORA Mensager"]
NotePadOptions = ["New File","Open File","Notepad Config"]
CryptographyOptions = ["Key Viewer","Export Keyfile","Import Keyfile"]

Cryptography.RunKeyViewer(lcd,uart1)
'''
while True:
    MainMenuSelected = RunMenu(MainMenuOptions)
    if (MainMenuSelected == "Serial Tools"):
        pass
    if (MainMenuSelected == "I2C Tools"):
        pass
    if (MainMenuSelected == "LORA Tools"):
        pass
    if (MainMenuSelected == "NotePad"):
        NotePadSelected = RunMenu(NotePadOptions)
    if (MainMenuSelected == "Cryptography"):
        CryptographySelected = RunMenu(CryptographyOptions)
    if (MainMenuSelected == "Device Info"):
        DisplayDeviceInfo()
'''
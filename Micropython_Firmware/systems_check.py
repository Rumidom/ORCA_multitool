import time
import math
import pcd8544_fb
import random
from machine import Pin,SPI,SoftSPI,I2S,I2C,UART
import framebuf
from eeprom_i2c import EEPROM, T24C256
from sx127x import SX127x
import fontlib

bck_pin = Pin(14)  # Bit clock output
ws_pin = Pin(15)   # Word clock output
sdin_pin = Pin(16) # Serial data input

Screen_Width = 85
Screen_Height = 85

audio_in = I2S(0,
               sck=bck_pin, ws=ws_pin, sd=sdin_pin,
               mode=I2S.RX,
               bits=32,
               format=I2S.STEREO,
               rate=22050,
               ibuf=20000)


i2c = I2C(1,scl=Pin(9), sda=Pin(8),freq=400000)

#spi = SoftSPI(baudrate= 4000000, sck=Pin(13), mosi=Pin(11), miso=Pin(12))
spi  = SPI(2, sck=Pin(13), mosi=Pin(11), miso=Pin(12))
spi.init(baudrate=4000000, polarity=0, phase=0)
lora_pins = {
    'dio_0':6,
    'ss':5,
    'reset':7,
}


uart1 = UART(1, baudrate=9600, tx=17, rx=18)

cs = Pin(1, Pin.OUT)
dc = Pin(2, Pin.OUT)
rst = Pin(3, Pin.OUT)
lcd = pcd8544_fb.PCD8544_FB(spi, cs, dc, rst)

backlight = Pin(48, Pin.OUT)
backlight.off()

Lora_NSS = Pin(5, Pin.OUT)
Lora_NSS.on()

buffer = bytearray((pcd8544_fb.HEIGHT // 8) * pcd8544_fb.WIDTH)
fbuf = framebuf.FrameBuffer(buffer, pcd8544_fb.WIDTH, pcd8544_fb.HEIGHT, framebuf.MONO_VLSB)

def PrintCheckList(CheckList):
    fbuf.fill(0)
    for i,item in enumerate(CheckList):
        status = "ERR"
        if item[1]:
            status = "OK"
        #fbuf.text(item[0]+"-"+status, 0, i*10, 1)
        fontlib.printstring(item[0]+"-"+status,0,i*8,0,fbuf,font_name = "five")
    lcd.data(buffer)

def PrintText(text_string,Screen_Width,CharSize):
    Max_char = int(Screen_Width/CharSize)
    framebuf.fill(0)
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
        fbuf.text(line, 0, i*10, 1)
    
    lcd.data(buffer)
        
    
CheckList = [('LCD',True)]
PrintCheckList(CheckList)

eep = None
try:
    eep = EEPROM(i2c, T24C256)
    CheckList.append(('EEPROM',True))
except Exception as e:
    print(e)
    CheckList.append(('EEPROM',False))
PrintCheckList(CheckList)

lora = None
try:
    lora = SX127x(spi, pins=lora_pins)
    CheckList.append(('Lora',True))
except Exception as e:
    print(e)

    CheckList.append(('Lora',False))
PrintCheckList(CheckList)

mic_samples = bytearray(10000)
mic_samples_mv = memoryview(mic_samples)
num_bytes_read_from_mic = audio_in.readinto(mic_samples_mv)

inputbuffer = bytearray()
def keyboard_event(pin):
    w = None
    while not w:
        w = uart1.read()
    if w:
        try:
            d = w.decode('utf-8')
            inputbuffer.extend(w)
            PrintText(inputbuffer.decode('utf-8'),85,8)
        except UnicodeError:
            print("not unicode")
        
Pin(18).irq(keyboard_event, trigger=Pin.IRQ_FALLING)

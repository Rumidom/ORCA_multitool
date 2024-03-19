import random
from machine import Pin,I2C
from eeprom_i2c import EEPROM, T24C256
import fontlib

i2c = I2C(1,scl=Pin(9), sda=Pin(8),freq=400000)

def Generatekey(seed=None):
    random.seed(seed)
    key = b''
    for i in range(16):
        key += random.getrandbits(32).to_bytes(2,'big')
    return key

def SaveKeyToEEPROM(key,slot_index):
    eep = EEPROM(i2c, T24C256)
    eep[slot_index*32:(slot_index+1)*32] = key

def GetKeyFroomEEPROM(slot_index):
    eep = EEPROM(i2c, T24C256)
    return eep[slot_index*32:(slot_index+1)*32]
    
def EraseEEPROM(lcd):
    print("Erasing EEPROM")
    eep = EEPROM(i2c, T24C256)
    pagesize = 64
    pages = len(eep)/pagesize
    for i in range(pages):
        lcd.fill(0)
        fontlib.printstring("Erasing EEPROM",8,15,0,lcd.fbuf)
        fontlib.printstring('{:.2f} %'.format(((i+1)/pages)*100),25,25,0,lcd.fbuf)
        eep[i*pagesize:(i+1)*pagesize] = b'\x00'*pagesize
        lcd.show()

def DrawKeySlot(lcd,posx,posy,selected = False,empty = True,slot=4):
    lcd.rect(posx, posy, 33, 11, 1)
    lcd.line(posx+6, posy, posx+6, posy+10, 1)
    if not empty:
        fontlib.printchar("+",posx+1,posy+2,lcd.fbuf,font = "icons",invert = False)
    fontlib.printstring(f'{slot:04}',posx+8,posy+3,1,lcd.fbuf,invert = selected)
    lcd.line(posx+7, posy+1, posx+8+23, posy+1, 1)
    lcd.line(posx+7, posy+9, posx+8+23, posy+9, 1)

def DrawButton(lcd,posx,posy,text,selected = False):
    lcd.rect(posx, posy, 36, 9, 1)
    fontlib.printstring(text,posx+3,posy+2,0,lcd.fbuf,invert = selected)
    if selected:
        lcd.rect(posx+1, posy, 34, 9, 1)

def DrawKeyWindow(lcd,keydata,indexpos,keyslot):
    lcd.fill(0)
    hexdata = keydata.hex()
    buttons = [["Import","Export"],["Random","Erase "]]
    for i in range(7):
        for j in range(5):
            bindex = (i+7*j)
            if bindex < 32:
                fontlib.printstring(hexdata[bindex*2:bindex*2+2],i*12+1,j*7,0,lcd.fbuf)

    for i in range(2):
        pair_choice = (indexpos//2)
        DrawButton(lcd,6+37*i,36,buttons[pair_choice][i],selected = (indexpos ==  pair_choice*2+i))
    
    if indexpos < 2:
        fontlib.printstring("@",(42+38),37,0,lcd.fbuf,font="icons")
    else:
        fontlib.printstring("?",0,37,0,lcd.fbuf,font="icons")

    lcd.show()
    
def DrawKeyViwer(lcd,pag,pagdata,Selectedindex):
    lcd.fill(0)
    for j in range(2):
        for i in range(4):
            empty_slot = True
            selected_slot = False
            slot_index = (i+4*j)
            slotdata = pagdata[slot_index*32:(slot_index+1)*32]
            if ((slotdata != b'\x00'*32) and (slotdata != b'\xFF'*32)):
                empty_slot = False
            if (slot_index == Selectedindex):
                selected_slot = True
            DrawKeySlot(lcd,34*j,12*i,selected = selected_slot,empty = empty_slot,slot=slot_index+pag*8)
    fontlib.printstring(f'P.',69,33,0,lcd.fbuf,invert = False)
    fontlib.printstring(f'{pag:03}',69,39,0,lcd.fbuf,invert = False)
    lcd.show()

def RunKeyWidown(lcd,uart_,keyslot,data):
    selected_index = 0
    while True:
        if (uart_.any()>0):
            w = uart_.read()
            if w == b'\xab': #>>
                if selected_index < 4:
                    selected_index += 1
            if w == b'\xa0': #ok
                pass
            if w == b'\xbb': #<<
                if selected_index > 0:
                    selected_index -= 1
            if w == b'\x9b': #ESC
                break
        DrawKeyWindow(lcd,data,selected_index,keyslot)
        
def RunKeyViewer(lcd,uart_,pag = 0):
    eep = EEPROM(i2c, T24C256)
    data = eep[pag*256:(pag+1)*256]
    selected_index = 0
    DrawKeyViwer(lcd,pag,data,selected_index)
    while True:
        if (uart_.any()>0):
            w = uart_.read()
            if w == b'\xab': #>>
                if selected_index < 7:
                    selected_index += 1
                else:
                    pag += 1
                    selected_index = 0
                    data = eep[pag*256:(pag+1)*256]
            if w == b'\xa0': #ok
                slot_index = selected_index+pag*8
                slotdata = data[slot_index*32:(slot_index+1)*32]
                RunKeyWidown(lcd,uart_,slot_index,slotdata)
            if w == b'\xbb': #<<
                if selected_index > 0:
                    selected_index -= 1
                elif pag > 0:
                    pag -=1
                    selected_index = 7
                    data = eep[pag*256:(pag+1)*256]
            if w == b'\x9b': #ESC
                break
        DrawKeyViwer(lcd,pag,data,selected_index)
        
import random
from machine import Pin,I2C
from eeprom_i2c import EEPROM, T24C256
import fontlib
import Popups,Buttons
import ucryptolib

i2c = I2C(1,scl=Pin(9), sda=Pin(8),freq=400000)

def AutoGenerateKeyOnEmptySlot():
    eep = EEPROM(i2c, T24C256)
    keyslot = None
    key = None
    for pag in range(128):# 128 pages total
        pagdata = eep[pag*256:(pag+1)*256]
        for i_slot in range(8):
            slotdata = pagdata[i_slot*32:(i_slot+1)*32]
            if ((slotdata == b'\x00'*32) or (slotdata == b'\xFF'*32)):
                keyslot = i_slot+pag*8
                SaveKeyToEEPROM(Generatekey(),keyslot,eep=eep)
                key = GetKeyFromEEPROM(keyslot,eep = eep)
                break
        if key != None:
            break
    return (key,keyslot)

def Generatekey(seed=None):
    random.seed(seed)
    key = b''
    for i in range(16):
        key += random.getrandbits(32).to_bytes(2,'big')
    return key

def SaveKeyToEEPROM(key,slot_index,eep=None):
    if not eep:
        eep = EEPROM(i2c, T24C256)
    eep[slot_index*32:(slot_index+1)*32] = key

def GetKeyFromEEPROM(slot_index,eep=None):
    if not eep:
        eep = EEPROM(i2c, T24C256)
    return eep[slot_index*32:(slot_index+1)*32]

def EraseKey(slot_index):
    SaveKeyToEEPROM(b'\x00'*32,slot_index)
    
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


def DrawKeyWindow(lcd,keydata,indexpos,keyslot,buttonNames):
    lcd.fill(0)
    hexdata = keydata.hex()
    NamePairs = []
    for i in range(0,len(buttonNames),2):
        NamePairs.append((buttonNames[i],buttonNames[i+1]))
    for i in range(7):
        for j in range(5):
            bindex = (i+7*j)
            if bindex < 32:
                fontlib.printstring(hexdata[bindex*2:bindex*2+2],i*12+1,j*7,0,lcd.fbuf)

    for i in range(2):
        pair_choice = (indexpos//2)
        Buttons.DrawButton(lcd,6+37*i,36,NamePairs[pair_choice][i],selected = (indexpos ==  pair_choice*2+i))
    
    if indexpos < 2:
        fontlib.printstring("?",(42+38),37,0,lcd.fbuf,font="icons")
    else:
        fontlib.printstring(";",0,37,0,lcd.fbuf,font="icons")

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
    buttonNames = ["Import","Export","Random","Erase"]
    while True:
        if (uart_.any()>0):
            w = uart_.read()
            if w == b'\xab': #>>
                if selected_index < 3:
                    selected_index += 1
            if w == b'\n': #ok
                Option = buttonNames[selected_index]
                if Option == 'Import':
                    pass
                if Option == 'Export':
                    pass
                if Option == 'Random':
                    Q_Ans = Popups.Question(lcd,uart_,line1="Are you sure?",line2="key will be lost",Button1="Cancel",Button2=" Yep ")
                    print(Q_Ans)
                    if Q_Ans == ' Yep ':
                        SaveKeyToEEPROM(Generatekey(seed=None),keyslot)
                    data = GetKeyFromEEPROM(keyslot)
                if Option == 'Erase':
                    Q_Ans = Popups.Question(lcd,uart_,line1="Are you sure?",line2="key will be lost",Button1="Cancel",Button2=" Yep ")
                    if Q_Ans == ' Yep ':
                        EraseKey(keyslot)
                    data = GetKeyFromEEPROM(keyslot)
            if w == b'\xbb': #<<
                if selected_index > 0:
                    selected_index -= 1
            if w == b'\x1b': #ESC
                return('ESCAPE')
        DrawKeyWindow(lcd,data,selected_index,keyslot,buttonNames)
        
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
            if w == b'\n': #ok
                slot_index = selected_index+pag*8
                slotdata = data[slot_index*32:(slot_index+1)*32]
                RunKeyWidown(lcd,uart_,slot_index,slotdata)
                data = eep[pag*256:(pag+1)*256]
            if w == b'\xbb': #<<
                if selected_index > 0:
                    selected_index -= 1
                elif pag > 0:
                    pag -=1
                    selected_index = 7
                    data = eep[pag*256:(pag+1)*256]
            if w == b'\x1b': #ESC
                break
        DrawKeyViwer(lcd,pag,data,selected_index)

def chunks(string, length):
    return list(string[0+i:length+i] for i in range(0, len(string), length))

def EncryptBytearray(data,Key):
    enc = ucryptolib.aes(Key, 1) # Electronic Code Book (ECB).
    datalist = chunks(data, 32)
    if len(datalist[-1]) < 32:
        datalist[-1] = datalist[-1] + b'\x00' * (32 - (len(datalist[-1]) ))
    encrypted_List = []
    for data in datalist:
        encrypted_List.append(enc.encrypt(data))
    output = bytearray()
    for encrypteddbytes in encrypted_List:
        output.extend(encrypteddbytes)
    return(output)
        
def DecryptBytearray(data,Key):
    dec = ucryptolib.aes(Key, 1)
    encrypted_List = []
    for i in range(len(data)//32):
        encrypted_List.append(data[32*i:32*(i+1)])
    plain_text = bytearray()
    for encryptedbytes in encrypted_List:
        plain_text.extend(dec.decrypt(encryptedbytes))
    return plain_text

def DecryptBytearraytoString(data,Key):
    return DecryptBytearray(data,Key).decode().rstrip('\x00')

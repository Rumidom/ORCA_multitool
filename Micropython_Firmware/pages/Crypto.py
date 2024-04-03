import random
from machine import Pin,I2C
from eeprom_i2c import EEPROM, T24C256
import fontlib
import Popups,UI
import ucryptolib
from Control import UserControl
import hashlib
import sys

def Geteep(lcd,i2c):
    eep = None
    try:
        eep = EEPROM(i2c, T24C256)
    except Exception as e:
        Popups.Splash(lcd,[str(e)])
    return eep

def Generatekey(seed=None):
    # could use os.urandom(32)
    random.seed(seed)
    key = b''
    for i in range(16):
        key += random.getrandbits(32).to_bytes(2,'big')
    return key

def XOR_Bytearrays(X,Y):
    return bytes(a ^ b for (a, b) in zip(X, Y))

def SaveKeyToEEPROM(lcd,key,slot_index,eep):
    eep[slot_index*32:(slot_index+1)*32] = key

def GetKeyFromEEPROM(lcd,slot_index,eep):
    return eep[slot_index*32:(slot_index+1)*32]

def EraseKey(lcd,slot_index,eep):
    SaveKeyToEEPROM(lcd,b'\x00'*32,slot_index,eep)

def AutoGenerateKeyOnEmptySlot(lcd,eep):
    keyslot = None
    key = None
    for pag in range(128):# 128 pages total
        pagdata = eep[pag*256:(pag+1)*256]
        for i_slot in range(8):
            slotdata = pagdata[i_slot*32:(i_slot+1)*32]
            if ((slotdata == b'\x00'*32) or (slotdata == b'\xFF'*32)):
                keyslot = i_slot+pag*8
                SaveKeyToEEPROM(lcd,Generatekey(),keyslot,eep)
                key = GetKeyFromEEPROM(lcd,keyslot,eep)
                break
        if key != None:
            break
    return (key,keyslot)

def EraseEEPROM(lcd,eep):
    print("Erasing EEPROM")
    pagesize = 64
    pages = len(eep)/pagesize
    for i in range(pages):
        lcd.fill(0)
        fontlib.printstring("Erasing EEPROM",8,15,0,lcd.fbuf)
        fontlib.printstring('{:.2f} %'.format(((i+1)/pages)*100),25,25,0,lcd.fbuf)
        eep[i*pagesize:(i+1)*pagesize] = b'\x00'*pagesize
        lcd.show()

def chunks(string, length):
    return list(string[0+i:length+i] for i in range(0, len(string), length))

def EncryptBytearray(data,Key,Keynum):
    # 256 bit AES Cipher Block Chaining (CBC) 
    IV = hashlib.sha256(Keynum.to_bytes(32, sys.byteorder)).digest()
    enc = ucryptolib.aes(Key, 1)
    datalist = chunks(data, 32)
    if len(datalist[-1]) < 32:
        datalist[-1] = datalist[-1] + b'\x00' * (32 - (len(datalist[-1]) ))
    encrypted_List = []
    for data in datalist:
        XOR_data = XOR_Bytearrays(data,IV)
        encrypted_List.append(enc.encrypt(XOR_data))
        IV = XOR_data
    output = bytearray()
    for encrypteddbytes in encrypted_List:
        output.extend(encrypteddbytes)
    return(output)
        
def DecryptBytearray(data,Key,Keynum):
    # 256 bit AES Cipher Block Chaining (CBC) 
    IV = hashlib.sha256(Keynum.to_bytes(32, sys.byteorder)).digest()
    dec = ucryptolib.aes(Key, 1)
    encrypted_List = []
    for i in range(len(data)//32):
        encrypted_List.append(data[32*i:32*(i+1)])
    plain_text = bytearray()
    for encryptedbytes in encrypted_List:
        decrypted_PreXOR = dec.decrypt(encryptedbytes)
        plain_text.extend(XOR_Bytearrays(decrypted_PreXOR,IV))
        IV = decrypted_PreXOR
    return plain_text

def DecryptBytearraytoString(data,Key,Keynum):
    return DecryptBytearray(data,Key,Keynum).decode().rstrip('\x00')


class KeyWindow(UserControl):
    def __init__(self,lcd,uart_,eep):
        self.lcd = lcd
        self.uart = uart_
        self.eep = eep
        self.keydata = None
        self.keyslot = None
        self.selected_index = 0
        self.Menubuttons = ["Import","Export","Random","Erase"]
    def Ok_Func(self):
        Option = self.Menubuttons[self.selected_index]
        if Option == 'Import':
            return('Import')
        if Option == 'Export':
            return('Export')
        if Option == 'Random':
            Q_Ans = Popups.OptionChoice(self.lcd,self.uart,("Are you sure?","key will be lost"),('Yep','Cancel'))
            #print(Q_Ans)
            if Q_Ans == 'Yep':
                SaveKeyToEEPROM(self.lcd,Generatekey(),self.keyslot,self.eep)
            self.keydata = GetKeyFromEEPROM(self.lcd,self.keyslot,self.eep)
        if Option == 'Erase':
            Q_Ans = Popups.OptionChoice(self.lcd,self.uart,("Are you sure?","key will be lost"),('Yep','Cancel'))
            if Q_Ans == 'Yep':
                EraseKey(self.lcd,self.keyslot,self.eep)
            self.keydata = GetKeyFromEEPROM(self.lcd,self.keyslot,self.eep)
    def Left_Func(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            
    def Right_Func(self):
        if self.selected_index < 3:
            self.selected_index += 1
            
    def ESC_Func(self):
        return("ESCAPE")
    
    def DEL_Func(self):
        return("DELETE")

    def DrawKeyWindow(self):
        self.lcd.fill(0)
        hexdata = self.keydata.hex()
        for i in range(7):
            for j in range(5):
                bindex = (i+7*j)
                if bindex < 32:
                    fontlib.printstring(hexdata[bindex*2:bindex*2+2],i*12+1,j*7,0,self.lcd.fbuf)
        UI.BottomMenu(self.lcd,self.Menubuttons,self.selected_index,MenuActive = True)
        self.lcd.show()
        
    def Run(self,keydata,keyslot):
        self.keydata = keydata
        self.keyslot = keyslot
        while True:
            self.DrawKeyWindow()
            r = self.CheckKeyPress()
            if r != None:
                return r

        
class KeysBrowser(UserControl):
    def __init__(self,lcd,uart_,i2c):
        self.lcd = lcd
        self.uart = uart_
        self.i2c = i2c
        self.eep = Geteep(self.lcd,self.i2c)
        self.pag = 0
        self.Selectedindex = 0
        self.pagdata = self.eep[self.pag*256:(self.pag+1)*256]
        self.keywindow = KeyWindow(self.lcd,self.uart,self.eep)
        
    def DrawKeySlot(self,posx,posy,selected = False,empty = True,slot=0):
        self.lcd.rect(posx, posy, 33, 11, 1)
        self.lcd.line(posx+6, posy, posx+6, posy+10, 1)
        if not empty:
            fontlib.printchar("+",posx+1,posy+2,self.lcd.fbuf,font = "icons",invert = False)
        fontlib.printstring(f'{slot:04}',posx+8,posy+3,1,self.lcd.fbuf,invert = selected)
        self.lcd.line(posx+7, posy+1, posx+8+23, posy+1, 1)
        self.lcd.line(posx+7, posy+9, posx+8+23, posy+9, 1)
        
    def DrawKeyView(self):
        self.lcd.fill(0)
        for j in range(2):
            for i in range(4):
                empty_slot = True
                selected_slot = False
                slot_index = (i+4*j)
                slotdata = self.pagdata[slot_index*32:(slot_index+1)*32]
                if ((slotdata != b'\x00'*32) and (slotdata != b'\xFF'*32)):
                    empty_slot = False
                if (slot_index == self.Selectedindex):
                    selected_slot = True
                self.DrawKeySlot(34*j,12*i,selected = selected_slot,empty = empty_slot,slot=slot_index+self.pag*8)
        fontlib.printstring(f'P.',69,33,0,self.lcd.fbuf,invert = False)
        fontlib.printstring(f'{self.pag:03}',69,39,0,self.lcd.fbuf,invert = False)
        self.lcd.show()
        
    def Ok_Func(self):
        slot_index = self.Selectedindex+self.pag*8
        slotdata = self.pagdata[slot_index*32:(slot_index+1)*32]
        self.keywindow.Run(slotdata,slot_index)
        self.pagdata = self.eep[self.pag*256:(self.pag+1)*256] 
    
    def Left_Func(self):
        if self.Selectedindex > 0:
            self.Selectedindex -= 1
        elif self.pag > 0:
            self.pag -=1
            self.Selectedindex = 7
            self.pagdata = self.eep[self.pag*256:(self.pag+1)*256]
            
    def Right_Func(self):
        if self.Selectedindex < 7:
            self.Selectedindex += 1
        else:
            self.pag += 1
            self.Selectedindex = 0
            self.pagdata = self.eep[self.pag*256:(self.pag+1)*256]
            
    def ESC_Func(self):
        return("ESCAPE")
    
    def DEL_Func(self):
        return("DELETE")
        
    def Run(self):
        while True:
            self.DrawKeyView()
            r = self.CheckKeyPress()
            if r != None:
                return r
            

# TESTs
# Open key Browser
# View key
# Max pag 127


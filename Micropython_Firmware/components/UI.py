import fontlib
import math
import Helpers
import time

def BottomMenu(lcd,buttons,indexpos,MenuActive = True):
    Pairs = []
    for i in range(0,len(buttons),2):
        if (i+1) <= (len(buttons)-1):
            Pairs.append((buttons[i],buttons[i+1]))
        else:
            Pairs.append((buttons[i],None))
        
    for i in range(2):
        pair_choice = (indexpos//2)
        if Pairs[pair_choice][i] != None:
            DrawButton(lcd,6+37*i,38,Pairs[pair_choice][i],selected = ((indexpos ==  pair_choice*2+i) and MenuActive))
    
    if indexpos < 2:
        fontlib.printstring("?",80,39,0,lcd.fbuf,font="icons")
    else:
        fontlib.printstring(";",0,39,0,lcd.fbuf,font="icons")

def DrawIconIndexMenuOption(lcd,iy,Index,text,icon=" ",posx=3,selected = False):
    DrawMenuOption(lcd,iy,str(Index),selected = False)
    if Index < 2:
        Index = 2
    DrawIconMenuOption(lcd,iy,text,icon=icon,posx=5+5*math.ceil(math.log(Index+1, 10)),selected = selected)
            
def DrawIconMenuOption(lcd,iy,text,icon=" ",posx=3,selected = False):
    fontlib.printstring(text,posx+8,iy*9+1,0,lcd.fbuf,font = "five",invert = selected)
    fontlib.printstring(icon,posx,iy*9,0,lcd.fbuf,font = "icons",invert = False)

def DrawMenuOption(lcd,iy,text,posx=3,selected = False):
    fontlib.printstring(text,posx,iy*9+1,0,lcd.fbuf,font = "five",invert = selected)

def DrawButton(lcd,posx,posy,text,selected = False):
    lcd.rect(posx, posy, 36, 9, 1)
    halftextwidth = (len(text)*5)//2
    centered_posx = posx+18-halftextwidth
    fontlib.printstring(text,centered_posx,posy+2,0,lcd.fbuf,invert = selected)
    if selected:
        lcd.rect(posx+1, posy, 34, 9, 1)
        if len(text) <= 5:
            lcd.fill_rect(posx+2, posy, 16-halftextwidth, 9, 1)
            lcd.fill_rect(posx+18+halftextwidth, posy, 18-halftextwidth, 9, 1)

def DrawMenuCheckBox(lcd,yi,text,selected = False,checked = False):
    if len(text) < 13:
        text = text + " " * (13 - len(text))
    fontlib.printstring(text,3,(10*yi)+2,0,lcd.fbuf,font = "five",invert = selected)
    if checked:
        fontlib.printstring("_`a",68,10*yi+1,0,lcd.fbuf,font = "icons")
    else:
        fontlib.printstring("_^a",68,10*yi+1,0,lcd.fbuf,font = "icons")

def DrawMenuScrollOptions(lcd,yi,text,options,index,selected=False,change = False):
    op_text = options[index]
    if len(op_text) < 3:
        op_text =  " "+op_text + "  "
    elif len(op_text) < 5:
        op_text =  " "+op_text + " "

    if len(text) < 7:
        text = text + " " * (7 - len(text))
    fontlib.printstring(text,3,(10*yi)+2,0,lcd.fbuf,font = "five",invert = selected)
    DrawButton(lcd,44,10*yi,op_text,selected = change)
    if index == 0:
        fontlib.printstring("?",80,10*yi+1,0,lcd.fbuf,font="icons")
    elif index == (len(options)-1):
        fontlib.printstring(";",39,10*yi+1,0,lcd.fbuf,font="icons")
    else:
        fontlib.printstring(";",39,10*yi+1,0,lcd.fbuf,font="icons")
        fontlib.printstring("?",80,10*yi+1,0,lcd.fbuf,font="icons")
        
def DrawMenuNumberInput(lcd,yi,text,num = "",selected=False,change = False):
    if len(num) < 4:
        num = "_" * (4 - len(num)) + num
    if len(num) < 7:
        text = text + "_" * (4 - len(text))
    fontlib.printstring(text,3,(10*yi)+2,0,lcd.fbuf,font = "five",invert = selected)
    fontlib.printstring(num,62,(10*yi)+2,0,lcd.fbuf,font = "five",invert = change)

def DrawScrollBar(lcd,posx,posy,index,lineslen,ScreenMaxLines=4,Bartotal = 64):

    chunks = math.ceil(lineslen/ScreenMaxLines)
    if chunks == 0:
        chunks = 1
    chunkSize = Bartotal/chunks
    if chunkSize < 2:
        chunkSize = 2
    remainder = Bartotal-chunks*chunkSize
    thumbx = posx+math.ceil((index//ScreenMaxLines)*chunkSize)
    if lineslen > ScreenMaxLines:
        lcd.fill_rect(thumbx, posy, math.ceil(chunkSize+remainder), 4, 1)
        lcd.rect(posx, posy, Bartotal, 4, 1)
        
def Cursor(lcd,xi,yi,charwidth = 5,lineheight=7,spce=0,selected = False):
    fontlib.printstring("|",(charwidth+spce)*xi+1,(lineheight*yi),0,lcd.fbuf,invert = selected)
    
def PrintWrapedText(lcd,text_string,xi,yi,Screen_Width=84,charwidth = 5,lineheight=7,spce=0):
    Max_char = int(Screen_Width//charwidth)
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
        fontlib.printstring(line,(charwidth+spce)*xi+1,(lineheight*yi),0,lcd,font = "five")

def DrawPacketWindow(lcd,Packetdata,PacketRSSI,PacketNum,lineindex,decode=False,MaxLines = 5):
    hexdata = Packetdata.hex()
    decodeddata = Helpers.ASCII_Decode(Packetdata)
    bytesPerLine = 7
    bytesnum = len(hexdata)//2
    linesnum = bytesnum//bytesPerLine
    fontlib.printstring("S:"+str(bytesnum)+" RSSI:"+str(PacketRSSI),3,0,0,lcd.fbuf)
    for i in range(bytesPerLine):
        for j in range(lineindex,MaxLines+lineindex):
            bindex = (i+bytesPerLine*j)
            if bindex*2+2 <= len(hexdata):
                if decode:
                    fontlib.printstring(decodeddata[bindex],i*12+1,j*7+7-lineindex*7,0,lcd.fbuf)                
                else:
                    fontlib.printstring(hexdata[bindex*2:bindex*2+2],i*12+1,j*7+7-lineindex*7,0,lcd.fbuf)
    DrawScrollBar(lcd,10,42,lineindex+4,linesnum,ScreenMaxLines=5)
    
def DrawPacketMonitor(lcd,PacketList,PacketIndex,Pindex,scroll,MaxCharsPerLine=14):
    for i,packet in enumerate(PacketList[Pindex:Pindex+4]):
        icon = " "
        payload = packet[1]
        if packet[0] >= -40:
            icon = "k"
        elif packet[0] < -40 and packet[0] >-100:
            icon = "l"
        elif packet[0] <= -110:
            icon = "M"
        if (i == PacketIndex-Pindex):
            scroll = scroll%(len(packet[1])-MaxCharsPerLine)
            payload = packet[1][scroll:scroll+MaxCharsPerLine]
        j = i+Pindex
        DrawIconIndexMenuOption(lcd,i,j,Helpers.ASCII_Decode(payload),icon=icon,posx=3,selected = (i == PacketIndex-Pindex))

    DrawScrollBar(lcd,10,40,PacketIndex,len(PacketList))

def DrawBitmap(path,x,y,fbuf):
    file = open(path, "rb")
    filebytes = bytearray(file.read())
    file.close()
    bmptag = filebytes[0:2]
    dataOffset = int.from_bytes(filebytes[10:13],"little")
    size = (int.from_bytes(filebytes[18:22],"little"),int.from_bytes(filebytes[22:26],"little"))
    formt = int.from_bytes(filebytes[28:30],"little")
    #print("file:{} bmptag:{} formt:{} size:{}".format(path,bmptag,formt,size))
    if formt != 1 or bmptag != b'BM':
        raise Exception("Only 1 bit bitmaps are supported.")
    posx = x +size[0]
    posy = y
    bytes = size[0]*size[0]/8
    pallet = [1,0][b'\x00\x00\x00\xff\xff\xff\xff\xff' == filebytes[54:62]]
    print(pallet)
    for byte in reversed(filebytes[dataOffset:]):
        for i in range(8):
            if (byte >> i & 1):
                fbuf.pixel(posx,posy,pallet)
            else:
                fbuf.pixel(posx,posy,not pallet)
            posx-= 1
            if posx <= x:
                posx = x +size[0]
                posy += 1
    
def RunAnimation(pathList,x,y,lcd,interval):
    for path in pathList:
        lcd.fill(0)
        DrawBitmap(path,x,y,lcd.fbuf)
        lcd.show()
        time.sleep_ms(interval)
    

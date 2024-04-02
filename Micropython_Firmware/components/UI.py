import fontlib
import math

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

def DrawScrollBar(lcd,posx,posy,index,linesnum,ScreenMaxLines=4,Bartotal = 64):

    chunks = math.ceil(linesnum/ScreenMaxLines)
    if chunks == 0:
        chunks = 1
    chunkSize = Bartotal/chunks
    if chunkSize < 2:
        chunkSize = 2
    remainder = Bartotal-chunks*chunkSize
    thumbx = posx+math.ceil((index//ScreenMaxLines)*chunkSize)
    if linesnum > ScreenMaxLines:
        lcd.fill_rect(thumbx, posy, math.ceil(chunkSize+remainder), 4, 1)
        lcd.rect(posx, posy, Bartotal, 4, 1)
        
def DrawCursor(lcd,xi,yi,charwidth = 5,lineheight=7,spce=0,selected = False):
    fontlib.printstring("|",(charwidth+spce)*xi+1,(lineheight*yi),0,lcd.fbuf,invert = selected)
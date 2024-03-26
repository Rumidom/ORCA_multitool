import fontlib

def DrawButton(lcd,posx,posy,text,selected = False):
    lcd.rect(posx, posy, 36, 9, 1)
    fontlib.printstring(text,posx+18-((len(text)*5)//2),posy+2,0,lcd.fbuf,invert = selected)
    if selected:
        lcd.rect(posx+1, posy, 34, 9, 1)
        if len(text) <= 5:
            lcd.rect(posx+2, posy, 2, 9, 1)
            lcd.rect(posx+32, posy, 2, 9, 1)
            lcd.rect(posx+3, posy, 2, 9, 1)

def DrawMenuCheckBox(lcd,yi,text,selected = False,checked = False):
    
    if len(text) < 13:
        text = text + " " * (13 - len(text))
    fontlib.printstring(text,3,(10*yi)+2,0,lcd.fbuf,font = "five",invert = selected)
    if checked:
        fontlib.printstring("_^a",68,10*yi+1,0,lcd.fbuf,font = "icons")
    else:
        fontlib.printstring("_`a",68,10*yi+1,0,lcd.fbuf,font = "icons")

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
        
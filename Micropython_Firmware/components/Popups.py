import fontlib,Buttons
import utime

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
    
def DrawQuestion(lcd,index,lines,Options = (None,None)):
    lcd.fill(0)
    if Options[0] != None and Options[1] == None:
        Buttons.DrawButton(lcd,24,25,Options[0],selected = (index == 0))
    if Options[0] != None and Options[1] != None:
        Buttons.DrawButton(lcd,6,25,Options[0],selected = (index == 0))
    if Options[0] != None:
        Buttons.DrawButton(lcd,43,25,Options[1],selected = (index == 1))
    DisplayCenteredLines(lcd,lines)
    lcd.show()
    
def Question(lcd,uart1,lines,Options = (None,None)):
    selected_index = 0
    while True:
        if (uart1.any()>0):
            w = uart1.read()
            if w == b'\xab' and Options[1] != None: #>>
                if selected_index < 1:
                    selected_index += 1
            if w == b'\n': #ok
                return(Options[selected_index])
            if w == b'\xbb'and Options[1] != None: #<<
                if selected_index > 0:
                    selected_index -= 1
            if w == b'\x9b': #ESC
                return("ESCAPE")
        DrawQuestion(lcd,selected_index,lines,Options = Options)

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
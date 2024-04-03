import fontlib
from Control import UserControl

class Menu(UserControl):
    def __init__(self,lcd,uart_,MenuOptions):
        self.lcd = lcd
        self.uart = uart_
        self.menupos = 0
        self.SelectedIndex = 0
        self.MenuOptions = MenuOptions
        self.MenuLen = len(MenuOptions)
        self.maxrows = 7
        
    def Ok_Func(self):
        return(self.MenuOptions[self.SelectedIndex])
        
    def Left_Func(self):
        if self.SelectedIndex > 0:
            self.SelectedIndex -= 1
        
    def Right_Func(self):
        if self.SelectedIndex < (self.MenuLen-1):
            self.SelectedIndex += 1
    
    def BKSP_Func():
        return("BKSP")
        
    def ESC_Func(self):
        return("ESCAPE")
    
    def DEL_Func(self):
        return("DELETE")
        
    def Input_Func(self,w):
        return("INPUT")
    
    def DrawMenu(self):
        self.lcd.fill(0)

        if (self.SelectedIndex > (self.maxrows-1)):
            self.menupos = self.SelectedIndex - (self.maxrows-1)
            self.SelectedIndex = (self.maxrows-1)
            
        for i,item in enumerate(self.MenuOptions[self.menupos:self.maxrows+self.menupos]):
            if i == self.SelectedIndex:
                fontlib.printstring(item,3,i*7,0,self.lcd.fbuf,font = "five",invert = True)
            else:
                fontlib.printstring(item,3,i*7,0,self.lcd.fbuf,font = "five")
        self.lcd.show()
    
    def Run(self):
        while True:
            self.DrawMenu()
            r = self.CheckKeyPress()
            if r != None:
                return r
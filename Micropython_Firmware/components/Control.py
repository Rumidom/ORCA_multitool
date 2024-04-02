import os

class UserControl():
    def has_method(self, name):
        return callable(getattr(self, name, None))

    def CheckKeyPress(self,DrawFunction=None):
        r = None
        if (self.uart.any()>0):
            w = self.uart.read()
            if self.has_method('Ok_Func') and w == b'\n': #OK
                r = self.Ok_Func()
            elif self.has_method('Right_Func') and w == b'\xab': #>>
                r = self.Right_Func()
            elif self.has_method('Left_Func') and w == b'\xbb': #<<
                r = self.Left_Func()
            elif self.has_method('BKSP_Func') and w == b'\x08': #BKSP
                r = self.BKSP_Func()
            elif self.has_method('ESC_Func') and w == b'\x1b': #ESC
                r = self.ESC_Func()
            elif self.has_method('DEL_Func') and w == b'\x7f': #DEL
                r = self.DEL_Func()
            else:
                r = self.Input_Func(w)
            if DrawFunction:
                DrawFunction()
        return r

'''
class ClassName(UserControl):
    def __init__(self,lcd,uart_):
        self.lcd = lcd
        self.uart = uart_

    def Ok_Func(self):
        return("OK")
        
    def Left_Func(self):
        return("LEFT")
        
    def Right_Func(self):
        return("RIGHT")
    
    def BKSP_Func():
        return("BKSP")
        
    def ESC_Func(self):
        return("ESCAPE")
    
    def DEL_Func(self):
        return("DELETE")
        
    def Input_Func(self,w):
        return("INPUT")
    
    def Run(self):
        while True:
            self.DrawFunction()
            self.CheckKeyPress()
            r = self.CheckKeyPress()
            if r != None:
                return r
'''
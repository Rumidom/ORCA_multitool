import Buttons,Popups
import os,json

def DrawConfig(lcd,Config,Configkeys,ConfigOptions,selected_index,change_config=False):
    lcd.fill(0)
    SelectList = [x == selected_index for x in range(4)]
    for i,key in enumerate(Configkeys):
        if isinstance(ConfigOptions[key], list):
            Buttons.DrawMenuScrollOptions(lcd,i,key,ConfigOptions[key],Config[key],selected=SelectList[i],change = (selected_index == i and change_config))
        elif ConfigOptions[key] == "Num":
            Buttons.DrawMenuNumberInput(lcd,i,key,num = Config['DefaultKey'],selected=SelectList[i],change = (selected_index == i and change_config))
    lcd.show()

def GetDeviceConfig():
    Config = {"DefaultKey":"","Save To":2,"Encrypt":0,"Use Key":2}
    noConfigFile = True
    for file in os.listdir("/"):
        if file == 'Device.conf':
            noConfigFile = False
            with open("Device.conf", 'r') as f:
                Config = json.loads(f.read())
            break
    if noConfigFile:
        with open("Device.conf", 'w') as f:
            f.write(json.dumps(Config))
    return Config
            
def RunDeviceConfig(lcd,uart_):
    numberskeys = ['q','w','e','r','t','y','u','i','o','p']
    ConfigOptions = {"DefaultKey":"Num","Use Key":["Defaut","Ask","Auto"],"Encrypt":["Yes","No","Ask"],"Save To":["Card","Flash","Both"]}
    Configkeys = ["Save To","Encrypt","Use Key","DefaultKey"]
    Config = GetDeviceConfig()
    selected_index = 0
    change_config = False
    key = Configkeys[selected_index]
    while True:
        if (uart_.any()>0):
            w = uart_.read()
            if w == b'\xbb': #<<
                if change_config:
                    if isinstance(ConfigOptions[key], list):
                        key = Configkeys[selected_index]
                        if (Config[key] > 0):
                            Config[key] -= 1
                else:
                    if selected_index > 0:
                        selected_index -= 1
                        key = Configkeys[selected_index]
            elif w == b'\n': #Ok/Enter
                change_config = not change_config
            elif w == b'\xab': #>>
                if change_config:
                    if isinstance(ConfigOptions[key], list):
                        
                        if (Config[key] < len(ConfigOptions[key])-1):
                            Config[key] += 1
                else:
                    if selected_index < (len(Configkeys)-1):
                        selected_index += 1
                        key = Configkeys[selected_index]
            elif w == b'\x1b': #ESC
                if int(Config['DefaultKey']) > 1023:
                    Popups.Splash(lcd,["Null DefaultKey","More than 1023"])
                else:
                    Popups.Splash(lcd,[None,"Saving Config"])
                    with open("Device.conf", 'w') as f:
                        f.write(json.dumps(Config))
                    return("ESCAPE")
            elif w == b'\x08': #BKSP
                if ConfigOptions[key] == "Num":
                    Config[key] = Config[key][1:]
            elif w == b'\x7f': #DEL
                if ConfigOptions[key] == "Num":
                    Config[key] = ""               
            else:
                if ConfigOptions[key] == "Num" and change_config:
                    decode = w.decode().lower()
                    for i,c in enumerate(numberskeys):
                        if (decode == str(i) or decode == c):
                            Config[key] = Config[key]+str(i)
                            if len(Config[key]) > 4:
                                Config[key] = Config[key][1:]
        DrawConfig(lcd,Config,Configkeys,ConfigOptions,selected_index,change_config)

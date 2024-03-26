# ORCA Multitool 

ORCA (Operational Resilient Computing Asset) is a Opensource portable multitool/cyberdeck. Weather you need a mission logger, send a message back to Star Command or just need to diagnose broken critical space hardware this device might be useful to you.

## Hardware Features
- WIFI & Bluetooh (ESP32 S3)
- QWERTY keyboard
- EEPROM
- Expansion/periferal ports (including STEMMA QT)
- SX1278 Radio
- Micro SD card slot
- real-time clock IC

## ORCA V1
First version of the PCB had a lot of mistakes, I'm working on a V2, do not recomend using V1 at all. I'm currently developing the firmware on a modded version of the device.

<p align="center">
<img src='./Photos/ORCA V1.png' width='600'>
</p>

## Design Goals
- Nice easy to use UI
- Low power
- All tools should be able to save/read plaintext/encrypted files on the SD card/Flash
  
## TODO
- Device Info
- [x] Displays available/used Ram, available/used Flash, available/used SD Card space, Device MAC Address
- Cryptograpfy
- [x] View, Generate, Delete 32 Byte AES keys on the EEPROM
- [x] AES File Encryption/Decryption using EEPROM keys
- NotePad
- [ ] Create, Load, Edit files on the SDCard/Flash
- LORA Tools
- [ ] LORA Monitor (Recieve and display recieved lora packets)
- [ ] LORA Sender (Sends lora packets)
- [ ] LORA Menssager (Sends and Recives Encrypted Messages, On a Chatapp-like UI)
- I2C Tools
- [ ] I2C Scanner
- [ ] I2C Monitor (Recive and display I2C data)
- [ ] I2C Sender (Sends packets over the I2C bus)
- [ ] I2C Screen Tester (Tests commonly available screens)
- Serial Tools
- [ ] Serial Monitor
- WIFI Tools
- ESP-now Tools
- Bluetooth Tools
  

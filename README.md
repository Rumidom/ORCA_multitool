# ORCA Multitool 

ORCA (Operational Resilient Computing Asset) is a Opensource portable multitool/cyberdeck. Whether you need a mission logger, send a message back to Star Command or just diagnose broken critical space hardware this device got you covered.

## Hardware Features
- WIFI & Bluetooh (ESP32 S3)
- QWERTY keyboard
- EEPROM
- Expansion/periferal ports (including STEMMA QT)
- SX1278 Radio
- Micro SD card slot
- Real-time clock IC

## ORCA V1
First version of the PCB had a lot of mistakes, I'm working on a V2, do not recomend using V1 at all. I'm currently developing the firmware on a modded version of the device.

<p align="center">
<img src='./Photos/ORCA V1.png' width='600'>
</p>

## BOM List:
[ESP32 S3 N16R8](https://s.click.aliexpress.com/e/_DD4kUg9)\
[SX1278 LORA radio](https://s.click.aliexpress.com/e/_DDBJqpf)

## Design Goals
- Nice easy to use UI
- Low power
- All tools should be able to save/read plaintext/encrypted files on the SD card/Flash
  
## TODO
- Device Info
- [x] Displays available/used Ram, available/used Flash, available/used SD Card space, Device MAC Address
- Cryptograpfy
- [x] View, Generate, Delete 256 bit AES keys on the EEPROM
- [x] AES File Encryption/Decryption using EEPROM keys
- NotePad
- [x] Create, Load, Edit files on the SDCard/Flash
- LORA Tools
- [x] LORA Monitor (Recieve,Display and Save recieved lora packets)
- [ ] LORA Sender (Sends lora packets)
- [ ] LORA Menssager (Sends and Recives Encrypted Messages, On a Chatapp-like UI)
- OOK/FSK/ASK Tools
- [ ] OOK/FSK/ASK Monitor (Recieve,Display and Save recieved OOK/FSK/ASK packets)
- [ ] OOK/FSK/ASK Sender (Sends OOK/FSK/ASK packets)
- I2C Tools
- [ ] I2C Scanner
- [ ] I2C Monitor (Recive and display I2C data)
- [ ] I2C Sender (Sends packets over the I2C bus)
- [ ] I2C Screen Tester (Tests commonly available screens)
- Serial Tools
- [ ] Serial Monitor
- WIFI Tools
- [ ] SSID Scanner/Signal Strength Meter
- ESP-NOW Tools
- IR Tools
- Bluetooth Tools
- Games
- [ ] Space invaders
- [ ] Lunar Lander
- Other Features
- [ ] OTP Generator (Creates a time based one time password from a file, encrypted or not)
  
## Donating:
Help me pay for prototyping costs by becoming a sponsor or using the referal links on the BOM list

## License:
the ORCA Project is [MIT licensed](https://github.com/Rumidom/ORCA_multitool/blob/main/LICENSE).


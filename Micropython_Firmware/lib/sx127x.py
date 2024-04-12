from time import sleep, ticks_ms
from machine import SPI, Pin
from micropython import const
import gc

# registers (Datasheet pag 90 - Description of the Registers)

REGFIFO = const(0x00) #FIFO REGISTER (Default: 0x00)
REGOPMODE = const(0x01) #OPERATION MODE REGISTER (Default: 0x01)(Can only be modified on Sleep mode)
                        #(BIT_7):     0 => FSK/OOK Mode       1 => LoRaTM Mode
                        #(BIT 6-5):  00 => FSK mode          01 => OOK mode
                        #(BIT 3):     1 => LOW Freq mode      0 => HIGH freq mode
                        #(BIT 2-0): 000 => Sleep mode       001 => Stdby mode 010 => FS mode TX (FSTx)
                        #           011 => Tx mode          100 => FSRX mode
                        #           101 => Rx mode          110 => Rx Single mode (Just LORA)
                        #           111 => Channel activity detection (Just LORA)
REGBITRATEMSB = const(0x02) #BITRATE SETTING MSB (FSK) (Default: 4.8 kb/s [0x1a,0x0b])
REGBITRATELSB = const(0x03) #BITRATE SETTING LSB (FSK)
REGFREQDEVIATIONMSB = const(0x04) #FREQUENCY DEVIATION MSB (FSK)
REGFREQDEVIATIONLSB = const(0x05) #FREQUENCY DEVIATION LSB (FSK)
REGFRFMSB = const(0x06) #RF CARRIER FREQUENCY MSB (FSK & LORA) (Default: 434.000 MHz)
REGFRFMID = const(0x07) #RF CARRIER FREQUENCY MID (FSK & LORA) The RF frequency is taken into account internally only when 
REGFRFLSB = const(0x08) #RF CARRIER FREQUENCY LSB (FSK & LORA) re-starting the receiver or entering FSRX/FSTX modes
REGPACONFIG = const(0x09) #OUTPUT POWER CONTROL (FSK & LORA)
REGFSKRSSITHRESH = const(0x10) #RSSI TRIGGER LEVEL FOR THE RSSI INTERRUPT (FSK)
REGLNA = const(0x0C) #LNA SETTINGS (FSK & LORA)
REGFIFOADDRPTR = const(0x0D) #AFC, AGC, SETTINGS / FIFO SPI POINTER (FSK / LORA)
REGRXCONFIG = const(0x0D) #AFC, AGC, SETTINGS / FIFO SPI POINTER (FSK / LORA)
                          #(BIT 4)     1 => AfcAutoOn  automatic frequency correction (AFC) (Default: 0)
                          #(BIT 3)     1 => AgcAutoOn  automatic gain control (AGC) (Default: 1)
                          #(BIT 2-0) 000 => RxTrigger None 001 => Rx Rssi Trigger 110 => PreambleDetect 111 => Rssi Trigger & PreambleDetect
REGAFCFEI = const(0x1a) #AFC AND FEI CONTROL
                        #(BIT 4) AgcStart() Triggers an AGC sequence when set to 1.
                        #(BIT 1) AfcClear() Clear AFC register set in Rx mode. Always reads 0.
                        #(BIT 0) AfcAutoClearOn AFC register is cleared at the beginning of the automatic AFC phase
REGRSSICONFIG = const(0x0E) #RSSI CONFIG/START TX DATA (FSK/LORA)
REGFIFOTXBASEADDR = const(0x0E) #RSSI CONFIG/START TX DATA (FSK/LORA)
REGFIFORXBASEADDR = const(0x0F) #RSSI COLLISION DETECTOR/START RX DATA (FSK/LORA)
REGFIFORXCURRENTADDR = const(0x10) #RSSI THRESHOLD CONTROL/START ADDRESS OF LAST PACKET RECEIVED (FSK / LORA)
REGRSSIVALUE = const(0x11) #CURRENT ABSOLUTE VALUE OF THE RSSI IN DBM, 0.5DB STEPS (FSK)/ OPTIONAL IRQ FLAG MASK (FSK / LORA)
REGIRQFLAGS = const(0x12) #CHANNEL FILTER BW CONTROL / IRQ FLAGS (FSK / LORA)
REGRXNBBYTES = const(0x13) #AFC CHANNEL FILTER BW / NUMBER OF RECEIVED BYTES (FSK / LORA)
REGOOKPEAK = const(0x14) #OOK DEMODULATOR / NUMBER OF VALID HEADERS RECEIVED MSB (FSK / LORA)
                         #(BIT 5) 1 => Enables the Bit Synchronizer.
REGOOKFIX = const(0x15) #THRESHOLD OF THE OOK DEMOD / NUMBER OF VALID HEADERS RECEIVED LSB (FSK / LORA)
REGOOKAVG = const(0x16) #AVERAGE OF THE OOK DEMOD / NUMBER OF VALID PACKETSRECEIVED MSB (FSK / LORA)
REGPKTRSSIVALUE = const(0x1A) #AFC AND FEI CONTROL / RSSI OF LAST PACKET (FSK / LORA)
REGPKTSNRVALUE = const(0x19) #ESTIMATION OF LAST PACKET SNR (FSK / LORA)
REGMODEMCONFIG1 = const(0x1D) #VALUE OF THE CALCULATED FREQUENCY ERROR / MODEM_CONFIG (FSK / LORA)
REGMODEMCONFIG2 = const(0x1E)
REGPREAMBLEDETECT = const(0x1f) #PREAMBLE_DETECT SETTINGS / SIZE OF PREAMBLE (FSK / LORA)
                                #(BIT 7) (Enables Preamble detector when set to 1. The AGC settings supersede this bit during the startup )
                                #(BIT 6-5) (Number of Preamble bytes to detect to trigger an interrupt)
                                #BIT 4-0:
REGPREAMBLEMSB = const(0x20) #TIMEOUT RX REQUEST AND RSS / SIZE OF PREAMBLE (FSK / LORA)
REGPREAMBLELSB = const(0x21) #TIMEOUT RSSI AND PAY-LOADREADY / SIZE OF PREAMBLE (FSK / LORA)
REGPAYLOADLENGTH_LORA = const(0x22) #TIMEOUT RSSI AND SYNCADDRESS / LORATM PAYLOAD LENGTH (FSK / LORA)
REGFIFORXBYTEADDR = const(0x25) #PREAMBLE LENGTH, MSB / ADDRESS OF LAST BYTE WRITTEN IN FIFO (FSK / LORA)
REGPREAMBLEMSB_FSK = const(0x25)
REGMODEMCONFIG3 = const(0x26) #PREAMBLE LENGTH, MSB / MODEM PHY CONFIG 3 (FSK / LORA)
REGPREAMBLELSB_FSK = const(0x26)

REGSYNCCONFIG = const(0x27)#SYNC WORD RECOGNITION CONTROL (FSK)
                                 #(bit 7) 00 => automatic restart of the receiver OFF 01 =>  On, without waiting for the PLL to re-lock,10 => SYNC WORD On, wait for the PLL to lock (frequency changed)
                                 #(bit 5)  0 => PreamblePolarity 0xAA                  1 => PreamblePolarity0x55 (default:0xAA)
                                 #(bit 4)  0 => SYNC WORD OFF                          1 => SYNC WORD ON
REGSYNCVALUE1 = const(0x28) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE2 = const(0x29) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE3 = const(0x2A) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE4 = const(0x2B) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE5 = const(0x2C) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE6 = const(0x2D) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE7 = const(0x2E) #SYNC WORD BYTES 1 - 8 (FSK)
REGSYNCVALUE9 = const(0x2F) #SYNC WORD BYTES 1 - 8 (FSK)
RSSIWIDEBAND = const(0x2C) #WIDEBAND RSSI MEASUREMENT (LORA)


REGFSKPACKETCONFIG1 = const(0x30)#PACKET MODE SETTINGS (FSK)
                                 #BIT 7: (Defines the packet format used: Variable or Fixed length)
                                 #BIT 6-5:(Defines DC-free encoding/decoding performed)
                                 #BIT 4:(Enables CRC calculation/check (Tx/Rx))
                                 #BIT 3:(Defines the behavior of the packet handler when CRC check fails)
                                 #BIT 2-1:(Defines address based filtering in Rx)
                                 #BIT 0:(Selects the CRC and whitening algorithms)
REGFSKPACKETCONFIG2 = const(0x31)#PACKET MODE SETTINGS (FSK)
                                 #BIT 7:(Not Used)
                                 #BIT 6:(Data processing mode: Continuous mode, Packet mode)
                                 #BIT 5:(Enables the io-homecontrol® compatibility mode)
                                 #BIT 4:(reserved - Linked to io-homecontrol® compatibility mode)
                                 #BIT 3:(Enables the Beacon mode in Fixed packet format)
                                 #BIT 2-1:( Packet Length Most significant bits)
REGINVERTIQ = const(0x33) #INVERT LORA I AND Q SIGNALS (LORA)
REGINVERTIQ2 = const(0x3B)
REG_PAYLOADLENGTH_FSK = const(0x32) #PAYLOAD LENGTH SETTING (FSK)
REGFIFOTHRESHOLD_FSK = const(0x35) #DEFINES THE CONDITION TO START PACKET TRANSMISSION (FSK)
REGDETECTIONOPTIMIZE = const(0x31) #LORA DETECTION OPTIMIZEFOR SF6 (LORA)
REGDETECTIONTHRESHOLD = const(0x37) #LoRa detection threshold
 0x0A => SF7 to SF12 0x0C => SF6
REGIRQFLAGS1_FSK = const(0x3e) #FSK IRQ FLAGS
REGIRQFLAGS2_FSK = const(0x3f) #FSK IRQ FLAGS
REGSYNCWORD_LORA = const(0x39) #LORA SYNC WORD (LORA)
REGDIOMAPPING1 = const(0x40) #Mapping of pins DIO0 to DIO3(LORA & FSK)
                             #BITS 7-6 Table 18
REGDIOMAPPING2 = const(0x41) #Mapping of pins DIO4,DIO5 & MapPreambleDetect(LORA & FSK)
                             #BITS 7-6 (CONTINUOUS MODE )Table 29 and Table 30
REGVERSION = const(0x42) #SEMTECH ID RELATING THE SILICON REVISION

class SX127x:

    def __init__(self, spi, ss, rst, freq, dio_0 = None,dio_1 = None,dio_2 = None,RadioMode = 'LORA'):
        self.spi = spi
        
        if dio_0:
            self.dio0 = Pin(dio_0, Pin.IN)
        if dio_1:
            self.dio1 = Pin(dio_1, Pin.IN)
        if dio_2:
            self.dio2 = Pin(dio_2, Pin.IN)
            
        self.pin_ss = Pin(ss, Pin.OUT)
        self.pin_rst = Pin(rst, Pin.OUT)
        self.pin_ss.on()
        
        self.implicit_header_mode = None
        self.tx_power_level = 14
        self.version = None
        self.signal_bandwidth = 125e3
        self.spreading_factor = 9       
        self.invertIQ = False
        self.frequency = freq
        self.frequency_offset = 0
        self.coding_rate = 5
        self.preamble_length = 8
        self.sync_word = 0x12
        self.enable_CRC = True
        self.RadioMode = RadioMode
        
        
        self.OpModes = [['SLEEP','STDBY','FSTX','TX','FSRX','RX'],
                        ['SLEEP','STDBY','FSTX','TX','FSRX','RXCONT','RXSING','CAD']]
        
        self.RadioModes = ['FSK','LORA','OOK']
        
        #perform reset
        self.pin_rst.off()
        sleep(0.01)
        self.pin_rst.on()
        sleep(0.01)
        
        # check version
        for i in range(5):
            self.version = self.readRegister(REGVERSION)
            if self.version:
                break
            
        # debug output
        print("SX version: {}".format(self.version))

        # put in sleep mode
        self.SetTransceiverMode('SLEEP')

        # set radio mode
        self.SetRadioMode(self.RadioMode)
        
        # config
        self.setFrequency(freq)
        self.setTxPower(self.tx_power_level)
        
        if self.RadioMode == 'LORA':
            self.Lora_Init()
        if self.RadioMode == 'FSK':
            self.FSK_Init()
        if self.RadioMode == 'OOK':
            self.OOK_Init()
            
        self.SetTransceiverMode('STDBY')
        

        
    def Lora_Init(self):
        
        #self.setSignalBandwidth(self.parameters["signal_bandwidth"])
        # set LNA boost 0x03 is highest gain
        self.writeRegister(REGLNA, self.readRegister(REGLNA) | 0x03)
        # set auto AGC (automatic gain control, negates LNA boost setting)
        self.writeRegister(REGMODEMCONFIG3, 0x04)

        # set base addresses
        self.writeRegister(REGFIFOTXBASEADDR, 0x00)
        self.writeRegister(REGFIFORXBASEADDR, 0x00)
        
        # set LowDataRateOptimize flag if symbol time > 16ms (default disable on reset)
        # self.writeRegister(REGMODEMCONFIG3, self.readRegister(REGMODEMCONFIG3) & 0xF7)  # default disable on reset
        bw = self.signal_bandwidth
        sf = self.spreading_factor
        if 1000 / bw / 2 ** sf > 16:
            self.writeRegister(REGMODEMCONFIG3, self.readRegister(REGMODEMCONFIG3) | 0x08)
    
    def FSK_Init(self,SyncWordComp = False,PreambDetect = False,CheckCRC = False,Continuous= True):
        self.SetTransceiverMode('STDBY')
        self.FSK_SetSyncword_On(SyncWordComp)
        #self.FSK_SetPreamble_On(PreambDetect)
        self.FSK_SetCRC_On(CheckCRC)
        #self.FSK_SetContinuousMode_On(Continuous)
        self.FSK_SetPacketFormatVariable(False)
        pass

    def OOK_Init(self,BitSync= True):
        self.FSK_Init()
        self.OOK_SetBitSynchronizer_On(BitSync)
        pass
    
    def getActiveModem(self):
        OpMode = self.readRegister(REGOPMODE)
        return(["LORA","FSK/OOK"][OpMode << 7 & 1])

    def SetRadioMode(self,Rmode):
        self.SetTransceiverMode('SLEEP')
        if self.RadioMode == "LORA":
            self.writeRegister(REGOPMODE,self.readRegister(REGOPMODE) | 0b10000000)
        elif self.RadioMode == "FSK":
            self.writeRegister(REGOPMODE,((self.readRegister(REGOPMODE) & 0b10011111)))
        elif self.RadioMode == "OOK":
            self.writeRegister(REGOPMODE,((self.readRegister(REGOPMODE) & 0b10011111) | 0b00100000))   
        else:
            raise Exception("Invalid Radio Mode")
        self.RadioMode = Rmode
        self.SetTransceiverMode('STDBY')
        
    def SetTransceiverMode(self,mode):
        OpMode = self.readRegister(REGOPMODE)
        #print(regOPMode >> 7,mode)
        mode_bin = self.OpModes[OpMode >> 7 & 1].index(mode)

        self.writeRegister(REGOPMODE, (self.readRegister(REGOPMODE) & 0b11111000) | mode_bin)
        return(self.readRegister(REGOPMODE))
    
    def PrintOpMode(self):
        OpMode = self.readRegister(0x01)
        print("-------------------------------------")
        print("RegOpMode:",'{:08b}'.format(OpMode))
        print("-------------------------------------")
        print("OpMode: ",["FSK","OOK","LORA"][((OpMode >> 7)*2)+((OpMode & 0b01100000)>>5)])
        print("Freq Mode: ",["HIGH Freq","LOW Freq"][OpMode >> 3 & 1])
        print("Transciver :",self.OpModes[OpMode >> 7 & 1][OpMode & ((1 << 3) - 1)])
        
    def PrintFSKPktMode(self):
        RegPktMode1 = self.readRegister(REGFSKPACKETCONFIG1)
        print("-------------------------------------")
        print("RegPktConfig1:",'{:08b}'.format(RegPktMode1))
        print("-------------------------------------")
        print("PacketFormat: ",["Fixed length","Variable length"][RegPktMode1 >> 7 & 1])
        print("Encod/Decod: ",["None","Manchester","Whitening"][(RegPktMode1 & 0b01100000)>>5])
        print("CRC Check:",["Off","On"][RegPktMode1 >> 4 & 1])
        
        RegPktMode2 = self.readRegister(REGFSKPACKETCONFIG2)
        print("-------------------------------------")
        print("RegPktConfig2:",'{:08b}'.format(RegPktMode2))
        print("-------------------------------------")
        print("DataMode: ",["Continuous mode","Packet mode",][RegPktMode2 >> 6 & 1])
        print("PayloadLength: ",RegPktMode1 << 8 |self.readRegister(PAYLOADLENGTH_FSK))

    def PrintFSKIRQFlags(self):
        FSKIrqFlags1 = self.GetFSKIrqFlags1()
        FSKIrqFlags2 = self.GetFSKIrqFlags2()
        print("-------------------------------------")
        print("FSKIrqFlags1:",'{:08b}'.format(FSKIrqFlags1))
        print("FSKIrqFlags2:",'{:08b}'.format(FSKIrqFlags2))
        print("-------------------------------------")
        print("Mode Ready: ",["False","True"][FSKIrqFlags1 >> 7 & 1])
        print("RxReady: ",["False","True"][FSKIrqFlags1 >> 6 & 1])
        print("TxReady: ",["False","True"][FSKIrqFlags1 >> 5 & 1])
        print("RssiThresholdExceded: ",["False","True"][FSKIrqFlags1 >> 3 & 1])
        print("PreambleDetected: ",["False","True"][FSKIrqFlags1 >> 1 & 1])
        print("FifoFull: ",["False","True"][FSKIrqFlags2 >> 7 & 1])
        print("FifoEmpty: ",["False","True"][FSKIrqFlags2 >> 6 & 1])
        print("PacketSent: ",["False","True"][FSKIrqFlags2 >> 3 & 1])
        print("PayloadReady: ",["False","True"][FSKIrqFlags2 >> 2 & 1])
        print("CrcOk: ",["False","True"][FSKIrqFlags2 >> 1 & 1])
        
    def PrintSyncWConf(self):
        syncwconf = self.readRegister(REGSYNCCONFIG)
        print("SyncWord Detect/Generate:",["Off","On"][syncwconf >> 4 & 1])

    def PrintPreambleConf(self):
        preambleconf = self.readRegister(REGPREAMBLEDETECT)
        print("Preamble Detector: ",["Off","On"][preambleconf >> 7 & 1])
        print("Preamble Detector Size:",(preambleconf & 0b01100000)>>5, "bytes")    

           
    def WriteToFIFO(self, buffer):
        currentLength = self.readRegister(REGPAYLOADLENGTH_LORA)
        size = len(buffer)

        # check size
        size = min(size, (255 - currentLength))

        # write data
        for i in range(size):
            self.writeRegister(REG_FIFO, buffer[i])

        # update length
        #self.writeRegister(REGPAYLOADLENGTH_LORA, currentLength + size)
        return size

    def Send(self,data):
        if isinstance(data, str):
            data = data.encode()
        data_len = len(data)
        
        #set mode to standby
        self.SetTransceiverMode('STDBY')
        modem = self.getActiveModem()
        
        #clear IRQ Flags
        self.ClearIRQFlags(m = modem)
        
        #toa = getTimeOnAir(data_len)
        self.writeRegister(REGDIOMAPPING1,0b00000000)
        self.writeRegister(REGDIOMAPPING2,0b00000000)
        
        timeout = 0
        if(modem == 'LORA'):
            # calculate timeout in ms (150 % of expected time-on-air)
            #timeout = (toa * 1.5) / 1000;
            timeout = 5000
            self.writeRegister(REGFIFOADDRPTR, 0b00000000  )
            self.writeRegister(REGFIFOTXBASEADDR, 0b00000000  )
            self.writeRegister(REGPAYLOADLENGTH_LORA, data_len)
        elif(modem == "FSK/OOK"):
            #calculate timeout in ms (5ms + 500 % of expected time-on-air)
            #timeout = 5 + (toa * 5) / 1000;
            timeout = 5000
            #set payload lenght only needed in fixed packet length
            self.writeRegister(PAYLOADLENGTH_FSK, data_len)
            #set condition to start transmiting
            self.writeRegister(REGFIFOTHRESHOLD_FSK, 0x80)

        else:
            raise Exception("Modem ERROR")
        
        #write data to FIFO
        self.WriteToFIFO(data)

        #print('{:08b}'.format(self.readRegister(REG_FSK_IRQFLAGS1) ) )
        #sleep(2)
        #start transmission
        self.SetTransceiverMode("TX")

        #wait for packet transmission or timeout
        start = ticks_ms()
        while (self.readRegister(REGIRQFLAGS) & 0x08) == 0 and (self.readRegister(REGIRQFLAGS2_FSK) & 0x08) == 0:
            if (ticks_ms() - start > timeout):
                print("Transmission Timedout")
                break
        
        self.collectGarbage()
        self.ClearIRQFlags(m=modem)
        print("Transmition Finished")

    def GetLORAIrqFlags(self):
        irqFlags = self.readRegister(REGIRQFLAGS)
        self.writeRegister(REGIRQFLAGS, irqFlags)
        return irqFlags

    def GetFSKIrqFlags1(self):
        irqFlags = self.readRegister(REGFSKIRQFLAGS1)
        self.writeRegister(REGFSKIRQFLAGS1, irqFlags)
        return irqFlags
    
    def GetFSKIrqFlags2(self):
        irqFlags = self.readRegister(REGFSKIRQFLAGS2)
        self.writeRegister(REGFSKIRQFLAGS2, irqFlags)
        return irqFlags
    
    def ClearIRQFlags(self,m=None):
        if m == None:
            m = self.getActiveModem()
        if m == "LORA":
            self.writeRegister(REGIRQFLAGS, 0b11111111);
        else:
            self.writeRegister(REGFSKIRQFLAGS1, 0b11111111);
            self.writeRegister(REGFSKIRQFLAGS2, 0b11111111);

    def packetRssi(self):
        rfi = self.readRegister(0x01) >> 3 & 1
        packet_rssi = self.readRegister(REG_PKT_RSSI_VALUE)
        return packet_rssi - (157 if rfi == 0 else 164)

    def packetSnr(self):
        return (self.readRegister(REG_PKT_SNR_VALUE)) * 0.25

    def setTxPower(self, level, usePaboost = True):
        self.tx_power_level = level       
        if usePaboost:
            # PA BOOST < this is to select a fisical pin on the chip for the antenna
            # Probably True for most SX127x diy lora modules
            level = min(max(level, 2), 17)
            self.writeRegister(REGPACONFIG, 0x80 | (level - 2))
        else:
            # RFO
            level = min(max(level, 0), 14)
            self.writeRegister(REGPACONFIG, 0x70 | level)

    def setFrequency(self, frequency):
        # TODO min max limit
        frequency = int(frequency)
        self.frequency = frequency
        frequency += self.frequency_offset

        frf = (frequency << 19) // 32000000
        self.writeRegister(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self.writeRegister(REG_FRF_MID, (frf >> 8) & 0xFF)
        self.writeRegister(REG_FRF_LSB, (frf >> 0) & 0xFF)

    def setSpreadingFactor(self, sf):
        sf = min(max(sf, 6), 12)
        self.writeRegister(REGDETECTIONOPTIMIZE, 0xC5 if sf == 6 else 0xC3)
        self.writeRegister(REGDETECTIONTHRESHOLD, 0x0C if sf == 6 else 0x0A)
        self.writeRegister(REG_MODEM_CONFIG_2,(self.readRegister(REG_MODEM_CONFIG_2) & 0x0F) | ((sf << 4) & 0xF0))

    def setSignalBandwidth(self, sbw):
        bins = (7.8e3,10.4e3,15.6e3,20.8e3,31.25e3,41.7e3,62.5e3,125e3,250e3,)
        bw = 9

        if sbw < 10:
            bw = sbw
        else:
            for i in range(len(bins)):
                if sbw <= bins[i]:
                    bw = i
                    break

        self.writeRegister(REGMODEMCONFIG1,(self.readRegister(REGMODEMCONFIG1) & 0x0F) | (bw << 4))

    def setCodingRate(self, denominator):
        denominator = min(max(denominator, 5), 8)
        cr = denominator - 4
        self.writeRegister(REGMODEMCONFIG1,(self.readRegister(REGMODEMCONFIG1) & 0xF1) | (cr << 1))

    def setPreambleLength(self, length):
        self.writeRegister(REG_PREAMBLE_MSB, (length >> 8) & 0xFF)
        self.writeRegister(REG_PREAMBLE_LSB, (length >> 0) & 0xFF)

    def enableCRC(self, enable_CRC=False):
        modem_config_2 = self.readRegister(REG_MODEM_CONFIG_2)
        config = modem_config_2 | 0x04 if enable_CRC else modem_config_2 & 0xFB
        self.writeRegister(REG_MODEM_CONFIG_2, config)

    def invertIQ(self, invertIQ):
        self.invertIQ = invertIQ
        if invertIQ:
            self.writeRegister(REGINVERTIQ,((self.readRegister(REGINVERTIQ)&0xbe)| 0x40))
            self.writeRegister(REGINVERTIQ2, 0x19)
        else:
            self.writeRegister(REGINVERTIQ,((self.readRegister(REGINVERTIQ)&0xbe)| 0x01))
            self.writeRegister(REGINVERTIQ2, 0x1D)

    def setSyncWord(self, sw):
        self.writeRegister(REGSYNCWORD_LORA, sw)

    def setChannel(self):
        self.SetTransceiverMode('STDBY')
        self.setFrequency(self.frequency)
        self.invertIQ(self.invert_IQ)
        self.setTxPower(self.tx_power_level)

    def dumpRegisters(self):
        # TODO end=''
        for i in range(128):
            print("0x{:02X}: {:02X}".format(i, self.readRegister(i)), end="")
            if (i + 1) % 4 == 0:
                print()
            else:
                print(" | ", end="")

    def implicitHeaderMode(self, implicitHeaderMode=False):
        if (
            self.implicit_header_mode != implicitHeaderMode
        ):  # set value only if different.
            self.implicit_header_mode = implicitHeaderMode
            modem_config_1 = self.readRegister(REGMODEMCONFIG1)
            config = (
                modem_config_1 | 0x01
                if implicitHeaderMode
                else modem_config_1 & 0xFE
            )
            self.writeRegister(REGMODEMCONFIG1, config)

    def receive(self, size=0):
        self.implicitHeaderMode(size > 0)
        if size > 0:
            self.writeRegister(REG_PAYLOAD_LENGTH, size & 0xFF)

        # The last packet always starts at FIFO_RX_CURRENT_ADDR
        # no need to reset FIFO_ADDR_PTR
        self.writeRegister(REGOPMODE, 0b10000101)

    def listen(self, time=1000):
        time = min(max(time, 0), 10000)
        self.receive()

        start = ticks_ms()
        while True:
            if self.receivedPacket():
                return self.readPayload()
            if ticks_ms() - start > time:
                return None
    
    def User_Callback(self,payload):
        pass
    
    def onReceive(self, callback):
        self.User_Callback = callback
        modem = self.getActiveModem()
        if self.dio0:
            if callback:
                if modem == "LORA":
                    self.writeRegister(REGDIOMAPPING1, 0x00)
                self.dio0.irq(trigger=Pin.IRQ_RISING, handler=self.handleOnReceive)
            else:
                pass
                # TODO detach irq
    def FSK_SetPacketFormatVariable(self,flag):
        self.SetSingleBitTo(REGFSKPACKETCONFIG1,flag,7)
        
    def FSK_SetSyncword_On(self,flag):
        self.SetSingleBitTo(REGSYNCCONFIG,flag,4)

    def FSK_SetPreamble_On(self,flag):
        self.SetSingleBitTo(REGPREAMBLEDETECT,flag,7)
    
    def FSK_SetCRC_On(self,flag):
        self.SetSingleBitTo(REGFSKPACKETCONFIG1,flag,4)
    
    def FSK_SetPayload_Lenght(self,lenght):
        self.writeRegister(REGFSKPACKETCONFIG2, (((lenght >> 8) & 0x03) | self.readRegister(REGFSKPACKETCONFIG2&0b11111100)) )
        self.writeRegister(PAYLOADLENGTH_FSK, lenght & 0xff)
        
    def FSK_SetContinuousMode_On(self, flag):
        self.SetSingleBitTo(REGFSKPACKETCONFIG2,flag,6,invert = True)
    
    def OOK_SetBitSynchronizer_On(self,flag):
        self.SetSingleBitTo(REGOOKPEAK,flag,5)

    def FSK_SetRXTrigger(self,N):
        # None N = 0
        # Rssi Interrupt N = 1
        # PreambleDetect N = 6
        # Rssi Interrupt & PreambleDetect N = 7
        self.writeRegister(REGRXCONFIG,(self.readRegister(REGRXCONFIG) & (0xf8))|N)

    def FSK_SetAGC_On(self,flag):
        self.SetSingleBitTo(REGRXCONFIG,flag,3)
    
    def FSK_SetAFC_On(self,flag):
        self.SetSingleBitTo(REGRXCONFIG,flag,4)
    
    def SetSingleBitTo(self,REG,flag,pos,invert = False):
        if invert:
            flag = not flag
        if flag:
            self.writeRegister(REG,self.readRegister(REG) | (1<<pos))
        else:
            self.writeRegister(REG,self.readRegister(REG) & (0xFF^(1<<pos)))
            
    def handleOnReceive(self, event_source):
        modem = self.getActiveModem()
        if modem == "LORA":
            lorairqFlags = self.GetLORAIrqFlags()
            # RX_DONE only, irqFlags should be 0x40
            if lorairqFlags & 0x40 == 0x40:
                # automatically standby when RX_DONE
                if self.onReceive:
                    payload = self.readPayload()
                    self.User_Callback(self,payload)

            elif self.readRegister(REGOPMODE) != 0b10000110:
                # no packet received.
                # reset FIFO address / # enter single RX mode
                self.writeRegister(REGFIFOADDRPTR, 0x00)
                self.writeRegister(REGOPMODE, 0b10000110)
        else:
            print("FSK PAYLOAD!")
            if self.onReceive:
                payload = self.readPayload()
                self.User_Callback(self,payload)
        #self.ClearIRQFlags()
        self.collectGarbage()
        return True

    def receivedPacket(self, size=0):
        irqFlags = self.GetLORAIrqFlags()
        self.implicitHeaderMode(size > 0)
        if size > 0:
            self.writeRegister(REG_PAYLOAD_LENGTH, size & 0xFF)

        # if (irqFlags & 0x40) and \
        # (irqFlags & 0x80 == 0) and \
        # (irqFlags & 0x20 == 0):

        if (irqFlags == 0x40):
            # RX_DONE only, irqFlags should be 0x40
            # automatically standby when RX_DONE
            return True

        elif self.readRegister(REGOPMODE) != 0b10000110:
            # no packet received.
            # reset FIFO address / # enter single RX mode
            self.writeRegister(REGFIFOADDRPTR, FifoRxBaseAddr)
            self.writeRegister(REGOPMODE, 0b10000110)

    def readPayload(self):
        modem = self.getActiveModem()
        if modem == "LORA":
            # set FIFO address to current RX address
            # fifo_rx_current_addr = self.readRegister(REGFIFORXCURRENTADDR)
            self.writeRegister(REGFIFOADDRPTR, self.readRegister(REGFIFORXCURRENTADDR))

            # read packet length
            packet_length = 0
            if self.implicit_header_mode:
                packet_length = self.readRegister(REG_PAYLOAD_LENGTH)
            else:
                packet_length = self.readRegister(REGRXNBBYTES)
        else:
            packet_length = 64
            
        payload = bytearray()
        for i in range(packet_length):
            payload.append(self.readRegister(REG_FIFO))

        self.collectGarbage()
        return bytes(payload)

    def readRegister(self, address, byteorder="big", signed=False):
        response = self.transfer(address & 0x7F)
        return int.from_bytes(response, byteorder)

    def DetectRSSI(self,callback,Treshold = 100):
        self.User_Callback = callback
        #set Standby
        self.SetTransceiverMode('STDBY')
        #set treshold value
        Treshold = min(127, Treshold)
        self.writeRegister(REGFSKRSSITHRESH,Treshold*2)
        print("detecting Treshold: ",self.readRegister(REGFSKRSSITHRESH)/2," dbm")
        #set Rx to RSSI Trigger
        self.FSK_SetRXTrigger(1)
        
        #set Continuous mode On
        self.FSK_SetContinuousMode_On(True)
        #setting payload lenght = 0 in Fixed length automatically sets ContinuousMode On
        self.FSK_SetPayload_Lenght(0)
        #set DIO0 mapping 
        self.writeRegister(REGDIOMAPPING1, 0b00010000)
        #set Period of decrement of the RSSI to once every 8 chips
        self.writeRegister(REGOOKAVG, 0x72)
        #Clear IRQ Flags
        #self.ClearIRQFlags()
        #if callback:
            #self.dio0.irq(trigger=Pin.IRQ_RISING, handler=self.handleOnReceive)
        #set bitrate to max
        self.writeRegister(REGBITRATEMSB, 0x00)
        self.writeRegister(REGBITRATELSB, 0x0D)

        #set start rx
        self.SetTransceiverMode('RX')
    
    def PrintFSKBitRate(self):
        dict = {}
        dict[(0x68,0x2B)] = 1.2
        dict[(0x34,0x15)] = 2.4
        dict[(0x1A,0x0B)] = 4.8
        dict[(0x0D,0x05)] = 9.6
        dict[(0x06,0x83)] = 19.2
        dict[(0x03,0x41)] = 38.4
        dict[(0x01,0xA1)] = 76.8
        dict[(0x00,0x0D)] = 153.6
        MSB = self.readRegister(REGBITRATEMSB)
        LSB = self.readRegister(REGBITRATELSB)        
        print("{} kbps".format(dict[(MSB,LSB)]))
    def writeRegister(self, address, value):
        self.transfer(address | 0x80, value)

    def transfer(self, address, value=0x00):
        response = bytearray(1)

        self.pin_ss.value(0)

        self.spi.write(bytes([address]))
        self.spi.write_readinto(bytes([value]), response)

        self.pin_ss.value(1)

        return response

    def collectGarbage(self):
        gc.collect()
        # print('[Mem aft - free: {}   allocated: {}]'.format(gc.mem_free(), gc.mem_alloc()))

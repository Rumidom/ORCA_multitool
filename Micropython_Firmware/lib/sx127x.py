from time import sleep, ticks_ms
from machine import SPI, Pin
from micropython import const
import gc

# registers (Datasheet pag 90 - Description of the Registers)
#FIFO REGISTER (Default: 0x00)
REG_FIFO = const(0x00)

#OPERATION MODE REGISTER (Default: 0x01)
REG_OP_MODE = const(0x01)
#LongRangeMode BIT 7 (Can only be modified on Sleep mode)
#0 => FSK/OOK Mode
MODE_LONG_RANGE_MODE = const(0x80)
#1 => LoRaTM Mode
MODE_SHORT_RANGE_MODE = const(0x00)
#Modulation Mode BIT 6-5: 
#00 => FSK mode 
MODE_FSK = const(0x00)
#01 => OOK mode
MODE_OOK = const(0x20)
# BIT 3:
#1 => LOW Frequency mode 
MODE_LOW_FREQUENCY = const(0x08) 
#0=> HIGH frequency mode
MODE_HIGH_FREQUENCY = const(0x00)
# BIT 2-0:
# Transceiver modes
#000 => Sleep mode
MODE_SLEEP = const(0x00)
#001 => Stdby mode
MODE_STDBY = const(0x01)
#010 => FS mode TX (FSTx)
MODE_FREQSYNTH_TX = const(0x02)
#011 => Transmitter mode (Tx)
MODE_TX = const(0x03)
#100 => FS mode RX (FSRx)
MODE_FREQSYNTH_RX = const(0x04)
#101 =>  Receiver mode (Rx)
MODE_RX_CONTINUOUS = const(0x05)
#110 => Receiver SINGLE (Rx) (Just for LORA)
MODE_RX_SINGLE = const(0x06)

#BITRATE SETTING (FSK) Default value: 4.8 kb/s 0x1a,0x0b
REG_BITRATE_MSB = const(0x02)
REG_BITRATE_LSB = const(0x03)

#FREQUENCY DEVIATION (FSK)
REG_FREQDEVIATION_MSB = const(0x04)
REG_FREQDEVIATION_LSB = const(0x05)

#RF CARRIER FREQUENCY (FSK & LORA)
REG_FRF_MSB = const(0x06)
REG_FRF_MID = const(0x07)
REG_FRF_LSB = const(0x08)
#Default value: 434.000 MHz
#The RF frequency is taken into account internally only when 
# re-starting the receiver or entering FSRX/FSTX modes

#OUTPUT POWER CONTROL (FSK & LORA)
REG_PA_CONFIG = const(0x09)

#LNA SETTINGS (FSK & LORA)
REG_LNA = const(0x0C)

#AFC, AGC, SETTINGS/FIFO SPI POINTER (FSK / LORA)
REG_FIFO_ADDR_PTR = const(0x0D)
REG_AFC_AGC_SET = const(0x0D)

#RSSI/START TX DATA (FSK / LORA)
REG_FIFO_TX_BASE_ADDR = const(0x0E)
FifoTxBaseAddr = const(0x00)

#RSSI COLLISION DETECTOR/START RX DATA (FSK / LORA)
REG_FIFO_RX_BASE_ADDR = const(0x0F)
FifoRxBaseAddr = const(0x00)

#RSSI THRESHOLD CONTROL/START ADDRESS OF LAST PACKET RECEIVED (FSK / LORA)
REG_FIFO_RX_CURRENT_ADDR = const(0x10)

#RSSI VALUE IN DBM / OPTIONAL IRQ FLAG MASK (FSK / LORA)
REG_IRQ_FLAGS_MASK = const(0x11)
REG_FSK_RSSI_DBM = const(0x11)

#CHANNEL FILTER BW CONTROL / IRQ FLAGS (FSK / LORA)
REG_IRQ_FLAGS = const(0x12)

#AFC CHANNEL FILTER BW / NUMBER OF RECEIVED BYTES (FSK / LORA)
REG_RX_NB_BYTES = const(0x13)

#OOK DEMODULATOR / NUMBER OF VALID HEADERS RECEIVED MSB (FSK / LORA)
REG_OOK_DEMOD_PEAK = const(0x14)
#BIT 5: Enables the Bit Synchronizer.
OOKDEMO_BITSYNC_ON = const(0x10)

#THRESHOLD OF THE OOK DEMOD / NUMBER OF VALID HEADERS RECEIVED LSB (FSK / LORA)
REG_OOK_DEMOD_THRESHOLD = const(0x15)

#AVERAGE OF THE OOK DEMOD / NUMBER OF VALID PACKETSRECEIVED MSB (FSK / LORA)
REG_OOK_DEMOD_AVERAGE = const(0x16)

#AFC AND FEI CONTROL / RSSI OF LAST PACKET (FSK / LORA)
REG_PKT_RSSI_VALUE = const(0x1A)

#ESTIMATION OF LAST PACKET SNR (FSK / LORA)
REG_PKT_SNR_VALUE = const(0x19)

#VALUE OF THE CALCULATED FREQUENCY ERROR / MODEM_CONFIG (FSK / LORA)
REG_MODEM_CONFIG_1 = const(0x1D)
REG_MODEM_CONFIG_2 = const(0x1E)

#PREAMBLE_DETECT SETTINGS / SIZE OF PREAMBLE (FSK / LORA)
REG_PREAMBLE_DETECT = const(0x1f)
#BIT 7: (Enables Preamble detector when set to 1. The AGC settings supersede this bit during the startup )
FSKPREAMBLE_DETECTOR_ON = const(0x80)
#BIT 6-5: (Number of Preamble bytes to detect to trigger an interrupt)
FSKPREAMBLE_DETECTOR_SIZE = const(0x00)#const(0x20),const(0x60),const(0x40)
#BIT 4-0:
FSKPREAMBLE_DETECTOR_TOL = const(0x0A)

#TIMEOUT RX REQUEST AND RSS / SIZE OF PREAMBLE (FSK / LORA)
REG_PREAMBLE_MSB = const(0x20)

#TIMEOUT RSSI AND PAY-LOADREADY / SIZE OF PREAMBLE (FSK / LORA)
REG_PREAMBLE_LSB = const(0x21)

#TIMEOUT RSSI AND SYNCADDRESS / LORATM PAYLOAD LENGTH (FSK / LORA)
REG_PAYLOAD_LENGTH = const(0x22)

#PREAMBLE LENGTH, MSB / ADDRESS OF LAST BYTE WRITTEN IN FIFO (FSK / LORA)
REG_FIFO_RX_BYTE_ADDR = const(0x25)
Reg_FSKPreambleMsb = const(0x25)

#PREAMBLE LENGTH, MSB / MODEM PHY CONFIG 3 (FSK / LORA)
REG_MODEM_CONFIG_3 = const(0x26)
Reg_FSKPreamblelsb = const(0x26)

#SYNC WORD RECOGNITION CONTROL (FSK)
REG_FSK_SYNC_CONFIG = const(0x27)
# AutoRestartRxMode bit 7 - 6: 00 => OFF,01 => On, without waiting for the PLL to re-lock,10 => On, wait for the PLL to lock (frequency changed)
FSKSYNC_AUTO_RESTART_ON_WAITRELOCK = const(0x40) 
FSKSYNC_AUTO_RESTART_ON_WAITLOCK = const(0x80) 
# PreamblePolarity bit 5: 0 => 0xAA (default) 1 => 0x55
FSKSYNC_PREPOL_0xAA = const(0x20)
FSKSYNC_PREPOL_0x55 = const(0x00)
# SyncOn bit 4: 0 => OFF 1 => ON
FSKSYNC_WORD_ON = const(0x10)

#SYNC WORD BYTES 1 - 8 (FSK)
REG_SYNC_WORD_BYTES_1 = const(0x28)
REG_SYNC_WORD_BYTES_2 = const(0x29)
REG_SYNC_WORD_BYTES_3 = const(0x2A)
REG_SYNC_WORD_BYTES_4 = const(0x2B)
REG_SYNC_WORD_BYTES_5 = const(0x2C)
REG_SYNC_WORD_BYTES_6 = const(0x2D)
REG_SYNC_WORD_BYTES_7 = const(0x2E)
REG_SYNC_WORD_BYTES_8 = const(0x2F)

#WIDEBAND RSSI MEASUREMENT (LORA)
REG_RSSI_WIDEBAND = const(0x2C)

#PACKET MODE SETTINGS (FSK)
REG_PACKETCONFIG1 = const(0x30)
#BIT 7: (Defines the packet format used: Variable or Fixed length)
FSKPACKET_PACKETFORMAT_VARIABLE = const(0x80)
#BIT 6-5:(Defines DC-free encoding/decoding performed)
#BIT 4:(Enables CRC calculation/check (Tx/Rx))
FSKPACKET_CRC_ON = const(0x10)
#BIT 3:(Defines the behavior of the packet handler when CRC check fails)
#BIT 2-1:(Defines address based filtering in Rx)
#BIT 0:(Selects the CRC and whitening algorithms)
REG_PACKETCONFIG2 = const(0x31)
#BIT 7:(Not Used)
#BIT 6:(Data processing mode: Continuous mode, Packet mode)
FSKPACKET_DATAMODE_PACKETMODE = const(0x40)
#BIT 5:(Enables the io-homecontrol® compatibility mode)
#BIT 4:(reserved - Linked to io-homecontrol® compatibility mode)
#BIT 3:(Enables the Beacon mode in Fixed packet format)
#BIT 2-1:( Packet Length Most significant bits)

#INVERT LORA I AND Q SIGNALS (LORA)
REG_INVERTIQ = const(0x33)
RFLR_INVERTIQ_RX_MASK = const(0xBF)
RFLR_INVERTIQ_RX_OFF = const(0x00)
RFLR_INVERTIQ_RX_ON = const(0x40)
RFLR_INVERTIQ_TX_MASK = const(0xFE)
RFLR_INVERTIQ_TX_OFF = const(0x01)
RFLR_INVERTIQ_TX_ON = const(0x00)

REG_INVERTIQ2 = const(0x3B)
RFLR_INVERTIQ2_ON = const(0x19)
RFLR_INVERTIQ2_OFF = const(0x1D)

#PAYLOAD LENGTH SETTING (FSK)
REG_PAYLOADLENGTH = const(0x32)

#LORA DETECTION OPTIMIZEFOR SF6 (LORA)
REG_DETECTION_OPTIMIZE = const(0x31)
REG_DETECTION_THRESHOLD = const(0x37)

#LORA SYNC WORD (LORA)
REG_SYNC_WORD = const(0x39)

#Mapping of pins DIO0 to DIO3(FSK & LORA)
REG_DIO_MAPPING_1 = const(0x40)
REG_DIO_MAPPING_2 = const(0x41)

#SEMTECH ID RELATING THE SILICON REVISION
REG_VERSION = const(0x42)

# PA config
PA_BOOST = const(0x80)

# IRQ masks
IRQ_TX_DONE_MASK = const(0x08)
IRQ_PAYLOAD_CRC_ERROR_MASK = const(0x20)
IRQ_RX_DONE_MASK = const(0x40)
IRQ_RX_TIME_OUT_MASK = const(0x80)

# Buffer size
MAX_PKT_LENGTH = const(255)


class SX127x:

    def __init__(self, spi, ss, rst, freq, dio_0 = None,OperationMode = 'LORA'):
        self.spi = spi
        
        self.OperationMode = OperationMode
        self.OperationModes = ['LORA','FSK','OOK']
        
        if dio_0:
            self.pin_rx_done = Pin(dio_0, Pin.IN)
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
        
        #perform reset
        self.pin_rst.off()
        sleep(0.01)
        self.pin_rst.on()
        sleep(0.01)
        
        # check version
        for i in range(5):
            self.version = self.readRegister(REG_VERSION)
            if self.version:
                break
            
        # debug output
        print("SX version: {}".format(self.version))

        # put sleep mode
        self.sleep()
        # config
        self.setFrequency(freq)
        self.setTxPower(self.tx_power_level)
        
        if self.OperationMode == 'LORA':
            self.LoraInit()
        if self.OperationMode == 'FSK' or self.OperationMode == 'OOK':
            self.FskOok_Init()
        self.standby()
    
    def LoraInit(self):
        
        #self.setSignalBandwidth(self.parameters["signal_bandwidth"])
        # set LNA boost 0x03 is highest gain
        self.writeRegister(REG_LNA, self.readRegister(REG_LNA) | 0x03)
        # set auto AGC (automatic gain control, negates LNA boost setting)
        self.writeRegister(REG_MODEM_CONFIG_3, 0x04)

        
        #self.implicitHeaderMode(self.parameters["implicitHeader"])
        #self.setSpreadingFactor(self.parameters["spreading_factor"])
        #self.setCodingRate(self.parameters["coding_rate"])
        #self.setPreambleLength(self.parameters["preamble_length"])
        #self.setSyncWord(self.parameters["sync_word"])
        #self.enableCRC(self.parameters["enable_CRC"])
        #self.invertIQ(self.parameters["invert_IQ"])

        # set LowDataRateOptimize flag if symbol time > 16ms (default disable on reset)
        # self.writeRegister(REG_MODEM_CONFIG_3, self.readRegister(REG_MODEM_CONFIG_3) & 0xF7)  # default disable on reset
        bw = self.signal_bandwidth
        sf = self.spreading_factor
        if 1000 / bw / 2 ** sf > 16:
            self.writeRegister(
                REG_MODEM_CONFIG_3, self.readRegister(REG_MODEM_CONFIG_3) | 0x08
            )

        # set base addresses
        self.writeRegister(REG_FIFO_TX_BASE_ADDR, FifoTxBaseAddr)
        self.writeRegister(REG_FIFO_RX_BASE_ADDR, FifoRxBaseAddr)
    
    
    def FskOok_Init(self):
        #turns off Syncword
        self.Fsk_SetSyncwordComparison(False)
        self.Fsk_SetPreambleDetection(False)
        self.Fsk_SetCRC(False)
        self.OOK_SetBitSynchronizer(False)
    
    def PrintOpMode(self):
        RegOpMode = self.readRegister(0x01)
        if (RegOpMode & (1<<7)):
            print("Lora Mode")
        elif (not (RegOpMode & (1<<6))) and (RegOpMode & (1<<5)):
            print("FSK Mode")
        else:
            print("OOK Mode")
            
        if (RegOpMode & (1<<3)):
            print("LOW Freq")
        else:
            print("HIGH Freq")
            
        t_mode_index = int(bin(RegOpMode)[5:], 2)
        if (RegOpMode & (1<<7)):
            t_mode = ["Sleep","Stdby","FSTx","Tx","FSRx","RXCONT","RXSINGLE","CAD"]
        else:
            t_mode = ["Sleep","Stdby","FSTx","Tx","FSRx","Rx"]
        print(t_mode[t_mode_index])
        
    def beginPacket(self, implicitHeaderMode=False):
        self.standby()
        self.implicitHeaderMode(implicitHeaderMode)

        # reset FIFO address and payload length
        self.writeRegister(REG_FIFO_ADDR_PTR, FifoTxBaseAddr)
        self.writeRegister(REG_PAYLOAD_LENGTH, 0)

    def endPacket(self):
        # put in TX mode
        self.writeRegister(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_TX)
        # wait for TX done, standby automatically on TX_DONE
        while (self.readRegister(REG_IRQ_FLAGS) & IRQ_TX_DONE_MASK) == 0:
            pass
        # clear IRQ's
        self.writeRegister(REG_IRQ_FLAGS, IRQ_TX_DONE_MASK)

    def write(self, buffer):
        currentLength = self.readRegister(REG_PAYLOAD_LENGTH)
        size = len(buffer)

        # check size
        size = min(size, (MAX_PKT_LENGTH - FifoTxBaseAddr - currentLength))

        # write data
        for i in range(size):
            self.writeRegister(REG_FIFO, buffer[i])

        # update length
        self.writeRegister(REG_PAYLOAD_LENGTH, currentLength + size)
        return size


    def println(self, message, implicitHeader=False, repeat=1):
        # wait until RX_Done, lock and begin writing

        if isinstance(message, str):
            message = message.encode()

        self.beginPacket(implicitHeader)
        self.write(message)

        for i in range(repeat):
            self.endPacket()

        # unlock when done writing
        self.collectGarbage()

    def getIrqFlags(self):
        irqFlags = self.readRegister(REG_IRQ_FLAGS)
        self.writeRegister(REG_IRQ_FLAGS, irqFlags)
        return irqFlags

    def packetRssi(self, rfi="hf"):
        packet_rssi = self.readRegister(REG_PKT_RSSI_VALUE)
        return packet_rssi - (157 if rfi == "hf" else 164)

    def packetSnr(self):
        return (self.readRegister(REG_PKT_SNR_VALUE)) * 0.25

    def standby(self):
        opMode = self.OperationMode
        if opMode == 'LORA':
            self.writeRegister(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_LOW_FREQUENCY | MODE_STDBY)
        elif opMode == 'FSK':
            self.writeRegister(REG_OP_MODE, MODE_SHORT_RANGE_MODE | MODE_FSK | MODE_LOW_FREQUENCY | MODE_STDBY)
        elif opMode == 'OOK':
            self.writeRegister(REG_OP_MODE, MODE_SHORT_RANGE_MODE | MODE_OOK | MODE_LOW_FREQUENCY | MODE_STDBY)

    def sleep(self):
        opMode = self.OperationMode
        if opMode == 'LORA':
            self.writeRegister(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_LOW_FREQUENCY | MODE_SLEEP)
        elif opMode == 'FSK':
            self.writeRegister(REG_OP_MODE, MODE_SHORT_RANGE_MODE | MODE_FSK | MODE_LOW_FREQUENCY | MODE_SLEEP)
        elif opMode == 'OOK':
            self.writeRegister(REG_OP_MODE, MODE_SHORT_RANGE_MODE | MODE_OOK | MODE_LOW_FREQUENCY | MODE_SLEEP)

    def setTxPower(self, level, usePaboost = True):
        self.tx_power_level = level       
        if usePaboost:
            # PA BOOST < this is to select a fisical pin on the chip for the antenna
            # Probably True for most SX127x diy lora modules
            level = min(max(level, 2), 17)
            self.writeRegister(REG_PA_CONFIG, 0x80 | (level - 2))
        else:
            # RFO
            level = min(max(level, 0), 14)
            self.writeRegister(REG_PA_CONFIG, 0x70 | level)

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
        self.writeRegister(REG_DETECTION_OPTIMIZE, 0xC5 if sf == 6 else 0xC3)
        self.writeRegister(REG_DETECTION_THRESHOLD, 0x0C if sf == 6 else 0x0A)
        self.writeRegister(
            REG_MODEM_CONFIG_2,
            (self.readRegister(REG_MODEM_CONFIG_2) & 0x0F) | ((sf << 4) & 0xF0),
        )

    def setSignalBandwidth(self, sbw):
        bins = (
            7.8e3,
            10.4e3,
            15.6e3,
            20.8e3,
            31.25e3,
            41.7e3,
            62.5e3,
            125e3,
            250e3,
        )
        bw = 9

        if sbw < 10:
            bw = sbw
        else:
            for i in range(len(bins)):
                if sbw <= bins[i]:
                    bw = i
                    break

        self.writeRegister(
            REG_MODEM_CONFIG_1,
            (self.readRegister(REG_MODEM_CONFIG_1) & 0x0F) | (bw << 4),
        )

    def setCodingRate(self, denominator):
        denominator = min(max(denominator, 5), 8)
        cr = denominator - 4
        self.writeRegister(
            REG_MODEM_CONFIG_1,
            (self.readRegister(REG_MODEM_CONFIG_1) & 0xF1) | (cr << 1),
        )

    def setPreambleLength(self, length):
        self.writeRegister(REG_PREAMBLE_MSB, (length >> 8) & 0xFF)
        self.writeRegister(REG_PREAMBLE_LSB, (length >> 0) & 0xFF)

    def enableCRC(self, enable_CRC):
        modem_config_2 = self.readRegister(REG_MODEM_CONFIG_2)
        config = modem_config_2 | 0x04 if enable_CRC else modem_config_2 & 0xFB
        self.writeRegister(REG_MODEM_CONFIG_2, config)
    

    def invertIQ(Self,invertIQ):
        self.invertIQ = invertIQ
        if invertIQ:
            self.writeRegister(
                REG_INVERTIQ,
                (
                    (
                        self.readRegister(REG_INVERTIQ)
                        & RFLR_INVERTIQ_TX_MASK
                        & RFLR_INVERTIQ_RX_MASK
                    )
                    | RFLR_INVERTIQ_RX_ON
                    | RFLR_INVERTIQ_TX_ON
                ),
            )
            self.writeRegister(REG_INVERTIQ2, RFLR_INVERTIQ2_ON)
        else:
            self.writeRegister(
                REG_INVERTIQ,
                (
                    (
                        self.readRegister(REG_INVERTIQ)
                        & RFLR_INVERTIQ_TX_MASK
                        & RFLR_INVERTIQ_RX_MASK
                    )
                    | RFLR_INVERTIQ_RX_OFF
                    | RFLR_INVERTIQ_TX_OFF
                ),
            )
            self.writeRegister(REG_INVERTIQ2, RFLR_INVERTIQ2_OFF)

    def setSyncWord(self, sw):
        self.writeRegister(REG_SYNC_WORD, sw)

    def setChannel(self):
        self.standby()
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
            modem_config_1 = self.readRegister(REG_MODEM_CONFIG_1)
            config = (
                modem_config_1 | 0x01
                if implicitHeaderMode
                else modem_config_1 & 0xFE
            )
            self.writeRegister(REG_MODEM_CONFIG_1, config)

    def receive(self, size=0):
        self.implicitHeaderMode(size > 0)
        if size > 0:
            self.writeRegister(REG_PAYLOAD_LENGTH, size & 0xFF)

        # The last packet always starts at FIFO_RX_CURRENT_ADDR
        # no need to reset FIFO_ADDR_PTR
        self.writeRegister(REG_OP_MODE, (((self.readRegister(REG_OP_MODE) | (1<<2))& ~(1<<1))| (1<<0)))

    def listen(self, time=1000):
        time = min(max(time, 0), 10000)
        self.receive()

        start = ticks_ms()
        while True:
            if self.receivedPacket():
                return self.readPayload()
            if ticks_ms() - start > time:
                return None

    def onReceive(self, callback):
        self.onReceive = callback

        if self.pin_rx_done:
            if callback:
                self.writeRegister(REG_DIO_MAPPING_1, 0x00)
                self.pin_rx_done.irq(
                    trigger=Pin.IRQ_RISING, handler=self.handleOnReceive
                )
            else:
                pass
                # TODO detach irq
    def Fsk_SetSyncwordComparison(self,flag):
        if flag:
            self.writeRegister(REG_FSK_SYNC_CONFIG,self.readRegister(REG_FSK_SYNC_CONFIG) | FSKSYNC_WORD_ON )
        else:
            self.writeRegister(REG_FSK_SYNC_CONFIG,self.readRegister(REG_FSK_SYNC_CONFIG) & (FSKSYNC_WORD_ON ^ 0b11111111))

    def Fsk_SetPreambleDetection(self,flag):
        if flag:
            self.writeRegister(REG_PREAMBLE_DETECT,self.readRegister(REG_PREAMBLE_DETECT) | FSKPREAMBLE_DETECTOR_ON)
        else:
            self.writeRegister(REG_PREAMBLE_DETECT,self.readRegister(REG_PREAMBLE_DETECT) & (FSKPREAMBLE_DETECTOR_ON ^ 0b11111111))
    
    def Fsk_SetCRC(self,flag):
        if flag:
            self.writeRegister(REG_PACKETCONFIG1,self.readRegister(REG_PACKETCONFIG1) | FSKPACKET_CRC_ON)
        else:
            self.writeRegister(REG_PACKETCONFIG1,self.readRegister(REG_PACKETCONFIG1) & (FSKPACKET_CRC_ON ^ 0b11111111))

    def FSK_SetContinuousMode(self, flag):
        if flag:
            self.writeRegister(REG_MODEM_CONFIG_2,self.readRegister(REG_PACKETCONFIG2) & (FSKPACKET_DATAMODE_PACKETMODE^ 0b11111111))
        else:
            self.writeRegister(REG_MODEM_CONFIG_2,self.readRegister(REG_PACKETCONFIG2) | FSKPACKET_DATAMODE_PACKETMODE)
    
    def OOK_SetBitSynchronizer(self,flag):
        if flag:
            self.writeRegister(REG_OOK_DEMOD_PEAK,self.readRegister(REG_OOK_DEMOD_PEAK) | (1 << 5))
        else:
            self.writeRegister(REG_OOK_DEMOD_PEAK,self.readRegister(REG_OOK_DEMOD_PEAK) & ((1<<5) ^ 0xFF))
            
          
    def handleOnReceive(self, event_source):
        # lock until TX_Done
        irqFlags = self.getIrqFlags()
        # RX_DONE only, irqFlags should be 0x40
        if irqFlags & IRQ_RX_DONE_MASK == IRQ_RX_DONE_MASK:
            # automatically standby when RX_DONE
            if self.onReceive:
                payload = self.readPayload()
                self.onReceive(self, payload)

        elif self.readRegister(REG_OP_MODE) != (
            MODE_LONG_RANGE_MODE | MODE_RX_SINGLE
        ):
            # no packet received.
            # reset FIFO address / # enter single RX mode
            self.writeRegister(REG_FIFO_ADDR_PTR, FifoRxBaseAddr)
            self.writeRegister(
                REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_SINGLE
            )

        self.collectGarbage()
        return True

    def receivedPacket(self, size=0):
        irqFlags = self.getIrqFlags()
        self.implicitHeaderMode(size > 0)
        if size > 0:
            self.writeRegister(REG_PAYLOAD_LENGTH, size & 0xFF)

        # if (irqFlags & IRQ_RX_DONE_MASK) and \
        # (irqFlags & IRQ_RX_TIME_OUT_MASK == 0) and \
        # (irqFlags & IRQ_PAYLOAD_CRC_ERROR_MASK == 0):

        if (
            irqFlags == IRQ_RX_DONE_MASK
        ):  # RX_DONE only, irqFlags should be 0x40
            # automatically standby when RX_DONE
            return True

        elif self.readRegister(REG_OP_MODE) != (
            MODE_LONG_RANGE_MODE | MODE_RX_SINGLE
        ):
            # no packet received.
            # reset FIFO address / # enter single RX mode
            self.writeRegister(REG_FIFO_ADDR_PTR, FifoRxBaseAddr)
            self.writeRegister(
                REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_SINGLE
            )

    def readPayload(self):
        # set FIFO address to current RX address
        # fifo_rx_current_addr = self.readRegister(REG_FIFO_RX_CURRENT_ADDR)
        self.writeRegister(
            REG_FIFO_ADDR_PTR, self.readRegister(REG_FIFO_RX_CURRENT_ADDR)
        )

        # read packet length
        packet_length = 0
        if self.implicit_header_mode:
            packet_length = self.readRegister(REG_PAYLOAD_LENGTH)
        else:
            packet_length = self.readRegister(REG_RX_NB_BYTES)

        payload = bytearray()
        for i in range(packet_length):
            payload.append(self.readRegister(REG_FIFO))

        self.collectGarbage()
        return bytes(payload)

    def readRegister(self, address, byteorder="big", signed=False):
        response = self.transfer(address & 0x7F)
        return int.from_bytes(response, byteorder)

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

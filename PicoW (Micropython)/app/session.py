from app.api import get_tokens, get_access_token, postPosTransaction, handlePosApiResponse
from app.wifimanager import WifiManager
from app.setup import setupNtpTime
from app.config import uhf_enable, buzzer
from app.display import Display
from micropython import alloc_emergency_exception_buf
from machine import SPI, UART, I2C, PWM
from utime import sleep, time
from app.uhf import UHF
import network
import vga1_8x16 as fontS

#-----------------------------------------------------------------------------------------#

class Session():

    def __init__(self, debounce_interval = 10, clear_interval = 20):
        self.debounce_interval = debounce_interval
        self.clear_interval = clear_interval

        self.display = Display() #Initialize display
        self.buzzer = buzzer #Initialize buzzer
        
        uhf_enable.value(0) #Initialize UHF Reader
        self.uhf = UHF(115200)
        
        self.initiate()

    def initiate(self):
        self.time_passed = time() #Time reference variable
        
        # WiFi Connection
        wlan_sta = network.WLAN(network.STA_IF)
        
        if not wlan_sta.isconnected():
            self.display.displayConnecting()
            WifiManager().get_connection()
            
            if not wlan_sta.isconnected():
                self.display.displayFailedConnection()
                import sys
                sys.exit()

        self.display.displayConnected(wlan_sta.ifconfig()[0], wlan_sta.config('ssid'))
        sleep(3)
        #-----------------------------------------------------------------------------------------#

        alloc_emergency_exception_buf(4096) # Buffer

        # Time Synchronization
        self.display.displayNTPSetup()
        self.display.displayText(text = setupNtpTime(), font = fontS, x = 28, y = 85)
        sleep(3)
        #-----------------------------------------------------------------------------------------#

        # API Setup
        self.display.displayAPISetup()
        response, self.tokens = get_tokens()
        self.display.displayText(text = response, font = fontS, x = 110, y = 85)
        sleep(1)
        self.access_token = ''
        #-----------------------------------------------------------------------------------------#

        self.table = {} # Table initialization

        self.uhf.multiple_read() # Start reading

    def read_configs(self): #Read configuration from file
        file = open('app/config.txt', 'r')
        read = []
        for line in file.readlines():
            read.append(line)
        file.close()

        settings = {}

        for i in range(len(read)):
            variable, value = read[i].split('=')
            settings[variable] = value.strip()

        del read, variable, value
        return settings

    def update_session(self): #Update session values

        settings = self.read_configs()
        
        self.debounce_interval = settings['debounce_interval']
        self.clear_interval = settings['clear_interval']

        del settings

    def renewToken(self): #Renew API Token
        new_tokens, access_token = get_access_token(self.tokens)
        if not new_tokens:
            print('Fail to refresh tokens!')
            return
        else:
            self.tokens = new_tokens
            self.access_token = access_token

    def receive_epcs(self): #Meant for esp32 multithreading
        start = time()
        while start + self.request_interval > time():
            frame = self.uhf.read_mul()
            if frame:
                epc = "".join(frame[8:20])
        self.process_epcs()

    def process_epcs(self):
        if self.tokens:
            self.renewToken()
            
            if (time() - self.time_passed) > 5:
                self.display.displayPlaceTag()
                self.time_passed = time()
            
            frame = self.uhf.read_mul() #Read EPC
            if frame:
                epc = "".join(frame[8:20])
                table = self.table
                current_time = time()

                if epc not in table: #If new, register
                    self.time_passed = time()
                    self.display.displayEPC(epc)
                    self.beep()
                    table[epc] = [current_time, current_time]
                    print('-----New EPC-----', epc)
                    self.send(epc)
                
                else: #If not new
                    last_seen, last_sent = table[epc]
                    if last_sent + int(self.debounce_interval) < current_time: #If has passed enough time since it was last sent
                        self.time_passed = time()
                        self.display.displayEPC(epc)
                        self.beep()
                        last_sent = current_time
                        self.send(epc)
                        print('-----Resent-----', epc)
                        
                    last_seen = current_time
                    self.table[epc] = [last_seen, last_sent]
            if (time() - self.time_passed) > 1:
                self.time_passed = time()
                self.expiredAndInfo()
        else:
            print('Authentication Failed!')
    
    def send(self, epc): #Sends epc to API
        posResponse = postPosTransaction(self.access_token, epc)
        if posResponse:
            handlePosApiResponse(posResponse)
            posResponse.close()
            del posResponse

    def expiredAndInfo(self): #Prints table and deals with expired epcs
    
        current_time = time()
        expired_tags = []
        print("{:<10} {:<10} {:<10}".format('EPC', '              LAST SEEN', '        LAST SENT'))

        for key, values in self.table.items():
            last_seen, last_sent = values

            if last_seen + int(self.clear_interval) < current_time:
                expired_tags.append(key)
                print('------- DELETED: ', key)
                continue
                
            print("{:x<7s} {:x<7f} {:x<7f}".format(key, last_seen, last_sent))
            
        for expired in expired_tags: del self.table[expired]

    def beep(self): #Buzzes
        buzzer.duty_u16(10000)  # HIGH will sound buzzer
        buzzer.freq(2000)
        sleep(0.1) # wait for some time
        buzzer.duty_u16(0) # Low will stop buzzer
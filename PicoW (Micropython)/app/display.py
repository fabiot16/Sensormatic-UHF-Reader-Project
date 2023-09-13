from machine import UART,SPI,Pin
from utime import sleep
import st7789
import vga1_8x16 as fontS
import vga1_16x16 as fontM
import vga1_16x32 as fontL

'''
#display functions to print to the screen
'''

class Display:

    # Color definitions
    BLACK = const(0x0000)
    BLUE = const(0x001F)
    RED = const(0xF800)
    GREEN = const(0x07E0)
    CYAN = const(0x07FF)
    MAGENTA = const(0xF81F)
    YELLOW = const(0xFFE0)
    WHITE = const(0xFFFF)

    def __init__(self):

        #configure SPI interfacing for display
        self.spi = SPI(0, baudrate=40000000, sck=Pin(6), mosi=Pin(7))  #setting the parameters for the SPI communication.

        '''
        #spi-->SPI bus object
        #135,240 --> width & height of the TFT display
        #reset pin, chip select pin ,Data command pin & Backlight of TFT --> GPIO output
        #Rotation = 1 --> Display rotation setting as per need, other options 0(default), 2, 3 
        '''
        self.tft = st7789.ST7789(self.spi,135,240,reset=Pin(14, Pin.OUT),cs=Pin(13, Pin.OUT),dc=Pin(11, Pin.OUT),
                            backlight=Pin(12, Pin.OUT),rotation=1)
        self.tft.init() # initialising the TFT  
                     
    def displayConnecting(self):
        self.clear()
        self.displayText(text = 'Connecting', font = fontL, x = 40, y = 0, color = GREEN)
        self.displayText(text = 'To', font = fontL, x = 104, y = 51, color = GREEN)
        self.displayText(text = 'WiFi', font = fontL, x = 88, y = 102, color = GREEN)

    def displayConnected(self, ip, ssid):
        self.clear()
        self.displayText(text = 'WiFi Connected', font = fontL, x = 8, y = 0, color = GREEN)
        self.displayText(text = 'SSID: ' + str(ssid), font = fontS, x = 0, y = 51, color = CYAN)
        self.displayText(text = 'IP: ' + str(ip), font = fontS, x = 0, y = 70, color = CYAN)

    def displayFailedConnection(self):
        self.clear()
        self.displayText(text = 'Connection', font = fontL, x = 40, y = 0, color = RED)
        self.displayText(text = 'Failed', font = fontL, x = 72, y = 51, color = RED)
        self.displayText(text = 'Rebooting', font = fontL, x = 48, y = 102, color = YELLOW)

    def displayNTPSetup(self):
        self.clear()
        self.displayText(text = 'NTP Setup', font = fontL, x = 48, y = 46, color = GREEN)

    def displayAPISetup(self):
        self.clear()
        self.displayText(text = 'API Setup', font = fontL, x = 48, y = 46, color = GREEN)

    def displayStarting(self):
        self.clear()
        self.displayText(text = 'Starting', font = fontL, x = 56, y = 51, color = GREEN)

    def displayEPC(self, epc):
        self.clear()
        epc_half_length = int(len(epc)/2)
        self.displayText(text = 'EPC', font = fontL, x = 96, y = 0, color = GREEN)
        self.displayText(text = epc[:epc_half_length], font = fontM, x = 24, y = 50)
        self.displayText(text = epc[epc_half_length:], font = fontM, x = 24, y = 70)

    def displayConfig(self):
        self.clear()
        self.displayText(text = 'Started', font = fontL, x = 64, y = 10, color = YELLOW)
        self.displayText(text = 'Config Portal', font = fontL, x = 16, y = 45, color = YELLOW)
        self.displayText(text = '192.168.4.1', font = fontS, x = 76, y = 84, color = CYAN)

    def displayUpdated(self):
        self.clear()
        self.displayText(text = 'Updated!', font = fontL, x = 56, y = 51, color = YELLOW)

    def displayPlaceTag(self):
        self.clear()
        self.displayText(text = 'Place Tag', font = fontL, x = 48, y = 51, color = GREEN)

    def displayDisconnected(self):
        self.clear()
        self.displayText(text = 'Lost Connection', font = fontL, x = 0, y = 30, color = RED)
        self.displayText(text = 'Please Reset...', font = fontL, x = 0, y = 72, color = RED)


    def displayText(self, text = '', font = fontM, x = 0, y = 0, color = WHITE):
        self.tft.text(font, text, x, y, color)
            
    def clear(self):
        self.tft.fill(0) #clear screen
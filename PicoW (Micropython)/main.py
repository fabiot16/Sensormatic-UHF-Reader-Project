def connectToWifiAndUpdate():
    from machine import reset,Pin,SPI
    from gc import collect, mem_free
    from time import sleep
    import network
    import st7789
    import vga1_16x32 as font
    #-----------------------------------------------------------------------------------------#

    #WiFi Connection
    sleep(1)
    print(mem_free())

    from app.ota_updater import OTAUpdater
    from app.wifimanager import WifiManager

    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        WifiManager().get_connection()
    
    print('Network Config:', sta_if.ifconfig())
    #-----------------------------------------------------------------------------------------#

    spi = SPI(0, baudrate=40000000, sck=Pin(6), mosi=Pin(7))  #setting the parameters for the SPI communication.
    tft = st7789.ST7789(spi,135,240,reset=Pin(14, Pin.OUT),cs=Pin(13, Pin.OUT),dc=Pin(11, Pin.OUT),
                    backlight=Pin(12, Pin.OUT),rotation=1)
    tft.init() # initialising the TFT 

    tft.text(font,"OTA Update", 40,51,st7789.RED)
    del tft
    del spi
    
    token='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'
    otaUpdater = OTAUpdater('https://github.com/fabiot16/Sensormatic-PicoW-RFID-Reader-Project', main_dir='app', headers={'Authorization': 'token {}'.format(token)})
    hasUpdated, string, version = otaUpdater.install_update_if_available()
    
    spi = SPI(0, baudrate=40000000, sck=Pin(6), mosi=Pin(7))  #setting the parameters for the SPI communication.
    tft = st7789.ST7789(spi,135,240,reset=Pin(14, Pin.OUT),cs=Pin(13, Pin.OUT),dc=Pin(11, Pin.OUT),
                    backlight=Pin(12, Pin.OUT),rotation=1)
    tft.init() # initialising the TFT 

    tft.text(font,string, 40,33,st7789.GREEN)
    tft.text(font,version, 88,70,st7789.GREEN)
    sleep(3)
    tft.fill(0)
    del tft
    del spi

    if hasUpdated:
        reset()
    else:
        del(otaUpdater)
        collect()

def startApp():
    import app.run

#connectToWifiAndUpdate()
startApp()
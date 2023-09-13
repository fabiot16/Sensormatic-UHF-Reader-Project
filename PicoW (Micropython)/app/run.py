#Imports
from app.wifimanager import WifiManager
from app.session import Session
from app.config import button2
from time import sleep
from gc import collect
import network
#-----------------------------------------------------------------------------------------#


#Initialize session
session = Session()
session.update_session() #Updates values from config.txt
session.display.displayStarting() #Displays message on screen
sleep(1)
session.display.clear() #Clears screen
session.display.displayPlaceTag()
wlan_sta = network.WLAN(network.STA_IF)
#-----------------------------------------------------------------------------------------#

#Cycle
while True:
    if not wlan_sta.isconnected():
        session.display.displyDisconnected()
        import sys
        sys.exit()
    if not button2.value(): #Button pressed enter config mode
        session.display.displayConfig()
        if WifiManager().start(config = 1):
            session.update_session()
            session.display.displayUpdated()

    session.process_epcs() #Process readings
    collect()
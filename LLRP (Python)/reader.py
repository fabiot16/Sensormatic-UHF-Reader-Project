from TagInventory import TagInventory
import threading

#-----------------------------------------------------------------------------------------

class Reader():

    def __init__(self, ip, transmit_power):
        self.ip = ip
        self.transmit_power = transmit_power

        self.setup()
    
    def setup(self):
        self.unique_epcs = set() #Read
        self.ti = TagInventory(host = self.ip, transmitPower = self.transmit_power) #Reader connection
        self.ti.Connect()
        
        threading.Thread(target=self.start, args=(), daemon=True).start()
        
    def start(self): #Start reading
        tag_inventory = self.ti.GetTagInventory()

        for epc in tag_inventory[0]:
                    
            if epc not in self.unique_epcs:
                self.unique_epcs.add(epc)
                print('Added:', epc)
        
        threading.Thread(target=self.start, args=(), daemon=True).start()

    def publishEvent(self): #Returns list
        
        epcs = self.unique_epcs

        print('\n')
        print('Sending:', epcs)
        print('\n')
        
        self.unique_epcs = set()
        
        return epcs
    
    def stop(self): #Stops reading
        self.ti.Disconnect()
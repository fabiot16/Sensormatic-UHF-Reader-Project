from api import get_tokens, get_access_token, postPosTransaction, handlePosApiResponse
from time import sleep, time
import threading

#-----------------------------------------------------------------------------------------

class Session():

    def __init__(self, reader, request_interval = 5, debounce_interval = 10, clear_interval = 20):  
        self.reader = reader
        self.request_interval = request_interval
        self.debounce_interval = debounce_interval
        self.clear_interval = clear_interval

        self.initiate()

    def initiate(self):        
        print('Login to API...')
        self.tokens = get_tokens()
        self.access_token = ''

        self.incoming_tags = []
        self.table = {}

        threading.Thread(target=self.receive_epcs, args=(), daemon=True).start()

    def renewToken(self):
        new_tokens, access_token = get_access_token(self.tokens)
        if not new_tokens:
            print('Fail to refresh tokens!')
            return
        else:
            self.tokens = new_tokens
            self.access_token = access_token

    def receive_epcs(self): #Gets read epcs
        start = time()
        while start + int(self.request_interval) > time():
            sleep(0.05)

        self.incoming_tags = self.reader.publishEvent()  

        threading.Thread(target=self.expiredAndInfo, args=(), daemon=True).start()
        threading.Thread(target=self.receive_epcs, args=(), daemon=True).start()

    def send(self, epc): #Send to API
        posResponse = postPosTransaction(self.access_token, epc)
        if posResponse:
            handlePosApiResponse(posResponse)
            posResponse.close()
            del posResponse

    def expiredAndInfo(self): #Prints info and manages expired 
    
        current_time = time()
        expired_tags = []
        print("{:<10} {:<10} {:<10}".format('EPC', '              LAST SEEN', '        LAST SENT'))

        for key, values in self.table.items():
            last_seen, last_sent = values

            if last_seen + self.clear_interval < current_time:
                expired_tags.append(key)
                print('------- DELETED: ', key)
                continue
                
            print("{:x<7s} {:x<7f} {:x<7f}".format(key, last_seen, last_sent))
            
        for expired in expired_tags: del self.table[expired]
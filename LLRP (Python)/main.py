from time import time, sleep
from session import Session
from reader import Reader
import threading

#-----------------------------------------------------------------------------------------

def open_portal(): #Opens config portal
    return WifiManager().start(config = 1)

def read_configs(): #Reads from file
    file = open('Test/config.txt', 'r')
    read = []
    for line in file.readlines():
        read.append(line)
    file.close()

    settings = {}

    for i in range(len(read)):
        variable, value = read[i].split('=')
        settings[variable] = value

    return settings

def new_reader(): #Starts reader with new configuration
    global reader
    settings = read_configs()
    reader.stop()
    reader = Reader(settings['ip'].strip(), int(settings['transmit_power']))

def new_session(): #Starts session with new configuration
    global session
    settings = read_configs()
    session = Session(reader, debounce_interval = settings['debounce_interval'], clear_interval = settings['clear_interval'])

ip = '192.168.222.173'
transmit_power = 10

reader = Reader(ip, transmit_power)
session = Session(reader, request_interval = 5, debounce_interval = 10, clear_interval = 20)

while True:
    if session.tokens: #Has token
        session.renewToken()
        epcs = session.incoming_tags #Read tag table
        
        if epcs:
            table = session.table #Internal time table
            current_time = time()

            while epcs:
                epc = epcs.pop()

                if epc not in table:
                    table[epc] = [current_time, current_time]
                    threading.Thread(target=session.send, args=(epc,)).start()
                    print('SENT: ', epc)
                
                else:
                    last_seen, last_sent = session.table[epc] #Times
                    
                    if last_sent + session.debounce_interval < current_time:
                        last_sent = current_time
                        threading.Thread(target=session.send, args=(epc,)).start()
                        print('SENT: ', epc)
                    
                    last_seen = current_time
                    session.table[epc] = [last_seen, last_sent]
            print('\n\n')
    else:
        print('Authentication Failed!')
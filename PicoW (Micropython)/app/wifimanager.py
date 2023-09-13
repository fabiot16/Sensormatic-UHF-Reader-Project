# https://pypi.org/project/micro-wifi-manager/#description
import network, os, socket, ure, time, errno
from machine import SPI, Pin, freq, reset
import st7789
import vga1_16x32 as font
import vga1_8x16 as fontS

NETWORK_PROFILES = 'wifi.dat'

wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)
changed_config = False
html_head = "<!DOCTYPE html><html lang='en'><head><meta name='format-detection' content='telephone=no'><meta charset='UTF-8'><meta  name='viewport' content='width=device-width,initial-scale=1,user-scalable=no'/><title>WiFiManager</title><script>function c(l){document.getElementById('s').value=l.getAttribute('data-ssid')||l.innerText||l.textContent;p = l.nextElementSibling.classList.contains('l');document.getElementById('p').disabled = !p;if(p)document.getElementById('p').focus();};function f() {var x = document.getElementById('p');x.type==='password'?x.type='text':x.type='password';}</script><style>.c,body{text-align:center;font-family:verdana}div,input,select{padding:5px;font-size:1em;margin:5px 0;box-sizing:border-box}input,button,select,.msg{border-radius:.3rem;width: 100%}input[type=radio],input[type=checkbox]{width:auto}button,input[type='button'],input[type='submit']{cursor:pointer;border:0;background-color:#1fa3ec;color:#fff;line-height:2.4rem;font-size:1.2rem;width:100%}input[type='file']{border:1px solid #1fa3ec}.wrap {text-align:left;display:inline-block;min-width:260px;max-width:500px}a{color:#000;font-weight:700;text-decoration:none}a:hover{color:#1fa3ec;text-decoration:underline}.q{height:16px;margin:0;padding:0 5px;text-align:right;min-width:38px;float:right}.q.q-0:after{background-position-x:0}.q.q-1:after{background-position-x:-16px}.q.q-2:after{background-position-x:-32px}.q.q-3:after{background-position-x:-48px}.q.q-4:after{background-position-x:-64px}.q.l:before{background-position-x:-80px;padding-right:5px}.ql .q{float:left}.q:after,.q:before{content:'';width:16px;height:16px;display:inline-block;background-repeat:no-repeat;background-position: 16px 0;background-image:url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAAAQCAMAAADeZIrLAAAAJFBMVEX///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADHJj5lAAAAC3RSTlMAIjN3iJmqu8zd7vF8pzcAAABsSURBVHja7Y1BCsAwCASNSVo3/v+/BUEiXnIoXkoX5jAQMxTHzK9cVSnvDxwD8bFx8PhZ9q8FmghXBhqA1faxk92PsxvRc2CCCFdhQCbRkLoAQ3q/wWUBqG35ZxtVzW4Ed6LngPyBU2CobdIDQ5oPWI5nCUwAAAAASUVORK5CYII=');}@media (-webkit-min-device-pixel-ratio: 2),(min-resolution: 192dpi){.q:before,.q:after {background-image:url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALwAAAAgCAMAAACfM+KhAAAALVBMVEX///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAOrOgAAAADnRSTlMAESIzRGZ3iJmqu8zd7gKjCLQAAACmSURBVHgB7dDBCoMwEEXRmKlVY3L//3NLhyzqIqSUggy8uxnhCR5Mo8xLt+14aZ7wwgsvvPA/ofv9+44334UXXngvb6XsFhO/VoC2RsSv9J7x8BnYLW+AjT56ud/uePMdb7IP8Bsc/e7h8Cfk912ghsNXWPpDC4hvN+D1560A1QPORyh84VKLjjdvfPFm++i9EWq0348XXnjhhT+4dIbCW+WjZim9AKk4UZMnnCEuAAAAAElFTkSuQmCC');background-size: 95px 16px;}}.msg{padding:20px;margin:20px 0;border:1px solid #eee;border-left-width:5px;border-left-color:#777}.msg h4{margin-top:0;margin-bottom:5px}.msg.P{border-left-color:#1fa3ec}.msg.P h4{color:#1fa3ec}.msg.D{border-left-color:#dc3630}.msg.D h4{color:#dc3630}.msg.S{border-left-color: #5cb85c}.msg.S h4{color: #5cb85c}dt{font-weight:bold}dd{margin:0;padding:0 0 0.5em 0;min-height:12px}td{vertical-align: top;}.h{display:none}button{transition: 0s opacity;transition-delay: 3s;transition-duration: 0s;cursor: pointer}button.D{background-color:#dc3630}button:active{opacity:50% !important;cursor:wait;transition-delay: 0s}body.invert,body.invert a,body.invert h1 {background-color:#060606;color:#fff;}body.invert .msg{color:#fff;background-color:#282828;border-top:1px solid #555;border-right:1px solid #555;border-bottom:1px solid #555;}body.invert .q[role=img]{-webkit-filter:invert(1);filter:invert(1);}:disabled {opacity: 0.5;}h1 { text-align: center;} </style></head>"

class WifiManager:

    # authmodes: 0=open, 1=WEP, 2=WPA-PSK, 3=WPA2-PSK, 4=WPA/WPA2-PSK
    def __init__(self, ssid='WifiManager', password='password'):
        self.ssid = ssid
        self.password = password
        self.server_socket = None

    def get_connection(self): #return a working WLAN(STA_IF) instance or None

        connected = False
        try:
            # First check if there already is any connection:
            time.sleep(3)
            if wlan_sta.isconnected():
                return wlan_sta
            #-----------------------------------------------------------------------------------------#

            # Read known network profiles from file and scans
            profiles = read_profiles()
            networks = scan()
            ssids = set()

            AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
            for ssid, bssid, channel, rssi, authmode, hidden in sorted(networks, key=lambda x: x[3], reverse=True):
                ssid = ssid.decode('utf-8')
                if ssid not in ssids:
                    ssids.add(ssid)
                    encrypted = authmode > 0
                    print("ssid: %s chan: %d rssi: %d authmode: %s" % (ssid, channel, rssi, AUTHMODE.get(authmode, '?')))
                    if encrypted:
                        if ssid in profiles:
                            password = profiles[ssid]
                            connected = do_connect(ssid, password)
                    if connected:
                        break
            #-----------------------------------------------------------------------------------------#

        except OSError as e:
            print("exception", str(e))

        # start web server for connection manager:
        if not connected:
            spi = SPI(0, baudrate=40000000, sck=Pin(6), mosi=Pin(7))  #setting the parameters for the SPI communication.
            tft = st7789.ST7789(spi,135,240,reset=Pin(14, Pin.OUT),cs=Pin(13, Pin.OUT),dc=Pin(11, Pin.OUT),
                            backlight=Pin(12, Pin.OUT),rotation=1)
            tft.init() # initialising the TFT 
            tft.text(font,"No Connection", 16,22,st7789.RED)
            tft.text(font,"Starting AP", 32,64,st7789.RED)
            tft.text(fontS,"192.168.4.1", 76,106,st7789.CYAN)
            connected = self.start()
            
            del spi
            del tft
        return wlan_sta if connected else None

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
    
    def start(self, port=80, config = 0):

        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

        self.stop()

        wlan_sta.active(True)

        wlan_ap.config(essid='WifiManager', password='password')
        wlan_ap.active(True)

        self.server_socket = socket.socket()
        self.server_socket.bind(addr)
        self.server_socket.listen(1)

        print('Connect to WiFi ssid ' + self.ssid + ', default password: ' + self.password)
        print('Access at 192.168.4.1')
        print('Listening on:', addr)

        while True:
            client, addr = self.server_socket.accept()
            print('client connected from', addr)
            try:
                client.settimeout(1)

                request = b""
                try:
                    while "\r\n\r\n" not in request:
                        request += client.recv(512)
                except OSError:
                    pass
                #print("Request is: {}".format(request))
                if "HTTP" not in request:  # skip invalid requests
                    continue

                # version 1.9 compatibility
                try:
                    url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).decode("utf-8").rstrip("/")
                except Exception:
                    url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).rstrip("/")
                print("URL is {}".format(url))

                # TODO getting "generate_204 as address"
                if url == "wifi":
                    handle_wifi(client)
                elif url == "wifisave":
                    handle_wifisave(client, request)
                elif url == 'info':
                    handle_info(client)
                elif url == 'update':
                    handle_update(client)
                elif url == 'updated':
                    updated(client, request)
                elif url == 'erase':
                    erase_wifi(client)
                elif url == 'exit':
                    time.sleep(1)
                    self.stop()
                    wlan_ap.active(False)
                    client.close()
                    reset()
                    return changed_config
                else:
                    if not config:
                        handle_root(client)
                    else:
                        handle_root(client, config = 1)

            finally:
                client.close()

def scan(): #Scans WiFis
    wlan_sta.active(True)
    return wlan_sta.scan()

def erase_wifi(client): #Erases saved WiFis
    os.remove('wifi.dat')
    wlan_sta.active(False)
    time.sleep(2)
    handle_wifi(client)

def write_file(values): #Writes configuration to config.txt
    global changed_config
    file = open("app/config.txt", "r")
    read = []
    for line in file.readlines():
        read.append(line)
    file.close()
    os.remove('app/config.txt')

    write = ''

    for i in range(len(read)):
        splited = [x.strip() for x in read[i].split('=')]
        if values[i] != '' and (splited[1] != values[i]):
            changed_config = True
            write += str(splited[0]) + '=' + str(values[i]) + '\n'
        else:
            write += str(read[i])
    file = open("app/config.txt", "w")
    file.write(write)
    file.close()

def get_info(): #Returns device info
    # print(freq())
    # print(esp.flash_user_start())
    # print(esp.flash_size())
    # print(esp32.raw_temperature())
    # print(esp32.idf_heap_info(esp32.HEAP_DATA))
    # print(wlan_sta.ifconfig())
    # print(network.hostname())
    # print(wlan_ap.config('ssid'))
    # print(wlan_ap.config('mac'))
    # print(wlan_ap.ifconfig())
    # print(esp32.idf_heap_info(esp32.HEAP_EXEC))
    # print(esp32.idf_heap_info(esp32.HEAP_DATA))
    # print(gc.mem_alloc())
    # print(gc.mem_free())
    return [wlan_sta.ifconfig(), wlan_sta.config('ssid'), wlan_sta.config('mac'), wlan_ap.config('ssid'), wlan_ap.config('mac'), wlan_ap.ifconfig()]

def hex2mac(h): #Converts hexadecimal to mac address
    v = 0x000e96a001064d60
    s = '{0:016x}'.format(v)
    return ':'.join(s[i:i + 2] for i in range(0, 12, 2))

def read_profiles(): #Reads saved WiFis
    try:
        with open(NETWORK_PROFILES) as f:
            lines = f.readlines()
        profiles = {}
        for line in lines:
            ssid, password = line.strip("\n").split(";")
            profiles[ssid] = password
        return profiles
    except Exception:
        return {}
    return profiles

def write_profiles(profiles): #Saves WiFis
    lines = []
    for ssid, password in profiles.items():
        lines.append("%s;%s\n" % (ssid, password))
    with open(NETWORK_PROFILES, "w") as f:
        f.write(''.join(lines))

def do_connect(ssid, password): #Tries connection
    print('Trying to connect to %s...' % ssid)
    wlan_sta.connect(ssid, password)
    for retry in range(100):
        connected = wlan_sta.isconnected()
        if connected:
            return True
        print(retry)
        time.sleep(0.1)
    if connected:
        print('\nConnected. Network config: ', wlan_sta.ifconfig())
    else:
        print('\nFailed. Not Connected to: ' + ssid)
    return False

def send_header(client, status_code=200, content_length=None ):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
        client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")

def send_response(client, payload, status_code=200):
    content_length = len(payload)
    send_header(client, status_code, content_length)
    if content_length > 0:
        client.sendall(payload)
    client.close()

def handle_root(client, config = 0): #Root page
    try:
        set_ap = list(read_profiles().keys())
        if not set_ap:
            set_ap = 'No AP Set'
        else:
            set_ap = set_ap[0]
        wlan_sta.active(True)
        send_header(client)
        if not config:
            client.sendall(f"""\
                {html_head}<body class='invert'><div class='wrap'><h1>WiFiManager</h1></br></br><form action="wifi" method="post"><button>Configure WiFi</button></form><br/><form action='update'  method='get'><button>Configure RFID</button></form><br/><form action='info' method='post'><button>WiFi Info</button></form><br/><form action='exit' method='post'><button class='D'>Exit</button></form><br/><div class='msg'>{set_ap}</div></div></body></html>
            """)     
        else:
            client.sendall(f"""\
                {html_head}<body class='invert'><div class='wrap'><h1>WiFiManager</h1><h3>AP</h3><form action='update'  method='get'><button>Configure RFID</button></form><br/><form action='erase' method='get'><button class='D'>Erase WiFi Config</button></form><br/><form action='info' method='post'><button>WiFi Info</button></form><br/><form action='exit' method='post'><button class='D'>Exit</button></form><br/><div class='msg'>{set_ap}</div></div></body></html>
            """)                          
    except Exception as e:
        if e.errno == errno.ECONNRESET:
            pass
        else:
            raise

def handle_wifi(client): #WiFi configuration page
    try:
        wlan_sta.active(True)
        scanned = {ssid.decode('utf-8'): (rssi, security) for ssid, _, _, rssi, security, _ in scan()}
        
        set_ap = list(read_profiles().keys())
        if not set_ap:
            set_ap = 'No AP Set'
        else:
            set_ap = set_ap[0]
        
        send_header(client)
        client.sendall(f"""\
            {html_head}<body class='invert'><div class='wrap'><div>
        """)
        
        for ssid in sorted(scanned):
            rssi, security = scanned[ssid]
            if ssid == '':
                ssid = '* hidden network *'
            rssi = max(min(rssi, -50), -90)
            intensity = int(100 * (rssi - (-90)) / (-50 - (-90)))
            secured = 'l' if security > 0 else ''

            client.sendall(f"""\
            <div><a href='#p' onclick='c(this)' data-ssid='{ssid}'>{ssid}</a><div role='img' aria-label='{intensity}%' title='{intensity}%' class='q q-{int(intensity/20)} {secured} '></div><div class='q h'>{intensity}%</div></div>
            """)
        
        client.sendall(f"""\
            <br/><form method='POST' action='wifisave'><label for='s'>SSID</label><input id='s' name='ssid' maxlength='32' autocorrect='off' autocapitalize='none' placeholder=''><br/><label for='p'>Password</label><input id='p' name='password' maxlength='64' type='password' placeholder=''><input type='checkbox' onclick='f()'> Show Password<br/><br/><button type='submit'>Save</button></form><br/><form action='/wifi?refresh=1' method='POST'><button name='refresh' value='1'>Refresh</button></form><br/><form action='index' method='POST'><button name='go back' value='1'>Go Back</button></form><br/><div class='msg'>{set_ap}</div></div></body></html>        
        """)
    except Exception as e:
        if e.errno == errno.ECONNRESET:
            pass
        else:
            raise

def handle_wifisave(client, request): #Saved WiFi page
    match = ure.search("ssid=([^&]*)&password=(.*)", request)
    # version 1.9 compatibility
    
    try:
        ssid = match.group(1).decode("utf-8").replace("%3F", "?").replace("%21", "!").replace("+", " ")
        password = match.group(2).decode("utf-8").replace("%3F", "?").replace("%21", "!")
    except Exception:
        ssid = match.group(1).replace("%3F", "?").replace("%21", "!").replace("+", " ")
        password = match.group(2).replace("%3F", "?").replace("%21", "!")

    if do_connect(ssid, password):
        time.sleep(2)
        send_header(client)
        client.sendall(f"""\
            {html_head}<body class='invert'><div class='wrap'><div class='msg'>Saving Credentials<br/>ESP Successfully Connected to Network</div><break/><form action='index' method='POST'><button name='go back' value='1'>Go Back</button></form><br/><form action='exit' method='post'><button class='D'>Exit</button></form><br/></div></body></html>        
        """)
        try:
            profiles = read_profiles()
        except OSError:
            profiles = {}
        profiles[ssid] = password
        write_profiles(profiles)

        time.sleep(2)
    else:
        time.sleep(2)
        send_header(client)
        client.sendall(f"""\
            {html_head}<body class='invert'><div class='wrap'><div class='msg'>Failed to Connect ESP to Network</div><form action="wifi" method="post"><button>Try Again</button></form></div></body></html>
        """)
        time.sleep(2)

def handle_info(client): #Info page
    sta_ifconfig, ssid, mac, ap_ssid, ap_mac, ap_ifconfig = get_info()
    sta_ip, sta_sub, sta_gate, sta_dns = sta_ifconfig
    ap_ip = ap_ifconfig[0]
    mac = hex2mac(mac.hex()).upper()
    ap_mac = hex2mac(ap_mac.hex()).upper()
    connected = wlan_sta.isconnected()

    send_header(client)
    try:
        set_ap = list(read_profiles().keys())
        if not set_ap:
            set_ap = 'No AP Set'
        else:
            set_ap = set_ap[0]
        client.sendall(f"""\
            {html_head}<body class='invert'><div class='wrap'><div class='msg'>{set_ap}</div><h3>WiFi</h3><hr><dt>Connected</dt><dd>{connected}</dd><dt>Station SSID</dt><dd>{ssid}</dd><dt>Station IP</dt><dd>{sta_ip}</dd><dt>Station gateway</dt><dd>{sta_gate}</dd><dt>Station subnet</dt><dd>{sta_sub}</dd><dt>DNS Server</dt><dd>{sta_dns}</dd><dt>Hostname</dt><dd>{'None'}</dd><dt>Station MAC</dt><dd>{mac}</dd><dt>Access point IP</dt><dd>{ap_ip}</dd><dt>Access point MAC</dt><dd>{ap_mac}</dd></dl><hr><br/><br/><form action='erase' method='get'><button class='D'>Erase WiFi Config</button></form><br/><form action='index' method='POST'><button name='go back' value='1'>Go Back</button></form><br/><h3>Available pages</h3><hr><table class='table'><thead><tr><th>Page</th><th>Function</th></tr></thead><tbody><tr><td><a href='/'>/</a></td><td>Menu page.</td></tr><tr><td><a href='/wifi'>/wifi</a></td><td>Show WiFi scan results and enter WiFi configuration.(/0wifi noscan)</td></tr><tr><td><a href='/wifisave'>/wifisave</a></td><td>Save WiFi configuration information and configure device. Needs variables supplied.</td></tr><tr><td><a href='/param'>/param</a></td><td>Parameter page</td></tr><tr><td><a href='/info'>/info</a></td><td>Information page</td></tr><tr><td><a href='/update'>/update</a></td><td>OTA Update</td></tr><tr><td><a href='/close'>/close</a></td><td>Close the captiveportal popup, config portal will remain active</td></tr><tr><td>/exit</td><td>Exit Config portal, config portal will close</td></tr><tr><td>/restart</td><td>Reboot the device</td></tr><tr><td>/erase</td><td>Erase WiFi configuration and reboot device. Device will not reconnect to a network until new WiFi configuration data is entered.</td></tr></table><p/>Github <a href='https://github.com/tzapu/WiFiManager'>https://github.com/tzapu/WiFiManager</a>.</div></body></html>
            """)
    except Exception as e:
        if e.errno == errno.ECONNRESET:
            pass
        else:
            raise

def handle_update(client): #Update page
    try:
        send_header(client)
        set_ap = list(read_profiles().keys())
        if not set_ap:
            set_ap = 'No AP Set'   
        else:
            set_ap = set_ap[0]
        client.sendall(f"""\
            {html_head}<body class='invert'><div class='wrap'><h1>RFID Reader Configuration</h1></br><form method='POST' action='updated'><label for='send'>Send Timer</label><input id='send' name='send' maxlength='32' autocorrect='off' autocapitalize='none' placeholder=''><br/><br/><label for='clear'>Clear Timer</label><input id='clear' name='clear' maxlength='32' autocorrect='off' autocapitalize='none' placeholder=''><br/><br/><button type='submit'>Save</button></form><br/><form action='index' method='POST'><button name='go back' value='1'>Go Back</button></form><br/><div class='msg'>{set_ap}</div></div></body></html>
            """)
        
    except Exception as e:
        if e.errno == errno.ECONNRESET:
            pass
        else:
            raise

def updated(client, request): #Updated page
    match = ure.search("send=(.*)&clear=(.*)", request)
    # version 1.9 compatibility
    send_header(client)
    try:
        send = match.group(1).decode("utf-8")
        clear = match.group(2).decode("utf-8")
    except Exception:
        send = match.group(1).decode("utf-8")
        clear = match.group(2).decode("utf-8")
    try:
        print([send, clear])
        write_file([send, clear])
        client.sendall(f"""\
            {html_head}<body class='invert'><div class='wrap'><div class='msg'>Success<br/>RFID Reader Configured</div><break/><form action='index' method='POST'><button name='go back' value='1'>Go Back</button></form><br/><form action='exit' method='post'><button class='D'>Exit</button></form><br/></div></body></html>        
        """)
    except Exception as e:
        if e.errno == errno.ECONNRESET:
            pass
        else:
            raise
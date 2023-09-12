from ntptime import settime
from utime import localtime, sleep
from machine import RTC

def setupNtpTime(): #Time synchronization
    while True:
        try:
            settime()
            tm = localtime()
            tm = tm[0:3] + (0,) + tm[3:6] + (0,)
            RTC().datetime(tm)
            return '{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.000Z'.format(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5])
        except:
            sleep(0.5)
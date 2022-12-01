import os
import glob
import time
import BlynkLib
import datetime
import RPi.GPIO as GPIO
import signal
import sys

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
blynk=0
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW)
print("off")
min_temp=43
max_temp=63
stat_rel=0

try:
    BLYNK_AUTH = ''
    blynk = BlynkLib.Blynk(BLYNK_AUTH)
except:
    print("no internet for blynk")

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

@blynk.VIRTUAL_WRITE(3)
def v3_write_handler(value):
    global min_temp
    min_temp=float(value)
    print("new min is ",value)

@blynk.VIRTUAL_WRITE(4)
def v4_write_handler(value):
    global max_temp
    max_temp=float(value)
    print("new max is ",value)

@blynk.VIRTUAL_READ(2)
def v2_read_handler():
    y = float(read_temp()) #(np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
    print(y)
    print(min_temp)
    print(max_temp)

    if y>max_temp:
        print("off")
        GPIO.output(18, GPIO.LOW)
        stat_rel = 0
    if y<min_temp:
        print("on")
        GPIO.output(18, GPIO.HIGH)
        stat_rel = 1
    try:
        blynk.virtual_write(2,y)
        blynk.virtual_write(7,stat_rel)
    except:
        print(sys.exc_info()[0])

def handler(signum, frame):
    v2_read_handler()
    signal.alarm(10)

signal.signal(signal.SIGALRM, handler)
signal.alarm(10)

#try:
blynk.run()
#except:
#    print "no net global"

while True:
    v2_read_handler()
    time.sleep(10)

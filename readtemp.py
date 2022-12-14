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
GPIO.output(18, GPIO.HIGH)
stat_rel=0
print(datetime.datetime.now(),"Start up. setting relay to off.")
min_temp=39
max_temp=59
started=False

while not started:
    try:
        blynk = BlynkLib.Blynk(open('blynk.auth', "r").read().replace("\n",""))
        started=True
    except:
        print(datetime.datetime.now(),sys.exc_info())
        time.sleep(10)

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

@blynk.on("connected")
def blynk_connected():
    print(datetime.datetime.now(),"Updating V3,V4 values from the server...")
    blynk.sync_virtual(3,4)

@blynk.on("V3")
def v3_write_handler(value):
    global min_temp
    min_temp=float(value[0])
    print(datetime.datetime.now(),"new min is ",value)

@blynk.on("V4")
def v4_write_handler(value):
    global max_temp
    max_temp=float(value[0])
    print(datetime.datetime.now(),"new max is ",value)

def process_state():
    global blynk
    y = float(read_temp()) 
    print(datetime.datetime.now(),"Current temp:",y,"min:",min_temp,"max:",max_temp)
    global stat_rel

    if y>max_temp:
        print(datetime.datetime.now(),"setting relay to OFF ...")
        GPIO.output(18, GPIO.HIGH)
        stat_rel = 0
    if y<min_temp:
        print(datetime.datetime.now(),"setting relay to ON ...")
        GPIO.output(18, GPIO.LOW)
        stat_rel = 1
    try:
        blynk.virtual_write(2,y)
        blynk.virtual_write(7,stat_rel)
    except:
        print(datetime.datetime.now(),sys.exc_info())



while True:
    try:
        blynk.run()
    except:
        print(datetime.datetime.now(),sys.exc_info())
    try:
        process_state()
    except:
        print(datetime.datetime.now(),sys.exc_info())
    time.sleep(10)

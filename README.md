# blynk_therm
Buy raspberry and SD Card adapter
Download Raspberry Pi Imager
Start Raspberry Pi Imager, in settings configure WIFI & SSH then Install iso on a SD Card
ssh pi@raspbeerypi.local
sudo apt update
sudo apt upgrade
sudo apt install python3-pip
pip install RPi.GPIO
raspi-config -> enable WIRE 
Reboot
ssh pi@raspbeerypi.local
git clone https://github.com/scrissti/blynk_therm.git
insert Blynk auth token in readtemp.py line 26

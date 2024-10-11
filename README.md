# Pi Radio
![LCD](https://github.com/user-attachments/assets/e973a910-e17a-4fd1-bf85-f4c63b5a746b)

You are listening MBS Radio, it's 13h30. Temperature is 21°C and Humidity is 58%

Pi Radio is a web radio station
It's using a web radio list file named radiolist.json
You are free to add any radio you want in this file

Pi Radio use an LCD1602 I2C screen with the liquidecrystal_i2c.py driver (make attention to the address of your screen)

Pi Radio is using ffplay from ffmpeg to play stream

Pi Radio comes with 4 boutons :
- the first one can power off the system
- the second one can start and stop the radio player
- with the third one you can swith to the previous station
- with the fourth one you can swith to the next station

PiRadio use a DHT sensor that will show tempereratues and humidity
It uses internet time to show you the date ans time of the day

# installpackage.sh and requirements.txt
It's a script shell and a pytohn3 requirement list to help you to install requirements.

# dht22.py
It's a small python script to help you to test your dht sensor

# piradio.py
The main script

# liquidcrystal_i2c.py
The python screen driver for the lcd1602 i2c (do not forget to activate i2c interface !)

# installservice.sh
A bash script that will install the service (auto start at boot) using piradio.service
By default, you have to use /home/pi/piradio/ folder (you can change that if you want)

# the box is 3D printed
see 3dprint folder



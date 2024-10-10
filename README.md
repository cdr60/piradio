#Pi Radio
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

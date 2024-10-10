#! /bin/bash
if [ ! -f /home/pi/piradio/piradio.service ]; then
   echo "Fichier /home/pi/piradio/piradio.service  absent"
   exit 99
fi   
sudo cp /home/pi/piradio/piradio.service  /lib/systemd/system/piradio.service
r=$?
if [ $r -ne 0 ]; then
   echo "Une erreur s'est produite"
   exit 1
fi
sudo systemctl daemon-reload
sudo systemctl enable piradio.service

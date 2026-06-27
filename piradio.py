#!/usr/bin/python3
#
import liquidcrystal_i2c  
import os
import time
import datetime
import RPi.GPIO as GPIO
import json
import subprocess
import signal
import sys
import threading
from tools import *
import board
import adafruit_ds1307
import Adafruit_DHT
import configparser

# Import de Flask pour la page web
from flask import Flask, render_template, request, jsonify

#apt-get install python3-rpi.gpio python3-spidev python3-pil libgpiod2 python3-smbus i2c-tools gstreamer1.0-x ffmpeg
#pip3 install adafruit-circuitpython-ds1307 smbus Adafruit_Python_DHT playsound --break-system-packages flask


def printcurrentdatetime():
	now = datetime.datetime.now()
	current_time = now.strftime("%d/%m/%Y %H:%M:%S")
	print(current_time)
	

def get_dht(sensor,pin,offset=0):
	try:
		humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	except:
		humidity, temperature=None,None
	return temperature + offset,humidity

def starting_rtc():
	i2c = board.I2C()
	rtc = adafruit_ds1307.DS1307(i2c)
	t = rtc.datetime
	s = datetime.datetime.now()
	print("RTC TIME")
	print(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
	print("SYSTEM TIME")
	print(s.year, s.month, s.day, s.hour, s.minute, s.second)
	
	if (t.tm_year==2000):
		print("Maj heure RTC a partir de l'heure systeme")
		rtc.datetime=time.struct_time((s.year, s.month, s.day, s.hour, s.minute, s.second,0,0,0))
	elif (s.year<=2000):
		print("Maj heure systeme a partir de l'heure RTC")
		time_tuple = ( t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec , 0)
		import ctypes
		import ctypes.util
		CLOCK_REALTIME = 0
		class timespec(ctypes.Structure):
			_fields_ = [("tv_sec", ctypes.c_long),("tv_nsec", ctypes.c_long)]
		librt = ctypes.CDLL(ctypes.util.find_library("rt"))
		ts = timespec()
		ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
		ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond
		librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


####################################################################################
# OBJET CLAVIER
####################################################################################
class Keyboard(threading.Thread):
	def __init__(self, KEY_1_PIN,KEY_2_PIN,KEY_3_PIN,KEY_4_PIN,min_short_time=150,min_long_time=1000):
		threading.Thread.__init__(self)
		self.lock = threading.Lock()
		self.min_short_time=min_short_time/1000.00
		self.min_long_time=min_long_time/1000.00
		K_1={"pin":KEY_1_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_2={"pin":KEY_2_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_3={"pin":KEY_3_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		K_4={"pin":KEY_4_PIN,"current":None,"previous":None,"pressed":False,"time":0,"type":""}
		self.BUTTONS={"K_1":K_1,"K_2":K_2,"K_3":K_3,"K_4":K_4}

		GPIO.setmode(GPIO.BCM)
		for key in self.BUTTONS:
			GPIO.setup(self.BUTTONS[key]["pin"],GPIO.IN, pull_up_down=GPIO.PUD_UP)		# Input with pull-up
		self.deamon = True
		#pour démarrer le service : start mais je le fais ailleurs
		#self.start()


	def run(self):
		for key in self.BUTTONS:
			self.BUTTONS[key]["previous"]=None
			self.BUTTONS[key]["time"]=0
			self.BUTTONS[key]["pressed"]=False
			self.BUTTONS[key]["type"]=""

		while 1:
			for key in self.BUTTONS:
				self.BUTTONS[key]["current"]=GPIO.input(self.BUTTONS[key]["pin"])
				time.sleep(0.01)
				if self.BUTTONS[key]["current"]==0 and self.BUTTONS[key]["previous"]==1:
					self.BUTTONS[key]["pressed"] = True
					self.BUTTONS[key]["time"]=0
					while self.BUTTONS[key]["pressed"]:
						time.sleep(0.05)
						self.BUTTONS[key]["time"]+=0.05
						self.BUTTONS[key]["current"]=GPIO.input(self.BUTTONS[key]["pin"])
						if (self.BUTTONS[key]["current"]==1): self.BUTTONS[key]["pressed"]=False
						
				self.BUTTONS[key]["previous"] = self.BUTTONS[key]["current"]
				if self.BUTTONS[key]["time"]<self.min_short_time: self.BUTTONS[key]["type"]=""
				elif self.BUTTONS[key]["time"]>=self.min_long_time: self.BUTTONS[key]["type"]="long"
				else: self.BUTTONS[key]["type"]="short"

	def wich_btn(self):
		btn,typ=None,None
		for key in self.BUTTONS:
			if self.BUTTONS[key]["type"]!="": 
				btn,typ=key,self.BUTTONS[key]["type"]
				self.BUTTONS[btn]["type"]=""
				self.BUTTONS[btn]["pressend"]=False
				self.BUTTONS[btn]["time"]=0
				self.BUTTONS[btn]["current"]=0
				self.BUTTONS[btn]["previous"]=0
				return btn,typ
			time.sleep(0.01)
		return btn,typ

####################################################################################
# OBJET REVEIL
####################################################################################
class MaRadio():

	def __init__(self,dht=True):
		#pour savoir si la page heure doit être raffraichit
		self.oldmin=-1
		self.ts_last_temp, self.old_temp, self.old_humidity , self.dht_sensor, self.radiothread = None, None, None, None, None
		if (dht == True): self.dht_sensor = Adafruit_DHT.DHT11
		if (self.dht_sensor!=None): print("Sonde DHT connectée")
		else: print("Sonde DHT non connectée")
		self.dht_pin=24

		#######################################
		#GPIO DES BOUTONS
		#######################################
		self.KEY_1_PIN=6
		self.KEY_2_PIN=13
		self.KEY_3_PIN=19
		self.KEY_4_PIN=26

		###################################################
		#Chargement fichier ini: descriptions des fonctionnalités
		###################################################
		self.radiolistfilename=os.path.dirname(os.path.realpath(__file__))+"/radiolist.json"
		self.radiolist=loadjson(self.radiolistfilename,"name")
		for i in range(0,len(self.radiolist)):
			print("Station "+str(i)+" id:"+str(self.radiolist[i]["id"])+"  nom:"+self.radiolist[i]["name"]+"  url:"+self.radiolist[i]["url"])
		self.radioselected=-1
		self.radioparamfilename=os.path.dirname(os.path.realpath(__file__))+"/radioparam.ini"
		r=loadradioini(self.radioparamfilename)
		self.radioselected=r["radioselected"]
		self.tempoffset=r["tempoffset"]
		#####################
		#Clavier
		#####################
		self.clickshort=100
		self.clicklong=1000
		self.KB=Keyboard(self.KEY_1_PIN,self.KEY_2_PIN,self.KEY_3_PIN,self.KEY_4_PIN,self.clickshort,self.clicklong)

		#####################################
		# INIT DISPLAY
		#####################################
		try:
			self.lcd=liquidcrystal_i2c.lcd(0x27)
		except:
			print("----------------------------------------")
			print("Erreur de communication avec l'écran LCD")
			print("----------------------------------------")
			sys.exit(-1)
		
		self.lcd.clear()  
		self.lcd.display("STARTING....",1,0)  
		time.sleep(1)
		self.lcd.clear()
	
	##########################################
	# DECLACHEMENT ECOUTE RADIO
	##########################################
	def start_stop_playing_radio(self,radio=""):
		if self.radiothread!=None:
			print("stop radio PID="+str(self.radiothread.pid))
			os.kill(self.radiothread.pid, signal.SIGTERM)
			#self.radiothread.kill()
			self.radiothread=None
			return
		if radio=="": return
		cmd=["ffplay","-v","0","-nodisp","-autoexit",radio]
		self.radiothread=subprocess.Popen(cmd, shell=False)
		print("start radio PID="+str(self.radiothread.pid))
		
	def detect_2_button(self,a,b):
		sleeptime=0.01
		result=""
		if ((GPIO.input(a) == 0) and (GPIO.input(b) == 0)):
			button_press_timer = 0
			while (GPIO.input(a) == 0) and (GPIO.input(b) == 0) and (button_press_timer<self.longtime):
				time.sleep(sleeptime)
				button_press_timer += sleeptime
			if button_press_timer>=self.longtime:  result="LONG_"
			elif button_press_timer>=sleeptime:   result="SHORT_"
		if result!="":
			if a==self.KEY_1_PIN: result+="K1_"
			elif a==self.KEY_2_PIN: result+="K2_"
			elif a==self.KEY_3_PIN: result+="K3_"
			elif a==self.KEY_4_PIN: result+="K4_"
			if b==self.KEY_1_PIN: result+="K1"
			elif b==self.KEY_2_PIN: result+="K2"
			elif b==self.KEY_3_PIN: result+="K3"
			elif b==self.KEY_4_PIN: result+="K4"
		return result

	#Afficher la date et l'heure
	def ecran_heure(self):
		#ne rien faire si rien n'a changé
		dt = datetime.datetime.now()
		if (dt.minute==self.oldmin): return
		self.oldmin=dt.minute
		#Effacer
		self.lcd.clear()
		
		#HEURE  ET DATE
		WEEKDAYS= ['Dim', 'Lun','Mar','Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
		MONTHS=['', 'Jan','Fev','Mars','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc'];
		dt = datetime.datetime.now()
		#TEXTE pour heure
		line="{:02}".format(dt.hour)+":"+"{:02}".format(dt.minute)
		self.lcd.display(line,0,0)
		
		if (self.radioselected<0):
			line=WEEKDAYS[dt.isoweekday()]+" {:02}".format(dt.day)+" "+MONTHS[dt.month]
		else:
			line=self.radiolist[self.radioselected]["name"]
		self.lcd.display(line,0,6)
		
		#Temperature : toutes les 2 secondes maxi
		todo=0
		if (self.dht_sensor!=None):
			if self.ts_last_temp==None: todo=1
			elif (datetime.datetime.now() - self.ts_last_temp).total_seconds()>2: 
				todo=1
			if (todo==1):
				self.ts_last_temp=datetime.datetime.now()
				temp,humidity=get_dht(self.dht_sensor,self.dht_pin,self.tempoffset)
				if (temp!=None): 
					self.old_temp,self.old_humidity=temp,humidity
				else: temp,humidity = self.old_temp,self.old_humidity
			else:
				temp,humidity=self.old_temp,self.old_humidity

			if (temp!=None):
				#TEXTE pour Temperature
				if temp>=0: line="+"
				line+="{:02}".format(temp)+" C   {:02}".format(humidity)+" %"
				self.lcd.display_line(line,2)

	######################################
	# POWEROFF
	######################################
	def poweroff(self):
		self.start_stop_playing_radio("")
		line="  POWERING OFF  "
		self.lcd.display_line(line,2)
		time.sleep(3)
		self.lcd.clear()
		self.lcd.backlight(0)
		s = os.popen("poweroff").read().strip()

	######################################
	#changer station radio
	######################################
	def next_station(self,liste=[]):
		self.start_stop_playing_radio("")
		self.radioselected=self.radioselected+1
		print(self.radioselected)
		if self.radioselected>=len(self.radiolist):
			self.radioselected=0
		if self.radioselected>=0:
			#print("Selected : "+self.radiolist[self.radioselected]["name"])
			self.start_stop_playing_radio(self.radiolist[self.radioselected]["url"])
		self.oldmin=-1

		saveini({"radioselected":self.radioselected},self.radioparamfilename)
		return
		
	def prev_station(self,liste=[]):
		self.start_stop_playing_radio("")
		self.radioselected=self.radioselected-1
		if self.radioselected<0:
			self.radioselected=len(self.radiolist)-1
		if self.radioselected>=0:
			#print("Selected : "+self.radiolist[self.radioselected]["name"])
			self.start_stop_playing_radio(self.radiolist[self.radioselected]["url"])
		self.oldmin=-1
		saveini({"radioselected":self.radioselected},self.radioparamfilename)
		return
######################################
# PARTIE SERVEUR WEB (FLASK)
######################################
web_app = Flask(__name__)
reveil = None  # Sera initialisé dans le main

@web_app.route('/')
def index():
	# Lit l'état depuis le fichier .ini pour être raccord avec l'appareil
	config = configparser.ConfigParser()
	config.read(reveil.radioparamfilename)
	current_id = config.get('radio', 'radioselected', fallback="0")
	is_playing = reveil.radiothread is not None
	return render_template('index.html', radios=reveil.radiolist, current_id=str(current_id), is_playing=is_playing)
	
# Route pour envoyer l'état complet (y compris température et humidité) en temps réel
@web_app.route('/status', methods=['GET'])
def get_status():
	is_playing = reveil.radiothread is not None
	# On formate proprement pour éviter les valeurs "None" sur le site
	temp_val = f"{reveil.old_temp}°C" if reveil.old_temp is not None else "--°C"
	hum_val = f"{reveil.old_humidity}%" if reveil.old_humidity is not None else "--%"
	
	return jsonify({
		"is_playing": is_playing,
		"current_id": reveil.radioselected,
		"temperature": temp_val,
		"humidity": hum_val
	})
	
@web_app.route('/action', methods=['POST'])
def click_btn1():
	# Bouton 1 (à gauche) -> Appui long = POWEROFF
	# Par sécurité sur le web, on peut choisir de couper le son, ou de l'éteindre pour de vrai :
	print("🔌 Ordre d'extinction reçu depuis le Web")
	reveil.poweroff()
	return jsonify({"status": "success"})

@web_app.route('/click/btn2', methods=['POST'])
def click_btn2():
	# Bouton 2 -> Appui court = START / STOP radio
	if reveil.radiothread is not None:
		reveil.start_stop_playing_radio("") # Stop
	elif reveil.radioselected > -1:
		reveil.start_stop_playing_radio(reveil.radiolist[reveil.radioselected]["url"]) # Start
	reveil.oldmin = -1
	return jsonify({"status": "success"})


@web_app.route('/click/btn3', methods=['POST'])
def click_btn3():
	# Bouton 3 -> STATION PRÉCÉDENTE
	reveil.prev_station(reveil.radiolist)
	reveil.oldmin = -1
	return jsonify({"status": "success", "is_playing": is_playing, "current_id": str(reveil.radioselected)})

@web_app.route('/click/btn4', methods=['POST'])
def click_btn4():
	# Bouton 4 (à droite) -> STATION SUIVANTE
	reveil.next_station(reveil.radiolist)
	reveil.oldmin = -1
	return jsonify({"status": "success", "is_playing": is_playing, "current_id": str(reveil.radioselected)})

def run_flask():
	# Désactive le logger par défaut pour éviter de polluer la console
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)
	web_app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False)
	
	
######################################
if (__name__ == "__main__"):
	
	
	#Pas d'horloge RTC présente
	RTC=False 
	if (RTC==True) : starting_rtc()
	
	print("DEMARRAGE A :")
	printcurrentdatetime()
	
	#########################################################
	# VERIFICATION INITIALES
	#########################################################
	if int(datetime.datetime.now().strftime("%Y"))<=2001:
		print("Date-Heure incorrecte : pas d'horloge et pas de connexion internet !")
		sys.exit(-1)
	
	reveil=MaRadio(True)

	if os.path.exists(reveil.radiolistfilename)==False:
		print("Fichier "+reveil.radiolistfilename+" absent")
		sys.exit(-1)

	if len(reveil.radiolist)==0:
		print("Le fichier "+reveil.radiolistfilename+" ne contient pas d'information concernant des stations radio")
		sys.exit(-1)
		
	#########################################################
	# FIN DES VERIFICATIONS INITIALES
	#########################################################
	
	# DÉMARRAGE DU SERVEUR WEB DANS UN THREAD SÉPARÉ
	web_thread = threading.Thread(target=run_flask)
	web_thread.daemon = True
	web_thread.start()
	print("Serveur Web démarré sur http://[IP_DU_RASPBERRY]:5000")
	
	#Clavier
	reveil.KB.start()
	
	# Variable locale pour détecter un changement externe du fichier .ini par le web
	last_ini_radio = reveil.radioselected
	
	# Variables de temps pour espacer la vérification du fichier INI
	dernier_check_ini = 0
	intervalle_check_ini = 1.0  # On vérifie le fichier toutes les 1.0 seconde
	
	while True:
		try:

			# 1. Vérification du fichier INI (Web -> Écran) espacée dans le temps de intervalle_check_ini
			temps_actuel = time.time()
			if (temps_actuel - dernier_check_ini) >= intervalle_check_ini:
				dernier_check_ini = temps_actuel
				
				config = configparser.ConfigParser()
				try:
					if os.path.exists(reveil.radioparamfilename):
						config.read(reveil.radioparamfilename)
						ini_radio = int(config.get('radio', 'radioselected', fallback=reveil.radioselected))
						if ini_radio != last_ini_radio:
							reveil.radioselected = ini_radio
							last_ini_radio = ini_radio
							reveil.oldmin = -1  # Force l'écran à se mettre à jour
				except:
					pass
			
			# 2. Gestion ecran
			reveil.ecran_heure()
			reveil.KB.lock.acquire()
			btn,typ=reveil.KB.wich_btn()
			#play / pause
			if (btn=="K_1") and (typ=="short"):
				reveil.next_station(reveil.radiolist)
			elif (btn=="K_2") and (typ=="short"):
				reveil.prev_station(reveil.radiolist)
			elif (btn=="K_3") and (typ=="short"):
				if reveil.radiothread!=None: reveil.start_stop_playing_radio("")
				elif (reveil.radioselected>-1): reveil.start_stop_playing_radio(reveil.radiolist[reveil.radioselected]["url"])
				reveil.oldmin=-1
			elif (btn=="K_4") and (typ=="long"):
				reveil.poweroff()
			reveil.KB.lock.release()
			time.sleep(0.01)
		except KeyboardInterrupt:
			#reveil.KB.join()
			#stopper une lecture de son si en cours
			reveil.start_stop_playing_radio("")
			sys.exit(-1)


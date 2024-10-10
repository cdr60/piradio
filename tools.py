#!/usr/bin/python3
from configparser import ConfigParser
import os
import json
import tempfile

######################################################
# Lecture du fichier Temp pour savoir s'il y a eu changement
######################################################
def readhaschanged():
	TMPCHANGEFILE=tempfile.gettempdir()+os.path.sep+"pirevreil.tmp"
	if os.path.exists(TMPCHANGEFILE)==False: return False
	file_contents=""
	with open(TMPCHANGEFILE,'r') as tmp_file:
		file_contents = tmp_file.read(1)
	tmp_file.close()
	return (str(file_contents)=="1")
######################################################
# Ecriture du fichier Temp pour savoir s'il y a eu changement
######################################################
def writehaschanged(haschanged="0"):
	TMPCHANGEFILE=tempfile.gettempdir()+os.path.sep+"pirevreil.tmp"
	with open(TMPCHANGEFILE,'w+') as tmp_file:
		tmp_file.write(haschanged)
	tmp_file.close()
	return True

######################################################
# Lecture du fichier Ini de parametrage de l'alarme
######################################################
def initdata():
	#Initialisation data avec valeurs initiales
	data={}
	data["alarme"]={"heure":"00:00","duree":"1","active":"0","beepindex":"","radioindex":"","fileindex":""}
	data["audio"]={"beepindex":"","radioindex":"","fileindex":""}
	data["click"]={"short":"200","long":"1000"}
	data["color"]={"font_1_d":"#A4A4A4","font_1_n":"#939393","font_2_d":"#D4D4D4","font_2_n":"#C3C3C3","ico_d":"#D4D4D4","ico_n":"#C3C3C3","background":"#000000","day_start":"08:00","day_end":"2200"}
	return data

def loadjson(jsonfile):
	result=[]
	print("Lecture de "+jsonfile)
	if os.path.exists(jsonfile)==False:
		print("Fichier "+jsonfile+" absent")
		return result
		
	with open(jsonfile) as user_file:
		file_contents = user_file.read()
	try:
		result = json.loads(file_contents)
	except:
		print("Fichier "+jsonfile+" mal formé")
		result=[]
	user_file.close()
	return result


def loadini(ficini,alarmelist,radiolist,audiolist):
	data=initdata()
	print("Lecture de "+ficini)
	if os.path.exists(ficini)==False:
		print("Fichier absent")
	parser = ConfigParser()	
	parser.read(ficini)
	if parser.has_section("alarme")==False: parser.add_section("alarme") 
	if parser.has_section("audio")==False: parser.add_section("audio") 
	if parser.has_section("click")==False: parser.add_section("click") 
	if parser.has_section("color")==False: parser.add_section("color") 
	#######################################################
	# COULEUR DE LA FONT DU TEXTE 1 DE JOUR (GROS TEXTES)
	#######################################################
	if (parser.has_option("color", "font_1_d")):
		ss=parser.get("color", "font_1_d")
		if (ss[0]!="#"): ss="#A4A4A4"
		if (len(ss)!=7): ss="#A4A4A4"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#A4A4A4"
		data["color"]["font_1_d"]=str(ss)
	else: parser.set("color","font_1_d",data["color"]["font_1_d"])
	
	#######################################################
	# COULEUR DE LA FONT DU TEXTE 1 DE NUIT (GROS TEXTES)
	#######################################################
	if (parser.has_option("color", "font_1_n")):
		ss=parser.get("color", "font_1_n")
		if (ss[0]!="#"): ss="#C3C3C3"
		if (len(ss)!=7): ss="#C3C3C3"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#C3C3C3"
		data["color"]["font_1_n"]=str(ss)
	else: parser.set("color","font_1_n",data["color"]["font_1_n"])

	###########################################################
	# COULEUR DE LA FONT DU TEXTE 2 DE JOUR (PETITS TEXTES)
	###########################################################
	if (parser.has_option("color", "font_2_d")):
		ss=parser.get("color", "font_2_d")
		if (ss[0]!="#"): ss="#D4D4D4"
		if (len(ss)!=7): ss="#D4D4D4"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#D4D4D4"
		data["color"]["font_2_d"]=str(ss)
	else: parser.set("color","font_2_d",data["color"]["font_2_d"])

	###########################################################
	# COULEUR DE LA FONT DU TEXTE 2 DE NUIT (PETITS TEXTES)
	###########################################################
	if (parser.has_option("color", "font_2_n")):
		ss=parser.get("color", "font_2_n")
		if (ss[0]!="#"): ss="#C3C3C3"
		if (len(ss)!=7): ss="#C3C3C3"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#C3C3C3"
		data["color"]["font_2_n"]=str(ss)
	else: parser.set("color","font_2_n",data["color"]["font_2_n"])	
	
	#############################################
	# COULEUR DES ICONES DE JOUR
	#############################################
	if (parser.has_option("color", "ico_d")):
		ss=parser.get("color", "ico_d")
		if (ss[0]!="#"): ss="#D4D4D4"
		if (len(ss)!=7): ss="#D4D4D4"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#D4D4D4"
		data["color"]["ico_d"]=str(ss)
	else: parser.set("color","ico_d",data["color"]["ico_d"])

	#############################################
	# COULEUR DES ICONES DE NUIT
	#############################################
	if (parser.has_option("color", "ico_n")):
		ss=parser.get("color", "ico_n")
		if (ss[0]!="#"): ss="#C3C3C3"
		if (len(ss)!=7): ss="#C3C3C3"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#C3C3C3"
		data["color"]["ico_n"]=str(ss)
	else: parser.set("color","ico_n",data["color"]["ico_n"])

	#############################################
	# COULEUR DU FOND D'ECRAN
	#############################################
	if (parser.has_option("color", "background")):
		ss=parser.get("color", "background")
		if (ss[0]!="#"): ss="#000000"
		if (len(ss)!=7): ss="#000000"
		sr=ss[1:3]
		sg=ss[3:5]
		sb=ss[5:7]
		try:
			ir=int(sr,16)
			ig=int(sg,16)
			ib=int(sb,16)
		except:
			ss="#000000"
		data["color"]["background"]=str(ss)
	else: parser.set("color","background",data["color"]["background"])
	
	#############################################
	# DEBUT ET FIN DE LA JOURNEE(CHANGEMENT AUTO DE COULEUR)
	#############################################
	if (parser.has_option("color", "day_start")):
		ss=parser.get("color", "day_start")
		tb=ss.split(":")
		if (len(tb)!=2): 
			ss="08:00"
			tb[0]="08"
			tb[1]="00"
		try:
			h=int(tb[0])
			m=int(tb[1])
		except:
			ss="08:00"
		data["color"]["day_start"]=str(ss)
	else: parser.set("color","day_start",data["color"]["day_start"])
	
	if (parser.has_option("color", "day_end")):
		ss=parser.get("color", "day_end")
		tb=ss.split(":")
		if (len(tb)!=2): 
			ss="22:00"
			tb[0]="22"
			tb[1]="00"
		try:
			h=int(tb[0])
			m=int(tb[1])
		except:
			ss="22:00"
		data["color"]["day_end"]=str(ss)
	else: parser.set("color","day_end",data["color"]["day_end"])
	
	#############################################
	# DUREE DU CLICK COURT EN MILLISECONDES
	#############################################
	if (parser.has_option("click", "short")):
		ss=parser.get("click", "short")
		s=1
		try:
			s=int(ss)
		except:
			s=200
		if s<5: s=200
		data["click"]["short"]=str(s)
	else: parser.set("click","short",data["click"]["short"])
	#############################################
	# DUREE DU CLICK LONG EN MILLISECONDES
	#############################################
	if (parser.has_option("click", "long")):
		ss=parser.get("click", "long")
		s=1
		try:
			s=int(ss)
		except:
			s=1000
		if s<int(data["click"]["short"]): data["click"]["long"]=str(int(data["click"]["short"])+500)
	else: parser.set("click","long",data["click"]["long"])
	
	#############################################
	# ALARME DU REVEIL ACTIVE OU PAS
	#############################################
	if (parser.has_option("alarme", "active")):
		try:
			x=int(parser.get("alarme", "active"))
		except:
			x=0
		if (x<0 or x>1): x=0
		data["alarme"]["active"]=str(x)
	else: parser.set("alarme","active",data["alarme"]["active"])
	#############################################
	# HEURE DU REVEIL
	#############################################
	if (parser.has_option("alarme", "heure")):
		tb=parser.get("alarme", "heure").split(":")
		h,m=0,0
		if len(tb)>0:
			try:
				h=int(tb[0])
			except:
				h=0
		if len(tb)>1:
			try:
				m=int(tb[1])
			except:
				m=0
		if (h<0) or (h>23): h=0
		if (m<0) or (m>59): m=0
		data["alarme"]["heure"]="{:02}".format(h)+":"+"{:02}".format(m)
	else: parser.set("alarme","heure",data["alarme"]["heure"])
	#############################################
	# DUREE DU REVEIL EN MINUTES
	#############################################
	if (parser.has_option("alarme", "duree")):
		sm=parser.get("alarme", "duree")
		m=1
		try:
			m=int(sm)
		except:
			m=1
		if m<1: m=1
		data["alarme"]["duree"]=m
	else: parser.set("alarme","duree",data["alarme"]["duree"])
	
	if (parser.has_option("alarme", "active")):
		try:
			x=int(parser.get("alarme", "active"))
		except:
			x=0
		if (x<0 or x>1): x=0
		data["alarme"]["active"]=str(x)
	else: parser.set("alarme","active",data["alarme"]["active"])
	#############################################
	# BEEP CHOISIS POUR LE REVEIL
	#############################################
	if (parser.has_option("alarme", "beepindex")):
		try:
			x=int(parser.get("alarme", "beepindex"))
		except:
			x=None
		if x!=None: 
			if (x<0) or (x>len(alarmelist)-1): x=None
		if x!=None: data["alarme"]["radioindex"]=str(x)
	else: parser.set("alarme","beepindex",data["alarme"]["beepindex"])
	#############################################
	# STATION RADIO CHOISIS POUR LE REVEIL
	#############################################
	if (parser.has_option("alarme", "radioindex")):
		try:
			x=int(parser.get("alarme", "radioindex"))
		except:
			x=None
		if x!=None: 
			if (x<0) or (x>len(radiolist)-1): x=None
		if x!=None: data["alarme"]["radioindex"]=str(x)
	else: parser.set("alarme","radioindex",data["alarme"]["radioindex"])
	#############################################
	# FICHIER AUDIO CHOISIS POUR LE REVEIL
	#############################################
	if (parser.has_option("alarme", "fileindex")):
		try:
			x=int(parser.get("alarme", "fileindex"))
		except:
			x=None
		if x!=None: 
			if (x<0) or (x>len(audiolist)-1): x=None
		if x!=None: data["alarme"]["fileindex"]=str(x)
	else: parser.set("alarme","fileindex",data["alarme"]["fileindex"])

	#############################################
	# BEEP A ECOUTER HORS REVEIL
	#############################################
	if (parser.has_option("audio", "beepindex")):
		try:
			x=int(parser.get("audio", "beepindex"))
		except:
			x=None
		if x!=None:
			if (x<0) or (x>len(alarmelist)-1): x=None
		if x!=None: data["audio"]["beepindex"]=str(x)
	else: parser.set("audio","beepindex",data["audio"]["beepindex"])
			
	#############################################
	# RADIO A ECOUTER HORS REVEIL
	#############################################
	if (parser.has_option("audio", "radioindex")):
		try:
			x=int(parser.get("audio", "radioindex"))
		except:
			x=None
		if x!=None:
			if (x<0) or (x>len(radiolist)-1): x=None
		if x!=None: data["audio"]["radioindex"]=str(x)
	else: parser.set("audio","radioindex",data["audio"]["radioindex"])
	
	#############################################
	# AUDIO A ECOUTER HORS REVEIL
	#############################################
	if (parser.has_option("audio", "fileindex")):
		try:
			x=int(parser.get("audio", "fileindex"))
		except:
			x=None
		if x!=None:
			if (x<0) or (x>len(audiolist)-1): x=None
		if x!=None: data["audio"]["fileindex"]=str(x)
	else: parser.set("audio","fileindex",data["audio"]["fileindex"])
	
	if (data["alarme"]["beepindex"]=="") and (data["alarme"]["radioindex"]=="") and (data["alarme"]["fileindex"]==""):
		data["alarme"]["beepindex"]="0"

	with open(ficini, 'w') as configfile:
		parser.write(configfile)	
	return data


def saveini(data_ini,ficini):
	config = ConfigParser()
	config.read(ficini)
	config["alarme"]["heure"]=data_ini["alarme"]["heure"]
	config["alarme"]["active"]=data_ini["alarme"]["active"]
	config["alarme"]["beepindex"]=data_ini["alarme"]["beepindex"]
	config["alarme"]["radioindex"]=data_ini["alarme"]["radioindex"]
	config["alarme"]["fileindex"]=data_ini["alarme"]["fileindex"]
	config["audio"]["beepindex"]=data_ini["audio"]["beepindex"]
	config["audio"]["radioindex"]=data_ini["audio"]["radioindex"]
	config["audio"]["fileindex"]=data_ini["audio"]["fileindex"]
	config["color"]["font_1_d"]=data_ini["color"]["font_1_d"]
	config["color"]["font_1_n"]=data_ini["color"]["font_1_n"]
	config["color"]["font_2_d"]=data_ini["color"]["font_2_d"]
	config["color"]["font_2_n"]=data_ini["color"]["font_2_n"]
	config["color"]["ico_d"]=data_ini["color"]["ico_d"]
	config["color"]["ico_n"]=data_ini["color"]["ico_n"]
	config["color"]["background"]=data_ini["color"]["background"]
	config["color"]["day_start"]=data_ini["color"]["day_start"]
	config["color"]["day_end"]=data_ini["color"]["day_end"]
	with open(ficini,'w') as configfile:
		config.write(configfile)
	#Signal les changements
	writehaschanged("1")

#!/usr/bin/python3
from configparser import ConfigParser
import os
import json
import tempfile

def loadjson(jsonfile,sortedby="id"):
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
	result = sorted(result, key=lambda x: x[sortedby])
	return result


def loadradioini(ficini):
	result={"radioselected":-1}
	print("Lecture de "+ficini)
	parser = ConfigParser()
	if os.path.exists(ficini)==False:
		print("Fichier absent")
	else:
		parser.read(ficini)
		
	if parser.has_section("radio")==False: parser.add_section("radio") 
	#######################################################
	# DERNIERE RADIO SELECTIONNEE
	#######################################################
	if (parser.has_option("radio", "radioselected")):
		s=parser.get("radio", "radioselected")
		try:
			result["radioselected"]=int(s)
		except:
			result["radioselected"]=-1
	else: parser.set("radio","radioselected",str(result["radioselected"]))

	with open(ficini, 'w') as configfile:
		parser.write(configfile)	
	return result


def saveini(data_ini,ficini):
	config = ConfigParser()
	config.read(ficini)
	config["radio"]["radioselected"]=str(data_ini["radioselected"])
	with open(ficini,'w') as configfile:
		config.write(configfile)


#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, locale
import configparser
import time
from dialog import Dialog
import subprocess
import hashlib

# This is almost always a good thing to do at the beginning of your programs.
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog",autowidgetsize = "true")

settingsglobal = configparser.ConfigParser()
settingsglobal.optionxform = str
settingsglobal.read('global.cfg')
settingsglobalfile = open("global.cfg",'r')
mail = settingsglobal['Info_Certbot']['mail']
NameConfig = ''
Nom = ''

class ConfigurationWebSite:
	def __init__(self, name):
		self.NomFichier = name
		
	

def OuvertureConfig(NameConfigtmp=""):
	global settingsConfig
	global settingsConfigfile
	global NameConfig
	
	if NameConfigtmp == "":
		listConfigAvailable = os.listdir('./');
		i = 0
		listFinal = []
		for elem in listConfigAvailable:
			if '.cfg' in elem and elem != 'global.cfg':
				i = i+1
				listFinal.append((str(i), elem, 'off'))
				
		code, tag = d.radiolist("Quel configuration modifier?",
					   choices=listFinal, title="Choix Config")
		if code == Dialog.CANCEL or tag == '':
			sys.exit(0)
		else:
			for elem in listFinal:
				if elem[0] == tag:
					NameConfig = elem[1]
	else:
		NameConfig = NameConfigtmp
		
	if not os.path.exists(NameConfig):
		open(NameConfig,'w+')
	settingsConfig = configparser.ConfigParser()
	settingsConfig.optionxform = str
	settingsConfig.read(NameConfig)
	settingsConfigfile = open(NameConfig,'r')

def DemandeTypeCertificat(force="false"):
	if (settingsConfig['Config']).get('LevelCertificate', '') == '' or force == "true":
		settingsConfig['Config']['LevelCertificate'] = ''
	
	code, tag = d.radiolist("Niveau de certificat?",
				   choices=[('Haut', '2*ecdsa 384 + rsa 4096', 'on'),('Moyen', '2* rsa 4096 + rsa 2048', 'off'),('Bas', '3rsa 2048', 'off')], title="Choix Config")
	if code != Dialog.CANCEL:
		if tag == 'Moyen' or tag == 'Bas':
			CodeVerif = d.yesno("Tu es sûr de ton choix "+tag+"...? Non par ce que je veux pas dire... mais ces vraiment un choix de MERDE")
			if CodeVerif == Dialog.CANCEL:
				d.infobox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
				DemandeTypeCertificat()
			else:
				settingsConfig['Config']['LevelCertificate'] = tag
		else:
			settingsConfig['Config']['LevelCertificate'] = tag
	else:
		settingsConfig['Config']['LevelCertificate'] = "Haut"

def DemanderLevelSecurityApache(force="false"):
	if (settingsConfig['Config']).get('LevelApache', '') == '' or force == "true":
		settingsConfig['Config']['LevelApache'] = ''
	code, tag = d.radiolist("Niveau de encryptage?",
				   choices=[('Haut', 'TLS1.2+1.3 only, CHACHA20+AESGCM -> ECDH', 'on'),('Moyen', 'TLS1.0->TLS1.3,ECDH+AES ', 'off'),('Bas/Null', 'All, DH/ problem navigateur recent', 'off')], title="Choix Config")
	if code != Dialog.CANCEL:
		if tag == 'Moyen' or tag == 'Bas':
			CodeVerif = d.yesno("Tu es sûr de ton choix "+tag+"...? Non par ce que je veux pas dire... mais ces vraiment un choix de MERDE")
			if CodeVerif == Dialog.CANCEL:
				d.infobox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
				DemanderLevelSecurityApache()
			else:
				settingsConfig['Config']['LevelApache'] = tag
		else:
			settingsConfig['Config']['LevelApache'] = tag
	else:
		settingsConfig['Config']['LevelCertificate'] = "Haut"
	
def DemanderDNSCAA(force="false"):	
	if (settingsConfig['Config']).get('DNSCAActivate', '') == '' or force == "true":
		settingsConfig['Config']['DNSCAActivate'] = DemandeBinaire("Voulez-vous activer les records CAA des DNS?\nCreer un fichier zone secondaire DNS")
def DemanderHSTS(force="false"):
	if (settingsConfig['Config']).get('HSTSActivate', '') == '' or force == "true":
		settingsConfig['Config']['HSTSActivate'] = DemandeBinaire("Voulez-vous activer HSTS(HTTP Strict Transport Security)?\nSeulement si vous souhaitez le site en TLS only")
def DemanderOCSPStapling(force="false"):
	if (settingsConfig['Config']).get('OCSPStaplingActivate', '') == '' or force == "true":
		settingsConfig['Config']['OCSPStaplingActivate'] = DemandeBinaire("Voulez-vous activer OCSP Stapling?")
def DemanderHPKP(force="false"):
	if (settingsConfig['Config']).get('HPKPActivate', '') == '' or force == "true":
		settingsConfig['Config']['HPKPActivate'] = DemandeBinaire("Voulez-vous activer HPKP?\nAttention cela peut break vos configuration en production pour vos client si mal utilisé")
		'''if settingsConfig['Config']['HPKPActivate'] == True:
			settingsConfig['Config']['HPKPMaxAge'] = (settingsConfig['Config']).get('HPKPActivate', '6307200')
			Code, result = d.inputbox("Choisir le temps du Max Age HPKP en secondes (RFC conseille 5,184,000 secondes soit 60 jours)", init="5184000")
			if Code == Dialog.OK:'''
				
def DemanderTLSA(force="false"):
	if (settingsConfig['Config']).get('TLSAActivate', '') == '' or force == "true":
		settingsConfig['Config']['TLSAActivate'] = DemandeBinaire("Voulez-vous activer TLSA?\nCreer un fichier zone secondaire DNS")
def DemandeBinaire(Msg):
	code = d.yesno(Msg, title="Choix Config", yes_label="Oui" , no_label="Non")
	if code == Dialog.CANCEL:
		CodeVerif = d.yesno("tu peux cliquer sur non, mais je te le conseille pas.\n\
		Tu es sûr de ce que tu veux faire...?")
		if CodeVerif == Dialog.CANCEL:
			d.infobox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
			return DemandeBinaire(Msg)
		else:
			return "false"
	else:
		return "true"
''''''
#def DemanderCertificateTransparency():
	
def DemanderTimeBeforeAutoRenew(force="false"):
	if (settingsConfig['Config']).get('TimeRenew', '') == '' or force == "true":
		Code, result = d.inputbox("Temps avant le renouvellement automatique du certificat (Let's encrypt: 7 776 000s maximum(90j))", init="5184000")
		if Code == Dialog.OK:
			settingsConfig['Current']['TimeRenew'] = result
		else:
			settingsConfig['Current']['TimeRenew'] = 5184000
	
def VerificationConfig():
	global Nom
	global settingsConfig
	
	if settingsConfig.has_section('Config') == False:
		settingsConfig.add_section('Config')
	Nom = (settingsConfig['Config']).get('Name', NameConfig)
	Nom = Nom.split('.')
	Nom = Nom[0]
	settingsConfig['Config']['Name'] = Nom
	if not os.path.exists("./"+Nom+"/Archive/"):
		os.makedirs("./"+Nom+"/Archive")
	if ((settingsConfig['Config']).get('LevelCertificate', '') == '') or ((settingsConfig['Config']).get('LevelApache', '') == '') or ((settingsConfig['Config']).get('DNSCAActivate', '') == '') or ((settingsConfig['Config']).get('HSTSActivate', '') == '') or ((settingsConfig['Config']).get('OCSPStaplingActivate', '') == '') or ((settingsConfig['Config']).get('HPKPActivate', '') == '') or ((settingsConfig['Config']).get('TLSAActivate', '') == '' or ((settingsConfig['Config']).get('TimeRenew', '') == ''):
		DemandeTypeCertificat()
		DemanderTimeBeforeAutoRenew()
		DemanderLevelSecurityApache()
		DemanderHSTS()
		DemanderOCSPStapling()
		DemanderHPKP()
		DemanderDNSCAA()
		DemanderTLSA()
	settingsConfigfile = open(NameConfig,'w')
	settingsConfig.write(settingsConfigfile)
	settingsConfigfile = open(NameConfig,'r')
	if ((settingsConfig['Config']).get('LevelCertificate', '') == '') or ((settingsConfig['Config']).get('LevelApache', '') == '') or ((settingsConfig['Config']).get('DNSCAActivate', '') == '') or ((settingsConfig['Config']).get('HSTSActivate', '') == '') or ((settingsConfig['Config']).get('OCSPStaplingActivate', '') == '') or ((settingsConfig['Config']).get('HPKPActivate', '') == '') or ((settingsConfig['Config']).get('TLSAActivate', '') == '' or ((settingsConfig['Config']).get('TimeRenew', '') == ''):
		VerificationConfig()

def UpdateGlobal():
	if float(settingsConfig['Current']['EndRoll']) < time.time():#Fin du roll
		settingsConfig['Current']['ActiveCertificate'] = "Main"
		settingsConfig['Current']['LastRenew'] = TimeArchives
		settingsConfig['Current']['EndRoll'] = 0
		AppelACME()
		#Requete du certbot Roll
	elif settingsConfig['Current']['EndRoll'] == "0":
		if time.time() >= int(settingsConfig['Current']['LastRenew'])+int(settingsConfig['Current']['TimeRenew']):# temps pour le renuvellement depasser
			AppelACME()
			#Requete pour renouvellement crt
		

def DemanderCnf():
	#Nom = 'NoKnow'
	settingscnf = configparser.ConfigParser()
	settingscnf.optionxform = str
	settingscnf.read('./'+Nom+'/'+Nom+'.cnf')
	settingscnffile = open('./'+Nom+'/'+Nom+'.cnf','w+')
	
	print (settingscnf.has_section('req'))
	if settingscnf.has_section('req') == False:
		settingscnf.add_section('req')
	if settingscnf.has_section('req_distinguished_name') == False:
		settingscnf.add_section('req_distinguished_name')
	settingscnf['req']['distinguished_name'] = "req_distinguished_name"
	settingscnf['req_distinguished_name']['countryName'] = (settingscnf['req_distinguished_name']).get('countryName', 'FR')
	settingscnf['req_distinguished_name']['stateOrProvinceName'] = (settingscnf['req_distinguished_name']).get('stateOrProvinceName', 'France')
	settingscnf['req_distinguished_name']['localityName'] = (settingscnf['req_distinguished_name']).get('localityName', 'Paris')
	settingscnf['req_distinguished_name']['organizationName'] = (settingscnf['req_distinguished_name']).get('organizationName', 'Eradicate GAFA')
	settingscnf['req_distinguished_name']['commonName'] = (settingscnf['req_distinguished_name']).get('commonName', '')
	
	multi = d.yesno("Voulez-vous associer plusieurs domaines pour ce certificat")
	distinguished_name=[('Country Name (2 letter code)', 1, 2, settingscnf['req_distinguished_name']['countryName'], 1, 40, 2, 2),\
	('State or Province Name (full name)', 2, 2, settingscnf['req_distinguished_name']['stateOrProvinceName'], 2, 40, 18, 30),\
	('Locality Name (eg, city)', 3, 2, settingscnf['req_distinguished_name']['localityName'], 3, 40, 18, 30),\
	('Organization Name (eg, company)', 4, 2, settingscnf['req_distinguished_name']['organizationName'], 4, 40, 18, 30)]
	if multi == Dialog.CANCEL:# Si un seul domaine on ajout Common Name
		distinguished_name.append(('Common Name (e.g. server FQDN or YOUR name)', 5, 2, 'Example.com', 5, 50, 18, 30))
		settingscnf.remove_section('v3_req')
		settingscnf.remove_section('alt_names')
		settingscnf.remove_option('req','req_extensions')
	Code, info = d.form("Indiquez les informations du certificat", elements=distinguished_name)
	
	settingscnf['req_distinguished_name']['countryName'] = info[0]
	settingscnf['req_distinguished_name']['stateOrProvinceName'] = info[1]
	settingscnf['req_distinguished_name']['localityName'] = info[2]
	settingscnf['req_distinguished_name']['organizationName'] = info[3]
	settingscnf['req_distinguished_name']['commonName'] = info[4]
	
	if multi == Dialog.OK:
		settingscnf['req_distinguished_name']['commonName'] = ''
		if settingscnf.has_section('alt_names') == False:
			settingscnf.add_section('alt_names')
		if settingscnf.has_section('v3_req') == False:
			settingscnf.add_section('v3_req')
		settingscnf['req']['req_extensions'] = "v3_req"
		settingscnf['v3_req']['subjectAltName'] = "@alt_names"
		ListDomains = []
		for settingscnf.options("alt_names") as option:
			ListDomains.append(settingscnf['alt_names'][option])
		if ListDomains.count == 0:
			ListDomains = ""
		else:
			ListDomains = ListDomains.join(";")
		Code, domains = d.inputbox("Taper les differents domaines pour ce certificat séparer par des ;",init=ListDomains)
		domains = domains.split(';')
		i = 1
		for elem in domains:
			settingscnf['alt_names']['DNS.'+str(i)] = elem
			i = i+1

	#settingscnffile = open('./'+Nom+'/'+Nom+'.cnf','w')#settingscnffile = open('./'+Nom+'/'+Nom+'.cnf','r+') 
	settingscnf.write(settingscnffile)
	
	
def CreationKeyAndCsr(Roll = False):
	global Nom
	TimeArchives = time.time()
	
	
	if Roll and settingsConfig['Current']['ActiveCertificate'] != "Roll":
		shutil.copy("./"+Nom+"/"+settingsConfig['Current']['ActiveCertificate']+".key", "./"+Nom+"/Roll.key")
		shutil.copy("./"+Nom+"/"+settingsConfig['Current']['ActiveCertificate']+".csr", "./"+Nom+"/Roll.csr")
		settingsConfig['Current']['ActiveCertificate'] = "Roll"
		settingsConfig['Current']['EndRoll'] = time.time()+5184000
		AppelACME()
		#Generation Certbot Roll
######################################	
		
	if os.path.exists("./"+Nom+"/Main.key") or os.path.exists("./"+Nom+"/Backup1.key") or os.path.exists("./"+Nom+"/Backup2.key"):
		shutil.move("./"+Nom+"/Main.key", "./"+Nom+"/Archive/"+TimeArchives+"/Main.key")
		shutil.move("./"+Nom+"/Backup1.key", "./"+Nom+"/Archive/"+TimeArchives+"/Backup1.key")
		shutil.move("./"+Nom+"/Backup2.key", "./"+Nom+"/Archive/"+TimeArchives+"/Backup2.key")

	if settingsConfig['Config']['LevelCertificate'] == "Haut":
		os.system("openssl ecparam -genkey -name secp384r1 > ./"+Nom+"/Main.key")
		os.system("openssl ecparam -genkey -name secp384r1 > ./"+Nom+"/Backup1.key")
		os.system("openssl genrsa -out ./"+Nom+"/Backup2.key 4096")
	elif settingsConfig['Config']['LevelCertificate'] == "Moyen":
		os.system("openssl genrsa -out ./"+Nom+"/Main.key 4096")
		os.system("openssl genrsa -out ./"+Nom+"/Backup1.key 4096")
		os.system("openssl genrsa -out ./"+Nom+"/Backup2.key 2048")
	elif settingsConfig['Config']['LevelCertificate'] == "Bas":
		os.system("openssl genrsa -out ./"+Nom+"/Main.key 2048")
		os.system("openssl genrsa -out ./"+Nom+"/Backup1.key 2048")
		os.system("openssl genrsa -out ./"+Nom+"/Backup2.key 2048")
	settingsConfig['Current']['ActiveCertificate'] = (settingsConfig['Current']).get('ActiveCertificate', "Main")# le certificat actif le principale ou une backup
	settingsConfig['Current']['LastRenew'] = TimeArchives
###############################################
	'''Demande de certificat csr'''
	if os.path.exists("./"+Nom+"/Main.csr") or os.path.exists("./"+Nom+"/Backup1.csr") or os.path.exists("./"+Nom+"/Backup2.csr"):
		shutil.move("./"+Nom+"/Main.csr", "./"+Nom+"/Archive/"+TimeArchives+"/Main.csr")
		shutil.move("./"+Nom+"/Backup1.csr", "./"+Nom+"/Archive/"+TimeArchives+"/Backup1.csr")
		shutil.move("./"+Nom+"/Backup2.csr", "./"+Nom+"/Archive/"+TimeArchives+"/Backup2.csr")

	os.system("openssl req -new -sha384 -key ./"+Nom+"/Main.key -nodes -out ./"+Nom+"/Main.csr -outform pem -config ./"+Nom+"/"+Nom+".cnf")
	os.system("openssl req -new -sha384 -key ./"+Nom+"/Backup1.key -nodes -out ./"+Nom+"/Backup1.csr -outform pem -config ./"+Nom+"/"+Nom+".cnf")
	os.system("openssl req -new -sha384 -key ./"+Nom+"/Backup2.key -nodes -out ./"+Nom+"/Backup2.csr -outform pem -config ./"+Nom+"/"+Nom+".cnf")
	AppelACME()
	#Generation Certbot settingsConfig['Current']['ActiveCertificate']
def AppelACME():
	#AppDir = os.getcwd()
	#os.chdir(AppDir+"/ToACME/")
	os.system("") #sudo ./../certbot/certbot-auto certonly --csr ./NoKnow/Main.csr --standalone --tls-sni-01-port 26226 --staging --cert-path ./NoKnow/Main_crt.pem --fullchain-path ./NoKnow/Main_fullchain.pem --chain-path ./ChainACME/Chain.pem.tmp
	#--cert-path ./NoKnow/Main_crt.pem
	#--fullchain-path ./NoKnow/Main_fullchain.pem
	#--chain-path ./ChainACME/Chain.pem.tmp
	
	# Verifier correspondance Chain Intermediaire
	listChain = os.listdir('./ChainACME/');
	ChainTmpFile = open("./ChainACME/Chain.pem.tmp",'r')
	tmpdigest = hashlib.sha224(ChainTmpFile.read()).hexdigest()
	ChainEqual = ""
	for elem in listChain:
		ChainFile = open("./ChainACME/"+elem,'r')
		digestTest = hashlib.sha224(ChainFile.read()).hexdigest()
		if digestTest == tmpdigest:
			ChainEqual = elem
	if ChainEqual == "":
		i = 1
		while os.path.exists("./ChainACME/Chain_"+i+".pem") :
			i = i+1
		shutil.move("./ChainACME/Chain.pem.tmp", "./ChainACME/Chain_"+i+".pem")
		ChainEqual = "Chain_"+i+".pem"
	settingsConfig['Current']['IntermediaireChain'] = ChainEqual
	
def UpdateZone():
	global mail
	global Nom
	global settingsConfig
	settingscnf = configparser.ConfigParser()
	settingscnf.optionxform = str
	settingscnf.read('./'+Nom+'/'+Nom+'.cnf')
	
	DemiZoneFile = open("./"+Nom+"/HalfZone.conf",'w+')
	proc = subprocess.Popen(['openssl x509 -noout -pubkey -in ./'+Nom+'/Main.crt  | openssl rsa -pubin -outform DER 2>/dev/null | sha256 | tr "a-z" "A-Z"'],stdout=PIPE,stdin=PIPE shell=True)
	hash = proc.stdout.read().split().at(1)
	
	if settingscnf['req_distinguished_name']['commonName'] != ''#OneDomain
		if settingsConfig['Config']['DNSCAActivate'] == "true":
			#############CAA#################
			DemiZoneFile.write(settingscnf['req_distinguished_name']['commonName']+".	IN	CAA	0 issue \"letsencrypt.org\"")
			DemiZoneFile.write(settingscnf['req_distinguished_name']['commonName']+".	IN	CAA	0 iodef \"mailto:"+mail"\"")
		if settingsConfig['Config']['TLSAActivate'] == "true":
			###############TLSA###############
			DemiZoneFile.write("_443._tcp."+settingscnf['req_distinguished_name']['commonName']+".	IN TLSA 3 1 1 "+hash)
	else:#multidomain
		ListDomains = []
		for settingscnf.options("alt_names") as option:
			ListDomains.append(settingscnf['alt_names'][option])
		for ListDomains as domain:
			if settingsConfig['Config']['DNSCAActivate'] == "true":
				#############CAA#################
				DemiZoneFile.write(domain+".	IN	CAA	0 issue \"letsencrypt.org\"")
				DemiZoneFile.write(domain+".	IN	CAA	0 iodef \"mailto:"+mail"\"")
			if settingsConfig['Config']['TLSAActivate'] == "true":
				###############TLSA###############
				DemiZoneFile.write("_443._tcp."+domain+".	IN TLSA 3 1 1 "+hash)

def UpdateConfApache():
	global mail
	global Nom
	global settingsConfig
	ApacheInFile = open("./"+Nom+"/ApacheIn.conf",'w+')#in virtualhost
	ApacheOutFile = open("./"+Nom+"/ApacheOut.conf",'w+')#out virtualhost
	
	ApacheInFile.write("SSLCertificateFile /etc/letsencrypt/live/loasisdeschatsbleus.fr/fullchain.pem\n\
	SSLCertificateKeyFile /etc/letsencrypt/live/loasisdeschatsbleus.fr/privkey.pem")
def ActivationBackup():
	if settingsConfig['Current']['ActiveCertificate'] != "Roll":
		d.infobox("Vous êtes actuellement en Roll à cause de HPKP\n\
		Le programme refuse de faire automatiquement, si vous insistez faite le manuellement.")
	else:
		d.infobox("L'activation du backup revokera automatiquement les certificat précédent\n NB: il régènerera pas les clé automatiquement")
		code, tag = d.menu("Le certificat activé actuel est le "+settingsConfig['Current']['ActiveCertificate']+". Lequel voulez-vous activer?",
		choices=[('Main', 'Le certificat principale'),('Backup1', 'Backup online'),('Backup2', 'Backup offline')], title="Security")
		if code == Dialog.OK:
			if tag == settingsConfig['Current']['ActiveCertificate']:
				d.infobox("Bravo le génie, on sent que tu as eu ton bac avec mention...")
			else:
				settingsConfig['Current']['ActiveCertificate'] = tag
				AppelACME()
def PrintInclusion():
	print()
def ModificationConfig():
	code, tag = d.menu("Que voulez vous faire?",
		choices=[('1', 'DemandeTypeCertificat'),('2', 'DemanderLevelSecurityApache'),('3', 'DemanderHSTS'),('4', 'DemanderOCSPStapling'),('5', 'DemanderHPKP'),('6', 'DemanderDNSCAA'),('7', 'DemanderTLSA') ,('8', 'DemanderTimeBeforeAutoRenew')], title="Security")
	if code == Dialog.OK:
		if tag == "1":
			tmpConfig = settingsConfig['Config']['LevelCertificate']
			DemandeTypeCertificat()
			if tmpConfig != settingsConfig['Config']['LevelCertificate']:#Alors changement , verification Roll a cause de HPKP
				if settingsConfig['Config']['HPKPActivate'] == "true":
					d.menu("HPKP est actvé ou était activé encore trop récemment. Pour assurer à tout les clients la continuité du service, il faut effectué une rotation avec l'un des certificat fingerprinté dans HPKP. \n\
					Pour cela nous allons garder le certificat actif en ce moment: "+settingsConfig['Current']['ActiveCertificate']+"\n\
					Pendant le temps impartit du max-age, soit jusqu'au ... \n\
					Le certificat sera ensuite remplacer automatiquement à la prochaine update nouvellement générer\n\
					Êtes-vous d'accords avec la procédure suivante?",choices=[('1', 'Confirmer la procedure'),('2', 'Activé une clé backup avant d\'activer le roll'),('3', 'Tous annuler(j\'ai encore fait de la merde avec HPKP T-T )')])
					if code == Dialog.OK:
						if tag == "1":
							CreationKeyAndCsr(True)
						elif tag == "2":
							ActivationBackup()
							CreationKeyAndCsr(True)
				else:
					CreationKeyAndCsr()
		elif tag == "2":
			DemanderLevelSecurityApache()
		elif tag == "3":
			DemanderHSTS()
		elif tag == "4":
			DemanderOCSPStapling()
		elif tag == "5":
			DemanderHPKP()
		elif tag == "6":
			DemanderDNSCAA()
		elif tag == "7":
			DemanderTLSA()
		elif tag == "8":
			DemanderTimeBeforeAutoRenew()
def Accueil():
	global NameConfig

	code, tag = d.menu("Que voulez vous faire?",
		choices=[('1', 'Nouveau'),('2', 'Ouvrir'),('3', 'Test')], title="Security")
	if code == Dialog.CANCEL:
		sys.exit(0)
		
	if tag == "1":
		code, NameFile = d.inputbox("Choisir un nom de projet:")
		if code == Dialog.CANCEL:
			Accueil()
		elif code == Dialog.OK:
			OuvertureConfig(NameFile+".cfg")
	elif tag == "2":
		OuvertureConfig()
	elif tag == "3":
		OuvertureConfig("NK.cfg")
		DemanderCnf()

def MainMenu():
	code, tag = d.menu("Que voulez vous faire?",
		choices=[('1', 'Modifier les informations du certificat'),('2', 'Modifier la configuration'),('3', 'Regénerer les clé privé'),('4', 'Regénerer les certificats'),('5', 'Activer une backup'),('6', 'Afficher les lignes d\'inclusion')], title="Security")
	if code == Dialog.CANCEL:
		Accueil()
	else:
		if tag == "1":
			DemanderCnf()
		elif tag == "2":
			ModificationConfig()
		elif tag == "3":
			if settingsConfig['Config']['HPKPActivate'] = "true":
				CreationKeyAndCsr(True)
			else:
				CreationKeyAndCsr()
		elif tag == "4":
			AppelACME()
		elif tag == "5":
			ActivationBackup()
		elif tag == "6":
			PrintInclusion()
		
if len(sys.argv) >= 2:
	OuvertureConfig(sys.argv[1])
else:
	Accueil()
#VerificationConfig()
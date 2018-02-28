#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, locale
import configparser
import time
from dialog import Dialog
import subprocess
import hashlib
import urllib.request

# This is almost always a good thing to do at the beginning of your programs.
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog",autowidgetsize = "true")

NameConfig = ''


class ConfigurationGeneral:
	def __init__(self):
		if not os.path.exists('global.cfg'):
			open('global.cfg','w+')
			#settingsglobal = configparser.ConfigParser()
			#settingsglobal.optionxform = str
			#settingsglobal.read('global.cfg')
			#settingsglobal.add_section('Info_Certbot')
			self.mail = ''
			self.tel = ''
			self.EmplacementCertbot = ''
			self.Port = '443'
			self.ModificationConfigGeneral()
		if not os.path.exists("./Certbot/certbot-auto"):
			exe = urllib.request.urlopen("https://dl.eff.org/certbot-auto")
			os.makedirs("./Certbot/")
			with open("./Certbot/certbot-auto register --config ./Certbot/Preload.ini","wb+") as f:
				f.write(exe.read())
				#-> chmod a+x
		self.ReadAll()
		self.UpdateCertbot()
	def ReadAll(self):
		settingsglobal = configparser.ConfigParser()
		settingsglobal.optionxform = str
		settingsglobal.read('global.cfg')
		settingsglobalfile = open("global.cfg",'r')
		self.mail = settingsglobal['Info_Certbot']['mail']
		self.tel = settingsglobal['Info_Certbot']['tel']
		self.EmplacementCertbot = settingsglobal['Info_Certbot']['Emplacement']
		self.Port = settingsglobal['Info_Certbot']['Port_TLS_SNI']
	def UpdateCertbot(self):
		proc = subprocess.Popen(['sudo ./Certbot/certbot-auto --help'],stdout=subprocess.PIPE,stdin=subprocess.PIPE,shell=True)
		#while proc.returncode == None:
		print (proc.stdout.read().decode('utf-8')+"\r\n")
		#print (proc.stderr)
	def ModificationConfigGeneral(self):
		ListInfo=[('Mail', 1, 2, self.mail, 1, 40, 18, 30),\
		('Tel. (+00)', 2, 2, self.tel, 2, 40, 18, 30),\
		('Emplacement de Certbot(Optionel)', 3, 2, self.EmplacementCertbot, 3, 40, 18, 30),\
		('Port de communication Certbot', 4, 2, self.Port, 4, 40, 18, 30)]

		Code, info = d.form("Indiquez les informations pour le fonctionnement du programme", elements=ListInfo)
		settingsglobal = configparser.ConfigParser()
		settingsglobal.optionxform = str
		settingsglobal.add_section('Info_Certbot')
		settingsglobal['Info_Certbot']['mail'] = self.mail = info[0]
		settingsglobal['Info_Certbot']['tel'] = self.tel = info[1]
		settingsglobal['Info_Certbot']['Emplacement'] = self.EmplacementCertbot = info[2]
		settingsglobal['Info_Certbot']['Port_TLS_SNI'] = self.Port = info[3]
		file = open('global.cfg','w+')
		settingsglobal.write(file)
		if not os.path.exists("./Certbot/certbot-auto"):
			os.makedirs("./Certbot/")
		preloadcertbotini = open('./Certbot/Preload.ini','w+')
		preloadcertbotini.write('email = '+self.mail+'\r\nagree-tos = True\r\nupdate-registration = True\r\nwork-dir = ./Certbot/Worker/\r\nlogs-dir = ./Certbot/Log/\r\nconfig-dir = ./Certbot/Config/\r\nstaging = True')
		
		

class ConfigurationWebSite:
	def __init__(self, name):
		self.NomFichier = name
		self.settingsConfig = configparser.ConfigParser()
		self.settingsConfig.optionxform = str
		self.settingsConfig.read(self.NomFichier)
		if not os.path.exists(self.NomFichier):
			open(self.NomFichier ,'w+')
			self.settingsConfig.add_section('Config')
			self.settingsConfig.add_section('Current')
			Nom = (self.settingsConfig['Config']).get('Name', self.NomFichier)
			Nom = Nom.split('.')
			Nom = Nom[0]
			self.settingsConfig['Config']['Name'] = Nom
			self.NomConfig = self.settingsConfig['Config']['Name']
			os.makedirs("./"+self.NomConfig+"/Archive")
		#open(NameConfig,'r')
		self.NomConfig = self.settingsConfig['Config']['Name']
		self.AppConfig = ApplicationConfiguration(self)
		self.VerificationConfig()
		self.AppConfig.MainMenu()
		
	def GetConfig(self,Section,Name,FallBack=''):
		#return self.settingsConfig[Section][Name]
		return (self.settingsConfig[Section]).get(Name, FallBack)
	def SetConfig(self,Name,Valeur):
		self.settingsConfig['Current'][Name] = Valeur
		self.UpdateConfig()
	
	def ModificationConfig(self):
		code, tag = d.menu("Que voulez vous faire?",
			choices=[('1', 'DemandeTypeCertificat'),('2', 'DemanderLevelSecurityApache'),('3', 'DemanderHSTS'),('4', 'DemanderOCSPStapling'),('5', 'DemanderHPKP'),('6', 'DemanderDNSCAA'),('7', 'DemanderTLSA') ,('8', 'DemanderTimeBeforeAutoRenew')], title="Security")
		if code == Dialog.OK:
			if tag == "1":
				tmpConfig = self.settingsConfig['Config']['LevelCertificate']
				self.DemandeTypeCertificat("true")
				if tmpConfig != self.settingsConfig['Config']['LevelCertificate']:#Alors changement , verification Roll a cause de HPKP
					if self.settingsConfig['Config']['HPKPActivate'] == "true":
						d.menu("HPKP est actvé ou était activé encore trop récemment. Pour assurer à tout les clients la continuité du service, il faut effectué une rotation avec l'un des certificat fingerprinté dans HPKP. \n\
						Pour cela nous allons garder le certificat actif en ce moment: "+self.settingsConfig['Current']['ActiveCertificate']+"\n\
						Pendant le temps impartit du max-age, soit jusqu'au ... \n\
						Le certificat sera ensuite remplacer automatiquement à la prochaine update nouvellement générer\n\
						Êtes-vous d'accords avec la procédure suivante?",choices=[('1', 'Confirmer la procedure'),('2', 'Activé une clé backup avant d\'activer le roll'),('3', 'Tous annuler(j\'ai encore fait de la merde avec HPKP T-T )')])
						if code == Dialog.OK:
							if tag == "1":
								self.AppConfig.CreationKeyAndCsr(True)
							elif tag == "2":
								self.AppConfig.ActivationBackup()
								self.AppConfig.CreationKeyAndCsr(True)
					else:
						self.AppConfig.CreationKeyAndCsr()
			elif tag == "2":
				self.DemanderLevelSecurityApache("true")
				self.AppConfig.UpdateConfApache()
			elif tag == "3":
				self.DemanderHSTS("true")
				self.AppConfig.UpdateConfApache()
			elif tag == "4":
				self.DemanderOCSPStapling("true")
				self.AppConfig.UpdateConfApache()
			elif tag == "5":
				self.DemanderHPKP("true")
				self.AppConfig.UpdateConfApache()
			elif tag == "6":
				self.DemanderDNSCAA("true")
				self.AppConfig.UpdateZone()
			elif tag == "7":
				self.DemanderTLSA("true")
				self.AppConfig.UpdateZone()
			elif tag == "8":
				self.DemanderTimeBeforeAutoRenew("true")
		self.UpdateConfig()
		

	def DemandeTypeCertificat(self,force="false"):
		if (self.settingsConfig['Config']).get('LevelCertificate', '') == '' or force == "true":
			self.settingsConfig['Config']['LevelCertificate'] = ''
		
		code, tag = d.radiolist("Niveau de certificat?",
					   choices=[('Haut', '2*ecdsa 384 + rsa 4096', 'on'),('Moyen', '2* rsa 4096 + rsa 2048', 'off'),('Bas', '3rsa 2048', 'off')], title="Choix Config")
		if code != Dialog.CANCEL:
			if tag == 'Moyen' or tag == 'Bas':
				CodeVerif = d.yesno("Tu es sûr de ton choix "+tag+"...? Non par ce que je veux pas dire... mais ces vraiment un choix de MERDE")
				if CodeVerif == Dialog.CANCEL:
					d.infobox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
					self.DemandeTypeCertificat()
				else:
					self.settingsConfig['Config']['LevelCertificate'] = tag
			else:
				self.settingsConfig['Config']['LevelCertificate'] = tag
		else:
			self.settingsConfig['Config']['LevelCertificate'] = "Haut"

	def DemanderLevelSecurityApache(self,force="false"):
		if (self.settingsConfig['Config']).get('LevelApache', '') == '' or force == "true":
			self.settingsConfig['Config']['LevelApache'] = ''
		code, tag = d.radiolist("Niveau de encryptage?",
					   choices=[('Haut', 'TLS1.2+1.3 only, CHACHA20+AESGCM -> ECDH', 'on'),('Moyen', 'TLS1.0->TLS1.3,ECDH+AES ', 'off'),('Bas/Null', 'All, DH/ problem navigateur recent', 'off')], title="Choix Config")
		if code != Dialog.CANCEL:
			if tag == 'Moyen' or tag == 'Bas':
				CodeVerif = d.yesno("Tu es sûr de ton choix "+tag+"...? Non par ce que je veux pas dire... mais ces vraiment un choix de MERDE")
				if CodeVerif == Dialog.CANCEL:
					d.infobox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
					self.DemanderLevelSecurityApache()
				else:
					self.settingsConfig['Config']['LevelApache'] = tag
			else:
				self.settingsConfig['Config']['LevelApache'] = tag
		else:
			self.settingsConfig['Config']['LevelCertificate'] = "Haut"
		
	def DemanderDNSCAA(self,force="false"):	
		if (self.settingsConfig['Config']).get('DNSCAActivate', '') == '' or force == "true":
			self.settingsConfig['Config']['DNSCAActivate'] = DemandeBinaire("Voulez-vous activer les records CAA des DNS?\nCreer un fichier zone secondaire DNS")
	def DemanderHSTS(self,force="false"):
		if (self.settingsConfig['Config']).get('HSTSActivate', '') == '' or force == "true":
			self.settingsConfig['Config']['HSTSActivate'] = DemandeBinaire("Voulez-vous activer HSTS(HTTP Strict Transport Security)?\nSeulement si vous souhaitez le site en TLS only")
	def DemanderOCSPStapling(self,force="false"):
		if (self.settingsConfig['Config']).get('OCSPStaplingActivate', '') == '' or force == "true":
			self.settingsConfig['Config']['OCSPStaplingActivate'] = DemandeBinaire("Voulez-vous activer OCSP Stapling?")
	def DemanderHPKP(self,force="false"):
		if (self.settingsConfig['Config']).get('HPKPActivate', '') == '' or force == "true":
			self.settingsConfig['Config']['HPKPActivate'] = DemandeBinaire("Voulez-vous activer HPKP?\nAttention cela peut break vos configuration en production pour vos client si mal utilisé")
			'''if self.settingsConfig['Config']['HPKPActivate'] == True:
				self.settingsConfig['Config']['HPKPMaxAge'] = (self.settingsConfig['Config']).get('HPKPActivate', '6307200')
				Code, result = d.inputbox("Choisir le temps du Max Age HPKP en secondes (RFC conseille 5,184,000 secondes soit 60 jours)", init="5184000")
				if Code == Dialog.OK:'''
					
	def DemanderTLSA(self,force="false"):
		if (self.settingsConfig['Config']).get('TLSAActivate', '') == '' or force == "true":
			self.settingsConfig['Config']['TLSAActivate'] = DemandeBinaire("Voulez-vous activer TLSA?\nCreer un fichier zone secondaire DNS")
	
	def VerificationConfig(self):
		if (((self.settingsConfig['Config']).get('LevelCertificate', '') == '') or ((self.settingsConfig['Config']).get('LevelApache', '') == '') or ((self.settingsConfig['Config']).get('DNSCAActivate', '') == '') or ((self.settingsConfig['Config']).get('HSTSActivate', '') == '') or ((self.settingsConfig['Config']).get('OCSPStaplingActivate', '') == '') or ((self.settingsConfig['Config']).get('HPKPActivate', '') == '') or ((self.settingsConfig['Config']).get('TLSAActivate', '') == '') or ((self.settingsConfig['Current']).get('TimeRenew', '') == '')):
			self.DemandeTypeCertificat()
			self.DemanderTimeBeforeAutoRenew()
			self.DemanderLevelSecurityApache()
			self.DemanderHSTS()
			self.DemanderOCSPStapling()
			self.DemanderHPKP()
			self.DemanderDNSCAA()
			self.DemanderTLSA()
			self.UpdateConfig()
			self.VerificationConfig()
	def UpdateConfig(self):
		settingsConfigfile = open(self.NomFichier,'w')
		self.settingsConfig.write(settingsConfigfile)
		settingsConfigfile = open(self.NomFichier,'r')
		self.settingsConfig.read(settingsConfigfile)
	
	def DemanderTimeBeforeAutoRenew(self,force="false"):
		if (self.settingsConfig['Current']).get('TimeRenew', '') == '' or force == "true":
			Code, result = d.inputbox("Temps avant le renouvellement automatique du certificat (Let's encrypt: 7 776 000s maximum(90j))", init="5184000")
			if Code == Dialog.OK:
				self.settingsConfig['Current']['TimeRenew'] = result
			else:
				self.settingsConfig['Current']['TimeRenew'] = 5184000
		
	def DemanderCnf(self):
		settingscnf = configparser.ConfigParser()
		settingscnf.optionxform = str
		settingscnf.read('./'+self.NomConfig+'/'+self.NomConfig+'.cnf')
		

		SettingsActuelle['countryName'] = (settingscnf['req_distinguished_name']).get('countryName', 'FR')
		SettingsActuelle['stateOrProvinceName'] = (settingscnf['req_distinguished_name']).get('stateOrProvinceName', 'France')
		SettingsActuelle['localityName'] = (settingscnf['req_distinguished_name']).get('localityName', 'Paris')
		SettingsActuelle['organizationName'] = (settingscnf['req_distinguished_name']).get('organizationName', 'Eradicate GAFA')
		SettingsActuelle['commonName'] = (settingscnf['req_distinguished_name']).get('commonName', '')
		ListDomains = self.GetListDomains()
		
		Code, domains = d.inputbox("Ajouter un ou plusieurs nom de domaines pour ce certificat, séparé par des ;",init=ListDomains)
		domains = domains.split(';')
		
		distinguished_name=[('Country Name (2 letter code)', 1, 2, SettingsActuelle['countryName'], 1, 40, 2, 2),\
		('State or Province Name (full name)', 2, 2, SettingsActuelle['stateOrProvinceName'], 2, 40, 18, 30),\
		('Locality Name (eg, city)', 3, 2, SettingsActuelle['localityName'], 3, 40, 18, 30),\
		('Organization Name (eg, company)', 4, 2, SettingsActuelle['organizationName'], 4, 40, 18, 30)]

		Code, info = d.form("Indiquez les informations du certificat", elements=distinguished_name)
		
		NewCNF = configparser.ConfigParser()
		NewCNF.optionxform = str
		NewCNF.add_section('req')
		NewCNF['req']['distinguished_name'] = "req_distinguished_name"
		NewCNF.add_section('req_distinguished_name')
		NewCNF['req_distinguished_name']['countryName'] = info[0]
		NewCNF['req_distinguished_name']['stateOrProvinceName'] = info[1]
		NewCNF['req_distinguished_name']['localityName'] = info[2]
		NewCNF['req_distinguished_name']['organizationName'] = info[3]
		if domains.count == 1:
			NewCNF['req_distinguished_name']['commonName'] = domains[0]
		else:
			NewCNF['req_distinguished_name']['commonName'] = ""
			NewCNF['req']['req_extensions'] = "v3_req"
			NewCNF.add_section('v3_req')
			NewCNF['v3_req']['subjectAltName'] = "@alt_names"
			NewCNF.add_section('alt_names')
			i = 1
			for elem in domains:
				NewCNF['alt_names']['DNS.'+str(i)] = elem
				i = i+1

		#settingscnffile = open('./'+self.NomConfig+'/'+self.NomConfig+'.cnf','w+') 
		settingscnf.write(NewCNF)
	def GetListDomains(self):
		settingscnf = configparser.ConfigParser()
		settingscnf.optionxform = str
		settingscnf.read('./'+self.NomConfig+'/'+self.NomConfig+'.cnf')
		ListDomains = []
		if settingscnf['commonName'] != "":
			ListDomains.append(settingscnf['commonName'])
		for option in settingscnf.options("alt_names"):
			ListDomains.append(settingscnf['alt_names'][option])
		if ListDomains.count == 0:
			ListDomains = ""
		else:
			ListDomains = ListDomains.join(";")
		
		
class ApplicationConfiguration:
	def __init__(self, Config):
		self.Config = Config
		self.Nom = self.Config.GetConfig("Config","Name")
		
	def CreationKeyAndCsr(self,Roll = False):
		TimeArchives = time.time()
		
		if Roll and self.Config.GetConfig('Current','ActiveCertificate') != "Roll":
			shutil.copy("./"+self.Nom+"/"+self.Config.GetConfig('Current','ActiveCertificate')+".key", "./"+self.Nom+"/Roll.key")
			shutil.copy("./"+self.Nom+"/"+self.Config.GetConfig('Current','ActiveCertificate')+".csr", "./"+self.Nom+"/Roll.csr")
			self.Config.SetConfig('ActiveCertificate',"Roll") 
			self.Config.SetConfig('EndRoll',time.time()+5184000)
			AppelACME()
			#Generation Certbot Roll
		######################################	
			
		if os.path.exists("./"+self.Nom+"/Main.key") or os.path.exists("./"+self.Nom+"/Backup1.key") or os.path.exists("./"+self.Nom+"/Backup2.key"):
			shutil.move("./"+self.Nom+"/Main.key", "./"+self.Nom+"/Archive/"+TimeArchives+"/Main.key")
			shutil.move("./"+self.Nom+"/Backup1.key", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup1.key")
			shutil.move("./"+self.Nom+"/Backup2.key", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup2.key")

		if self.Config.GetConfig('Config','LevelCertificate') == "Haut":
			os.system("openssl ecparam -genkey -name secp384r1 > ./"+self.Nom+"/Main.key")
			os.system("openssl ecparam -genkey -name secp384r1 > ./"+self.Nom+"/Backup1.key")
			os.system("openssl genrsa -out ./"+self.Nom+"/Backup2.key 4096")
		elif self.Config.GetConfig('Config','LevelCertificate') == "Moyen":
			os.system("openssl genrsa -out ./"+self.Nom+"/Main.key 4096")
			os.system("openssl genrsa -out ./"+self.Nom+"/Backup1.key 4096")
			os.system("openssl genrsa -out ./"+self.Nom+"/Backup2.key 2048")
		elif self.Config.GetConfig('Config','LevelCertificate') == "Bas":
			os.system("openssl genrsa -out ./"+self.Nom+"/Main.key 2048")
			os.system("openssl genrsa -out ./"+self.Nom+"/Backup1.key 2048")
			os.system("openssl genrsa -out ./"+self.Nom+"/Backup2.key 2048")
		self.Config.SetConfig('ActiveCertificate',self.Config.GetConfig('Current', 'ActiveCertificate', 'Main'))
		#self.Config.GetConfig('ActiveCertificate'] = (settingsConfig['Current')).get('ActiveCertificate', "Main")# le certificat actif le principale ou une backup
		self.Config.SetConfig('LastRenew',TimeArchives)
		###############################################
		'''Demande de certificat csr'''
		if os.path.exists("./"+self.Nom+"/Main.csr") or os.path.exists("./"+self.Nom+"/Backup1.csr") or os.path.exists("./"+self.Nom+"/Backup2.csr"):
			shutil.move("./"+self.Nom+"/Main.csr", "./"+self.Nom+"/Archive/"+TimeArchives+"/Main.csr")
			shutil.move("./"+self.Nom+"/Backup1.csr", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup1.csr")
			shutil.move("./"+self.Nom+"/Backup2.csr", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup2.csr")

		os.system("openssl req -new -sha384 -key ./"+self.Nom+"/Main.key -nodes -out ./"+self.Nom+"/Main.csr -outform pem -config ./"+self.Nom+"/"+self.Nom+".cnf")
		os.system("openssl req -new -sha384 -key ./"+self.Nom+"/Backup1.key -nodes -out ./"+self.Nom+"/Backup1.csr -outform pem -config ./"+self.Nom+"/"+self.Nom+".cnf")
		os.system("openssl req -new -sha384 -key ./"+self.Nom+"/Backup2.key -nodes -out ./"+self.Nom+"/Backup2.csr -outform pem -config ./"+self.Nom+"/"+self.Nom+".cnf")
		AppelACME()
		#Generation Certbot self.Config.GetConfig('ActiveCertificate')
	def UpdateGlobal(self):
		if float(self.Config.GetConfig('Current','EndRoll')) < time.time():#Fin du roll
			self.Config.SetConfig('ActiveCertificate',"Main")
			self.Config.SetConfig('LastRenew',TimeArchives)
			self.Config.SetConfig('EndRoll',0)
			AppelACME()
			#Requete du certbot Roll
		elif self.Config.GetConfig('Current','EndRoll') == "0":
			if time.time() >= int(self.Config.GetConfig('Current','LastRenew'))+int(self.Config.GetConfig('Current','TimeRenew')):# temps pour le renuvellement depasser
				AppelACME()
				#Requete pour renouvellement crt
	def AppelACME(self):
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
		self.Config.SetConfig('IntermediaireChain',ChainEqual)
	def UpdateZone(self):
		settingscnf = configparser.ConfigParser()
		settingscnf.optionxform = str
		settingscnf.read('./'+self.Nom+'/'+self.Nom+'.cnf')
		
		DemiZoneFile = open("./"+self.Nom+"/HalfZone.conf",'w+')
		proc = subprocess.Popen(['openssl x509 -noout -pubkey -in ./'+self.Nom+'/Main.crt  | openssl rsa -pubin -outform DER 2>/dev/null | sha256 | tr "a-z" "A-Z"'],stdout=PIPE,stdin=PIPE,shell=True)
		hash = proc.stdout.read().split().at(1)
		
		ListDomains = self.Config.GetListDomains()
		for domain in ListDomains:
			if self.Config.GetConfig('Config','DNSCAActivate') == "true":
				#############CAA#################
				DemiZoneFile.write(domain+".	IN	CAA	0 issue \"letsencrypt.org\"")
				DemiZoneFile.write(domain+".	IN	CAA	0 iodef \"mailto:"+mail+"\"")
			if self.Config.GetConfig('Config','TLSAActivate') == "true":
				###############TLSA###############
				DemiZoneFile.write("_443._tcp."+domain+".	IN TLSA 3 1 1 "+hash)
			

	def UpdateConfApache(self):
		ApacheInFile = open("./"+self.Nom+"/ApacheIn.conf",'w+')#in virtualhost
		ApacheOutFile = open("./"+self.Nom+"/ApacheOut.conf",'w+')#out virtualhost
		
		ApacheInFile.write("SSLCertificateFile /etc/letsencrypt/live/loasisdeschatsbleus.fr/fullchain.pem\n\
		SSLCertificateKeyFile /etc/letsencrypt/live/loasisdeschatsbleus.fr/privkey.pem")
	def ActivationBackup(self):
		if self.Config.GetConfig('Current','ActiveCertificate') != "Roll":
			d.infobox("Vous êtes actuellement en Roll à cause de HPKP\n\
			Le programme refuse de faire automatiquement, si vous insistez faite le manuellement.")
		else:
			d.infobox("L'activation du backup revokera automatiquement les certificat précédent\n NB: il régènerera pas les clé automatiquement")
			code, tag = d.menu("Le certificat activé actuel est le "+self.Config.GetConfig('Current','ActiveCertificate')+". Lequel voulez-vous activer?",
			choices=[('Main', 'Le certificat principale'),('Backup1', 'Backup online'),('Backup2', 'Backup offline')], title="Security")
			if code == Dialog.OK:
				if tag == self.Config.GetConfig('Current','ActiveCertificate'):
					d.infobox("Bravo le génie, on sent que tu as eu ton bac avec mention...")
				else:
					self.Config.setConfig('ActiveCertificate',tag)
					AppelACME()
	def PrintInclusion(self):
		print()
	def MainMenu(self):
		code, tag = d.menu("Que voulez vous faire?",
			choices=[('1', 'Modifier les informations du certificat'),('2', 'Modifier la configuration'),('3', 'Regénerer les clé privé'),('4', 'Regénerer les certificats'),('5', 'Activer une backup'),('6', 'Afficher les lignes d\'inclusion')], title="Security")
		if code == Dialog.CANCEL:
			Accueil()
		else:
			if tag == "1":
				self.Config.DemanderCnf()
			elif tag == "2":
				self.Config.ModificationConfig()
			elif tag == "3":
				if self.Config.GetConfig('Config','HPKPActivate') == "true":
					self.CreationKeyAndCsr(True)
				else:
					self.CreationKeyAndCsr()
			elif tag == "4":
				self.AppelACME()
			elif tag == "5":
				self.ActivationBackup()
			elif tag == "6":
				self.PrintInclusion()
		

def OuvertureConfig(NameConfigtmp=""):
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
					NameConfig = ConfigurationWebSite(elem[1])
	else:
		NameConfig = ConfigurationWebSite(NameConfigtmp)
		
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
		NameConfig.DemanderCnf()

ConfigGeneral = ConfigurationGeneral()

if len(sys.argv) >= 2:
	OuvertureConfig(sys.argv[1])
else:
	Accueil()
#VerificationConfig()

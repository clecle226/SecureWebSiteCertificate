#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, locale, shutil
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
DEBUG = True #Staging
AUTHENTIFICATEUR = "apache"

class ConfigurationGeneral:
	def __init__(self):
		if not os.path.exists('./Certbot/Preload.ini'):
			self.mail = '';
			self.ModificationConfigGeneral()
		self.ReadAll()
	def ReadAll(self):
		settingsglobal = configparser.ConfigParser()
		settingsglobal.optionxform = str
		settingsglobal.read('./Certbot/Preload.ini')
		settingsglobalfile = open("./Certbot/Preload.ini",'r')
		self.mail = settingsglobal['DEFAULT']['email']
	def ModificationConfigGeneral(self):
		Code, info = d.form("Indiquez les informations pour le fonctionnement du programme", elements=[('Mail', 1, 2, self.mail, 1, 40, 18, 30)])
		if info[0] == '' or Code == Dialog.CANCEL:
			sys.exit(0)
		self.mail = info[0]
		command = "./Certbot/certbot-auto register --email "+self.mail+" --work-dir ./Certbot/Worker/ --logs-dir ./Certbot/Log/ --config-dir ./Certbot/Config/"
		if not os.path.exists("./Certbot/certbot-auto"):
			os.makedirs("./Certbot/")
			os.makedirs("./ChainACME/")
			exe = urllib.request.urlopen("https://dl.eff.org/certbot-auto")
			with open("./Certbot/certbot-auto","wb+") as f:
				f.write(exe.read())
				os.system("chmod a+x ./Certbot/certbot-auto")
		else:
			command = command+" --update-registration"
		if DEBUG == True:
			command = command+" --staging"
		os.system(command)

		
		

class ConfigurationWebSite:
	def __init__(self, name):
		settingsglobal = configparser.ConfigParser()
		settingsglobal.optionxform = str
		settingsglobal.read('./Certbot/Preload.ini')
		settingsglobalfile = open("./Certbot/Preload.ini",'r')
		self.mail = settingsglobal['DEFAULT']['email']
		#########################################
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

		self.NomConfig = self.settingsConfig['Config']['Name']
		self.AppConfig = ApplicationConfiguration(self)
		self.VerificationConfig()
		self.AppConfig.MainMenu()
		
	def GetConfig(self,Section,Name,FallBack=''):
		if Section == "General" and Name == "mail":
			return self.mail
		return (self.settingsConfig[Section]).get(Name, FallBack)
	def SetConfig(self,Name,Valeur):
		self.settingsConfig['Current'][Name] = str(Valeur)
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
								self.AppConfig.CreationKey(True)
							elif tag == "2":
								self.AppConfig.ActivationBackup()
								self.AppConfig.CreationKey(True)
					else:
						self.AppConfig.CreationKey()
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
					d.msgbox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
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
					d.msgbox("Ouai tu as raison...  je préfère ça... Merci pour l'internet...")
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
			self.DemanderCnf()
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
		if not self.settingsConfig.has_section('InfoCertificate'):
			self.settingsConfig.add_section('InfoCertificate')
			self.settingsConfig['InfoCertificate']['countryName'] = 'FR'
			self.settingsConfig['InfoCertificate']['stateOrProvinceName'] = 'France'
			self.settingsConfig['InfoCertificate']['localityName'] = 'Paris'
			self.settingsConfig['InfoCertificate']['organizationName'] = 'Eradicate GAFA'
			self.settingsConfig['InfoCertificate']['domaine'] = ''#commonName

		Code, domains = d.inputbox("Ajouter un ou plusieurs nom de domaines pour ce certificat, séparé par des ;",init=self.settingsConfig['InfoCertificate']['domaine'])
		
		
		distinguished_name=[('Country Name (2 letter code)', 1, 2, self.settingsConfig['InfoCertificate']['countryName'], 1, 40, 2, 2),\
		('State or Province Name (full name)', 2, 2, self.settingsConfig['InfoCertificate']['stateOrProvinceName'], 2, 40, 18, 30),\
		('Locality Name (eg, city)', 3, 2, self.settingsConfig['InfoCertificate']['localityName'], 3, 40, 18, 30),\
		('Organization Name (eg, company)', 4, 2, self.settingsConfig['InfoCertificate']['organizationName'], 4, 40, 18, 30)]

		Code, info = d.form("Indiquez les informations du certificat", elements=distinguished_name)
		
		self.settingsConfig['InfoCertificate']['countryName'] = info[0]
		self.settingsConfig['InfoCertificate']['stateOrProvinceName'] = info[1]
		self.settingsConfig['InfoCertificate']['localityName'] = info[2]
		self.settingsConfig['InfoCertificate']['organizationName'] = info[3]
		self.settingsConfig['InfoCertificate']['domaine'] = domains
		self.UpdateConfig()
	
	def CreationCNFTemp(self):
		shutil.copy("/etc/ssl/openssl.cnf", "./"+self.NomConfig+"/"+self.NomConfig+".cnf")
		
		settingscnf = configparser.ConfigParser()
		settingscnf.optionxform = str
		fichier = open('./'+self.NomConfig+'/'+self.NomConfig+'.cnf' , 'r')
		settingscnf.read_string("[DEFAULT]\n"+fichier.read())
		domains = (self.settingsConfig['InfoCertificate']['domaine']).split(';')

		if len(domains) > 1:
			settingscnf[' req ']['req_extensions'] = "v3_req"
			settingscnf[' v3_req ']['subjectAltName'] = "@alt_names"
			settingscnf.add_section(' alt_names ')
			i = 1
			for elem in domains:
				settingscnf[' alt_names ']['DNS.'+str(i)] = elem
				i = i+1

		fichier.close()
		fichier = open('./'+self.NomConfig+'/'+self.NomConfig+'.cnf' , 'w+')
		settingscnf.write(fichier)
		fichier.close()
	
	def GetSubj(self):
		domains = (self.settingsConfig['InfoCertificate']['domaine']).split(';')
		subj = "'/C="+self.settingsConfig['InfoCertificate']['countryName']+"/ST="+self.settingsConfig['InfoCertificate']['stateOrProvinceName']+"/L="+self.settingsConfig['InfoCertificate']['localityName']+"/O="+self.settingsConfig['InfoCertificate']['organizationName']+"/OU=null/CN="+domains[0]
		
		subj = subj+"'"
		return subj
		
	def CronUpdate(self):
		self.AppConfig.UpdateGlobal()
		
class ApplicationConfiguration:
	def __init__(self, Config):
		self.Config = Config
		self.Nom = self.Config.GetConfig("Config","Name")
	
	def ActivationRoll(self, DemandeRoll = "Backup1"):
		TimeArchives = str(int(time.time()))
		
		os.system("rm ./"+self.Nom+"/Roll.*")
		shutil.copy("./"+self.Nom+"/"+self.Config.GetConfig('Current','ActiveCertificate')+".key", "./"+self.Nom+"/Roll.key")
		self.Config.SetConfig('ActiveCertificate',"Roll")
		self.Config.SetConfig('ActualBackupActivate', DemandeRoll) 
		self.Config.SetConfig('EndRoll',time.time()+5184000)
		if DemandeRoll == "Backup1":
			CreationKey(Main = True, Backup1 = False, Backup2 = False)
		if DemandeRoll == "Backup2":
			CreationKey(Main = True, Backup1 = True, Backup2 = False)
		self.UpdateConfApache()#Avec HPKP, génération nouvelle clé

			
	def CreationKey(self,Main = True, Backup1 = True, Backup2 = True):
		TimeArchives = str(int(time.time()))
		
		######################################	
			####Deplacement old file#########
		if os.path.exists("./"+self.Nom+"/Main.key") or os.path.exists("./"+self.Nom+"/Backup1.key") or os.path.exists("./"+self.Nom+"/Backup2.key") or os.path.exists("./"+self.Nom+"/Main.csr") or os.path.exists("./"+self.Nom+"/Backup1.csr") or os.path.exists("./"+self.Nom+"/Backup2.csr"):
			os.makedirs("./"+self.Nom+"/Archive/"+TimeArchives+"/")
			
		if os.path.exists("./"+self.Nom+"/Main.key") and Main == True:
			shutil.move("./"+self.Nom+"/Main.key", "./"+self.Nom+"/Archive/"+TimeArchives+"/Main.key")
		if os.path.exists("./"+self.Nom+"/Backup1.key") and Backup1 == True:
			shutil.move("./"+self.Nom+"/Backup1.key", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup1.key")
		if os.path.exists("./"+self.Nom+"/Backup2.key") and Backup2 == True:
			shutil.move("./"+self.Nom+"/Backup2.key", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup2.key")
		if os.path.exists("./"+self.Nom+"/Main.csr"):
			shutil.move("./"+self.Nom+"/Main.csr", "./"+self.Nom+"/Archive/"+TimeArchives+"/Main.csr")
		if os.path.exists("./"+self.Nom+"/Backup1.csr"):
			shutil.move("./"+self.Nom+"/Backup1.csr", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup1.csr")
		if os.path.exists("./"+self.Nom+"/Backup2.csr"):
			shutil.move("./"+self.Nom+"/Backup2.csr", "./"+self.Nom+"/Archive/"+TimeArchives+"/Backup2.csr")
		################################################
		if self.Config.GetConfig('Config','LevelCertificate') == "Haut":
			if Main == True:
				os.system("openssl ecparam -genkey -name secp384r1 > ./"+self.Nom+"/Main.key")
			if Backup1 == True:
				os.system("openssl ecparam -genkey -name secp384r1 > ./"+self.Nom+"/Backup1.key")
			if Backup2 == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Backup2.key 4096")
		elif self.Config.GetConfig('Config','LevelCertificate') == "Moyen":
			if Main == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Main.key 4096")
			if Backup1 == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Backup1.key 4096")
			if Backup2 == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Backup2.key 2048")
		elif self.Config.GetConfig('Config','LevelCertificate') == "Bas":
			if Main == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Main.key 2048")
			if Backup1 == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Backup1.key 2048")
			if Backup1 == True:
				os.system("openssl genrsa -out ./"+self.Nom+"/Backup2.key 2048")
				
		self.Config.SetConfig('ActiveCertificate',self.Config.GetConfig('Current', 'ActiveCertificate', 'Main'))#si pas d'activate alors Main

		self.Config.SetConfig('LastRenew',TimeArchives)
		###############################################

		self.AppelACME()
		
	def UpdateGlobal(self):
		if float(self.Config.GetConfig('Current','EndRoll')) < time.time():#Fin du roll
			self.Config.SetConfig('ActiveCertificate',"Main")
			self.Config.SetConfig('EndRoll',0)
			if self.Config.GetConfig('Current','ActualBackupActivate') == "Backup1":
				CreationKey(Main = False, Backup1 = True, Backup2 = False)
			if self.Config.GetConfig('Current','ActualBackupActivate') == "Backup2":
				CreationKey(Main = False, Backup1 = False, Backup2 = True)
			self.UpdateConfApache()#Avec HPKP, génération nouvelle clé
			
			AppelACME()#Requete du certbot Roll
		elif float(self.Config.GetConfig('Current','EndRoll')) > time.time() and time.time() >= int(self.Config.GetConfig('Current','LastRenew'))+int(self.Config.GetConfig('Current','TimeRenew')):#Roll NonFini mais renouvellement depasser
			AppelACME()#Requete pour renouvellement crt
		elif self.Config.GetConfig('Current','ActiveCertificate') == "Main" and time.time() >= int(self.Config.GetConfig('Current','LastRenew'))+int(self.Config.GetConfig('Current','TimeRenew')):# temps pour le renuvellement depasser:
			AppelACME()#Requete pour renouvellement crt
				

	def AppelACME(self):
		CurrentKeyUse = self.Config.GetConfig('Current','ActiveCertificate')
		self.Config.SetConfig('LastRenew',TimeArchives)
		if not os.path.exists("./"+self.Nom+"/"+CurrentKeyUse+".csr"):
			self.Config.CreationCNFTemp()
			os.system("openssl req -new -sha384 -key ./"+self.Nom+"/"+CurrentKeyUse+".key -nodes -out ./"+self.Nom+"/"+CurrentKeyUse+".csr -outform pem -subj "+self.Config.GetSubj()+" -config ./"+self.Nom+"/"+self.Nom+".cnf")
			os.system("sudo rm ./"+self.Nom+"/"+self.Nom+".cnf")
		
		TimeArchives = str(int(time.time()))
		if os.path.exists("./"+self.Nom+"/"+CurrentKeyUse+"_fullchain.pem") or os.path.exists("./"+self.Nom+"/"+CurrentKeyUse+"_crt.pem"):
			os.makedirs("./"+self.Nom+"/Archive/CRT"+TimeArchives+"/")
			shutil.move("./"+self.Nom+"/"+CurrentKeyUse+"_fullchain.pem", "./"+self.Nom+"/Archive/CRT"+TimeArchives+"/"+CurrentKeyUse+"_fullchain.pem")
			shutil.move("./"+self.Nom+"/"+CurrentKeyUse+"_crt.pem", "./"+self.Nom+"/Archive/CRT"+TimeArchives+"/"+CurrentKeyUse+"_crt.pem")
			os.system("sudo rm ./"+self.Nom+"/Actual_FC.pem")
			os.system("sudo rm ./"+self.Nom+"/Actual_key.pem")
		
		command = "sudo ./Certbot/certbot-auto certonly -a "+AUTHENTIFICATEUR+" --csr ./"+self.Nom+"/"+CurrentKeyUse+".csr --cert-path ./"+self.Nom+"/"+CurrentKeyUse+"_crt.pem --fullchain-path ./"+self.Nom+"/"+CurrentKeyUse+"_fullchain.pem --chain-path ./ChainACME/Chain.pem.tmp --work-dir ./Certbot/Worker/ --logs-dir ./Certbot/Log/ --config-dir ./Certbot/Config/"
		if DEBUG == True:
			command = command+" --staging"
		os.system(command)
		
		os.system("sudo ln -s ./"+self.Nom+"/"+CurrentKeyUse+"_fullchain.pem ./"+self.Nom+"/Actual_FC.pem")
		os.system("sudo ln -s ./"+self.Nom+"/"+CurrentKeyUse+".key ./"+self.Nom+"/Actual_key.pem")
		
		# Verifier correspondance Chain Intermediaire
		listChain = os.listdir('./ChainACME/')
		ChainTmpFile = open("./ChainACME/Chain.pem.tmp",'rb')
		tmpdigest = hashlib.sha224(ChainTmpFile.read()).hexdigest()
		ChainEqual = ""
		for elem in listChain:
			ChainFile = open("./ChainACME/"+elem,'rb')
			digestTest = hashlib.sha224(ChainFile.read()).hexdigest()
			if digestTest == tmpdigest and elem != "Chain.pem.tmp":
				ChainEqual = elem
		if ChainEqual == "":
			shutil.move("./ChainACME/Chain.pem.tmp", "./ChainACME/Chain_"+str(len(listChain))+".pem")
			ChainEqual = "Chain_"+str(len(listChain))+".pem"
		else:
			os.system("sudo rm ./ChainACME/Chain.pem.tmp")
		self.Config.SetConfig('IntermediaireChain',ChainEqual)
	def UpdateZone(self):
		settingscnf = configparser.ConfigParser()
		settingscnf.optionxform = str
		settingscnf.read('./'+self.Nom+'/'+self.Nom+'.cnf')
		
		DemiZoneFile = open("./"+self.Nom+"/HalfZone.conf",'w+')
		#proc = subprocess.Popen(['openssl x509 -noout -pubkey -in ./'+self.Nom+'/'+self.Config.GetConfig('Current','ActiveCertificate')+'_crt.pem  | openssl rsa -pubin -outform DER 2>/dev/null | openssl sha256 | tr "a-z" "A-Z"'],stdout=subprocess.PIPE,stdin=subprocess.PIPE,shell=True)
		#hash = str(proc.stdout.read()).split(" ")
		#hash = (hash[1]).replace("\\n'", "")
		#print(hash)
		#Don't work#########################################################
		
		ListDomains = self.Config.GetConfig('InfoCertificate','domaine').split(';')
		for domain in ListDomains:
			if self.Config.GetConfig('Config','DNSCAActivate') == "true":
				#############CAA#################
				DemiZoneFile.write(domain+".	IN	CAA	0 issue \"letsencrypt.org\"\n")
				DemiZoneFile.write(domain+".	IN	CAA	0 iodef \"mailto:"+self.Config.GetConfig('General','mail')+"\"\n")
			#if self.Config.GetConfig('Config','TLSAActivate') == "true":
				###############TLSA###############
				#DemiZoneFile.write("_443._tcp."+domain+".	IN TLSA 3 1 1 "+hash+"\n")
			
	def UpdateConfApache(self):
		ApacheInFile = open("./"+self.Nom+"/Apache.conf",'w+')#in virtualhost
		AppDir = os.getcwd()
		
		ApacheInFile.write("SSLCertificateFile "+AppDir+"/"+self.Nom+"/Actual_FC.pem\nSSLCertificateKeyFile "+AppDir+"/"+self.Nom+"/Actual_key.pem\n")
		if self.Config.GetConfig('Config','LevelApache') == "Haut":
			ApacheInFile.write("Include "+AppDir+"/Apache/ApacheHaut.conf\n")
		elif self.Config.GetConfig('Config','LevelApache') == "Moyen":
			ApacheInFile.write("Include "+AppDir+"/Apache/ApacheMoyen.conf\n")
		elif self.Config.GetConfig('Config','LevelApache') == "Bas":
			ApacheInFile.write("Include "+AppDir+"/Apache/ApacheBas.conf\n")

		if self.Config.GetConfig('Config','OCSPStaplingActivate') == "true":
			ApacheInFile.write("Include "+AppDir+"/Apache/OCSP.conf\n")
		if self.Config.GetConfig('Config','HSTSActivate') == "true":
			ApacheInFile.write('Header always set Strict-Transport-Security "max-age=15768000; includeSubDomains; preload"\n')
		if self.Config.GetConfig('Config','HPKPActivate') == "true":
			ApacheInFile.write(self.CalculHPKP())
			
	def CalculHPKP(self):
		if self.Config.GetConfig('Config','LevelCertificate') == "Haut":
			MainHash = (os.popen("openssl ec -in ./"+self.Nom+"/Main.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
			Backup1Hash = (os.popen("openssl ec -in ./"+self.Nom+"/Backup1.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
			Backup2Hash = (os.popen("openssl rsa -in ./"+self.Nom+"/Backup2.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
		elif self.Config.GetConfig('Config','LevelCertificate') == "Moyen":
			MainHash = (os.popen("openssl rsa -in ./"+self.Nom+"/Main.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
			Backup1Hash = (os.popen("openssl rsa -in ./"+self.Nom+"/Backup1.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
			Backup2Hash = (os.popen("openssl rsa -in ./"+self.Nom+"/Backup2.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
		elif self.Config.GetConfig('Config','LevelCertificate') == "Bas":
			MainHash = (os.popen("openssl rsa -in ./"+self.Nom+"/Main.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
			Backup1Hash = (os.popen("openssl rsa -in ./"+self.Nom+"/Backup1.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
			Backup2Hash = (os.popen("openssl rsa -in ./"+self.Nom+"/Backup2.key -outform der -pubout | openssl dgst -sha256 -binary | openssl enc -base64").read()).strip("\n")
		return 'Header always set Public-Key-Pins "pin-sha256=\\"'+MainHash+'\\"; pin-sha256=\\"'+Backup1Hash+'\\"; pin-sha256=\\"'+Backup2Hash+'\\"; max-age=5184000; includeSubDomains"'
		
	def ActivationBackup(self):
		if self.Config.GetConfig('Current','ActiveCertificate') == "Roll" and self.Config.GetConfig('Current','ActualBackupActivate') == "Backup2":
			d.msgbox("Vous êtes actuellement en roll Backup2 pour HPKP\n\
Le programme refuse de faire automatiquement, si vous insistez faite le manuellement.\n\
Si vous le faites sachez que vous risqué de casser les services géré par ce projet.")
		else:
			d.msgbox("L'activation du backup revokera automatiquement les certificat précédent\n NB: il régènerera pas les clé automatiquement")
			if self.Config.GetConfig('Current','ActiveCertificate') == "Main":
				menuchoices =[('Backup1', 'Backup online'),('Backup2', 'Backup offline')]
			elif self.Config.GetConfig('Current','ActualBackupActivate') == "Backup1":
				menuchoices =[('Backup2', 'Backup offline')]
			code, tag = d.menu("Le certificat activé actuel est le "+self.Config.GetConfig('Current','ActiveCertificate')+". Lequel voulez-vous activer?",
			choices=menuchoices, title="Security")
			if code == Dialog.OK:
				if tag == "Backup2":
					retour = d.yesno("Attention!!! Ceci est la dernière backup valide... Si vous activer cette backup vous devrez attendre la fin du roll avant toutes modification des clé HPKP\nÊtes-vous de votre action?")
					if retour == "no":
						return ""
					retour = d.yesno("Cette action va recréer les key de Main et/ou Backup1 après le lancement du Roll et changer en consequence HPKP.\nSi vous voulez utiliser Backup2 merci de la mettre à l'adresse ./"+self.Nom+"/Backup2.key\n Voulez-vous continuer?")
					if retour == "yes":
						ActivationRoll(tag)
					else:
						return ""
	def PrintInclusion(self):
		self.CalculHPKP()
		self.UpdateConfApache()
		Msg = "Apache config file(in virtualhost):\n Include ./"+self.Nom+"/Apache.conf\n"
		if self.Config.GetConfig('Config','DNSCAActivate') == "true" or self.Config.GetConfig('Config','TLSAActivate') == "true":
			self.UpdateZone()
			Msg = Msg+"Bind(DNS server) config file:\n Include ./"+self.Nom+"/HalfZone.conf\n"
		d.msgbox(Msg)

	def MainMenu(self):
		if not os.path.exists("./"+self.Nom+"/"+self.Config.GetConfig('Current','ActiveCertificate')+"_fullchain.pem") or not os.path.exists("./"+self.Nom+"/"+self.Config.GetConfig('Current','ActiveCertificate')+"_crt.pem"):
			self.CreationKey()
			self.PrintInclusion()
		code = 1
		while code != Dialog.CANCEL:
			code, tag = d.menu("Que voulez vous faire?",
				choices=[('1', 'Modifier les informations du certificat'),('2', 'Modifier la configuration'),('3', 'Regénerer les clé privé'),('4', 'Regénerer les certificats'),('5', 'Activer une backup'),('6', 'Afficher les lignes d\'inclusion')], title="Security")
			if tag == "1":
				self.Config.DemanderCnf()
			elif tag == "2":
				self.Config.ModificationConfig()
			elif tag == "3":
				if self.Config.GetConfig('Config','HPKPActivate') == "true" and self.Config.GetConfig('Current', 'EndRoll', 'null') != 'null':
					self.CreationKey(True)
				else:
					self.CreationKey()
			elif tag == "4":
				self.AppelACME()
			elif tag == "5":
				self.ActivationBackup()
			elif tag == "6":
				self.PrintInclusion()
		Accueil()
		

def OuvertureConfig(NameConfigtmp=""):
	global NameConfig
	
	if NameConfigtmp == "":
		listConfigAvailable = os.listdir('./');
		i = 0
		listFinal = []
		for elem in listConfigAvailable:
			if '.cfg' in elem and elem != 'global.cfg':
				i = i+1
				listFinal.append((str(i), elem))
				
		code, tag = d.menu("Quel configuration modifier?",
					   choices=listFinal, title="Choix Config")
		if code != Dialog.CANCEL and tag != '':
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
			d.msgbox("Ouai tu as raison...  je préfère ça... Merci pour la securite sur internet...")
			return DemandeBinaire(Msg)
		else:
			return "false"
	else:
		return "true"

def Accueil():
	global NameConfig
	code = 1
	while code != Dialog.CANCEL:
		code, tag = d.menu("Que voulez vous faire?",
			choices=[('1', 'Nouveau'),('2', 'Ouvrir')], title="Security")

		if tag == "1":
			code, NameFile = d.inputbox("Choisir un nom de projet:")
			if code == Dialog.OK:
				OuvertureConfig(NameFile+".cfg")
		elif tag == "2":
			OuvertureConfig()
	sys.exit(0)

ConfigGeneral = ConfigurationGeneral()

if len(sys.argv) == 2:
	if sys.argv[1] == "--debug":
		OuvertureConfig("Test.cfg")
		#NameConfig.AppConfig.CalculHPKP()
	else:
		OuvertureConfig(sys.argv[1])
elif len(sys.argv) >= 3:
	if sys.argv[1] == "--cron":
		if sys.argv[2] == "all":
			listConfigAvailable = os.listdir('./');
			for elem in listConfigAvailable:
				if '.cfg' in elem and elem != 'global.cfg':
					OuvertureConfig(elem)
					NameConfig.CronUpdate()
			else:
				OuvertureConfig(sys.argv[2])
				NameConfig.CronUpdate()
else:
	Accueil()

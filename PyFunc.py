import time
import re
import os
import sys
import mysql.connector
import socket
import struct
import subprocess
from xml.dom import minidom
import xml.etree.ElementTree

#Define regex
# regIP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
# regMAC = re.compile('[a-fA-F0-9]{1,2}\-[a-fA-F0-9]{2}\-[a-fA-F0-9]{2}\-[a-fA-F0-9]{2}\-[a-fA-F0-9]{2}\-[a-fA-F0-9]{2}')
regMAC = re.compile('([a-fA-F0-9]{1,2}[:|\-| ]){5}([a-fA-F0-9]{1,2})', re.IGNORECASE)
regIP = re.compile('(\d{1,3}[.]){3}(\d{1,3})')
regSubnet = re.compile('255\.\d{1,3}\.\d{1,3}\.\d{1,3}')
regIPOID = re.compile('((\.\d{1,3})+)')
regUserName = re.compile('([a-f0-9]{1,255}[\])([a-f0-9]{1,255})', re.IGNORECASE)

#Function to create a SQL Connection
def sql_connection(userid, password):
    #Pull the Logon info for SQL
    #"with" opens reads and cloes DocScan.xml
    with open("DocScan.xml") as doc_scan:
        #Open the XML document in the minidom parser
        xml_docscan = minidom.parse(doc_scan)
        #Search for the Community Element, take the first Child Node and
        # convert to XML then strip the extra white spaces
        sql_userid = xml_docscan.getElementsByTagName(userid)\
                     [0].childNodes[0].toxml().strip()
        sql_password = xml_docscan.getElementsByTagName(password)\
                       [0].childNodes[0].toxml().strip()
    #MSSQL Connection String
    #sql_connection = pyodbc.connect('DRIVER={SQL Server}; SERVER=ECCO-SQL;\
                    # DATABASE=Workstation; UID=UserName; PWD=Password')
    #MySQL Connection String
    sql_connection = mysql.connector.Connect(host="localhost"\
                     , user=sql_userid, password=sql_password\
                     , database="Monitoring")
    #Clear variables		
    del(sql_userid)
    del(sql_password)
    return sql_connection
	
#Function to determine script run time
def python_run_time(end_time):
    #Check if script took longer than 60 seconds to process
    if (time.mktime(end_time) - time.mktime(start_time)) > 60:
        #Set the time and the measurement to minutes
        time_frame = (time.mktime(end_time) - \
                        time.mktime(start_time))/ 60
        time_measurement = ' minutes'
    else:
        #Set the time and the measurement to seconds
        time_frame = time.mktime(end_time) - time.mktime(start_time)
        time_mesurement = ' seconds'
    return "Script completed in " + str(round(time_frame,1)) + \
            time_measurement
	
#Function to determine if a device is online using Ping
def verify_online_ping(ip_fqdn):
    nmap_command = ("sudo nmap %s -sP -n" % ip_fqdn)
    nmap_ip_test = subprocess.Popen(nmap_command, stdin=None, stdout=-1, 
                                    stderr=-1, shell=True)
    while True:
        read_line = nmap_ip_test.stdout.readline()
        if not read_line: break
        if "Nmap done:" in read_line:
            if "1 host up" in read_line:
                return "Success"
            else:
                return "Fail"
		
#Function to pull the Default Gateway from IPConfig, and run MAC scan using SNMP against the DG
def defaultgateway_snmp_mac_pull():
	#Define a dictionary of IP's to MAC Addresses
	dictIPMAC = {}
	#Pull DG IP Address for the MAC pull from the Router
	strDG = funcDefaultGateway()
	#Pull a list of MAC Address from the DG and dump into a Dictionary
	#objSNMP = os.popen('snmpwalk -v 2c -c %s %s 1.3.6.1.2.1.3.1.1.2', 'r') %(snmp_community, strDG)
	objSNMP = os.popen('snmpwalk -v 2c -c %s %s .1.3.6.1.2.1.4.22.1.2' \
		%(snmp_community, strDG))
	#Loop through the objSNMP results
	while 1:
		strSNMPLine = objSNMP.readline()
		#If there are no more lines quit the while loop
		if not strSNMPLine: break
		#If the OID Line has a Hex-String then pull the IP and the MAC and assign to a dictionary
		if strSNMPLine.find('Hex-STRING:') != -1:
			#Pull the IP address from the end of the OID ".1.3.6.1.2.1.3.1.1.2.8.1.10.1.110.61"
			  #'.'join(strSNMPLine.split()[0].split('.')[len(strSNMPLine.split()[0].split('.'))-4:])
			#Pull the MAC address of the OID line ".1.3.6.1.2.1.3.1.1.2.16.1.10.1.253.4 = Hex-STRING: 00 50 56 7C A2 AA"
			  #strSNMPLine[regMAC.search(strSNMPLine).start():regMAC.search(strSNMPLine).end()].replace(' ', '-')
			#Assign the MAC address to a dictionary where the IP address is the key
			dictIPMAC['.'.join(strSNMPLine.split()[0].split('.')[len(strSNMPLine.split()[0].split('.'))-4:])] = strSNMPLine[regMAC.search(strSNMPLine).start():regMAC.search(strSNMPLine).end()].replace(' ', '-')
	#Close the SNMP object
	objSNMP.close
	#Clear variables used
	del(strSNMPLine)
	del(strDG)
	return dictIPMAC
		
#Function to parse variables by a single split
def funcVariableParse(strVariable, strSplitBy):
	#Take the variable, split it by strSplitBy then remove all Quotations (' ") and extra spaces
	strSplitVar = strVariable.split(strSplitBy)[1].replace('"', '').replace("'", '').strip()
	#Clear variables used
	del(strVariable)
	del(strSplitBy)
	return strSplitVar
	
#Function t oget the Default Gateway
def funcDefaultGateway():
	#Check to see if the system is Linux
	if sys.platform == 'linux2':
		#Run the route command like a file
		#The with open() opens the "file" and closes the "file" when the routine is done
		with open("/proc/net/route") as arrSocketRoute:
			#Loop through the open "file"
			for lpSocketRoute in arrSocketRoute:
				#Strip leading and trailing space, then split into a list by SPACE
				arrRoute = lpSocketRoute.strip().split()
				#Pull the IP that is just the active default gateway
				if arrRoute[1] != '00000000' or not int(arrRoute[3], 16) & 2:
					#Continue to the endian translation exiting the if statement
					continue
				#Translate the endian results back to an IP Address
				strDGIP = socket.inet_ntoa(struct.pack("<L", int(arrRoute[2], 16)))
				#Clear variables used
				del(arrRoute)
	#Check to see if the system is Windows
	elif sys.platform == 'win32':
		objIPConfigDG = os.popen('ipconfig /all | find "Default Gateway"', 'r')
		#Loop through the objIPConfigDG results
		while 1:
			strIPConfigDG = objIPConfigDG.readline()
			#If there are no more lines quit the while loop
			if not strIPConfigDG: break
			#Assign the IP address by using a regex to find the beginning of the iP and the end of the IP
			strDGIP = strIPConfigDG[regIP.search(strIPConfigDG).start():regIP.search(strIPConfigDG).end()]
		#Close the IPConfig object
		objIPConfigDG.close
		#Clear variables used
		del(strIPConfigDG)
	return strDGIP
		
#Function to pull the Community String by reading the 
#DocScan.XML file located in the same directory
def funcSNMPCommunity():
	#"with" opens reads and cloes DocScan.xml
	with open("DocScan.xml") as arrDocScan:
		#Open the XML document in the minidom parser
		objXMLDocScan = minidom.parse(arrDocScan)
		#Search for the Community Element, take the 
		#first Child Node and convert to XML
		snmp_community = (
				objXMLDocScan
				.getElementsByTagName('Community')[0]
			.childNodes[0].toxml().strip()
		)
	#Clear variables		
	del(arrDocScan)
	return snmp_community
				
#Function to pull the network segments from 
#DocScan.xml
def funcNetworkSeg():
	#Create an empty array for use in multiple networks
	network_segments = []
	#"with" opens reads and cloes DocScan.xml
	with open("DocScan.xml") as arrDocScan:
		#Open the XML document in the minidom parser
		objXMLDocScan = minidom.parse(arrDocScan)
		#Loop through the VLAN Elements
		for lpVLANXML in objXMLDocScan.getElementsByTagName('VLAN'):
			#Convert, strip whitespace and the childNodes from
			#getElementsByTagName and append to the array
			network_segments.append(lpVLANXML.childNodes[0].toxml().strip())
	#Clear variables
	del(arrDocScan)
	#Return all of the Network Segments from DocScan.xml
	return network_segments
			
#Function to pull UserName and Password with Admin rights
def funcUserPass():
	#Create an empty array for UserName and Password
	arrUserPass = []	
	#"with" opens reads and cloes DocScan.xml
	with open("DocScan.xml") as arrDocScan:
		#Open the XML document in the minidom parser
		objXMLDocScan = minidom.parse(arrDocScan)
		#Search for the Community Element, take the first Child Node and
		# convert to XML then strip the extra white spaces
		arrUserPass.append(objXMLDocScan.getElementsByTagName('WinUserID')[0]\
			.childNodes[0].toxml().strip())
		arrUserPass.append(objXMLDocScan.getElementsByTagName('WinPassword')[0]\
			.childNodes[0].toxml().strip())
	return arrUserPass
	
def snmp_walk(retries, version, vlan, ip, oid):
	oid_vars = []
	snmp_command = (
			"snmpwalk -r %i -v %s -c %s%s %s %s" 
			%(retries, version, snmp_community, vlan, ip, oid)
	)
	snmp = subprocess.Popen(
			snmp_command, stdin=None, stdout=-1, stderr=-1, shell=True
	)
	while True:
		read_line = snmp.stdout.readline()
		if not read_line: break
		oid_vars.append(read_line.strip())
	return oid_vars
	
def snmp_get(retries, version, vlan, ip, oid):
	snmp_command = (
			"snmpget -r %i -v %s -c %s%s %s %s" 
			%(retries, version, snmp_community, vlan, ip, oid)
	)
	snmp = subprocess.Popen(
			snmp_command, stdin=None, stdout=-1, stderr=-1, shell=True
	)
	while True:
		read_line = snmp.stdout.readline()
		if not read_line: break
		return read_line
	
def snmp_oid(oid_var, oid_parse, oid_type):
	oid_var_parsed = ["", ""]
	if oid_type in oid_var:
		oid_raw = oid_var.split(oid_type)
		oids = oid_raw[0].split(".")
		oid_type_parse = oids[oid_parse:]
		oid_parsed = ".".join(oids[oid_parse:]).strip()
		var = oid_var.split(oid_type)[1].strip()
		oid_var_parsed = (oid_parsed, var)
	return oid_var_parsed
	
#class ProgressBar(object):
#	
#	def __init__(
#			self, max_value, max_part, current_part, size=80
#	):
#		self.max_value = max_value
#		self.size = size
#		self.value = 0
#		print "Part %i of %i \n" % (current_part, 
#				max_part)
#		
#	def draw(self):
#		fill_size = self.size * self.value // self.max_value
#		if fill_size > self.size -2:
#			fill_size = self.size -2
#		blank_size = self.size - fill_size - 2
#		bar = ''.join(['[', '=' * fill_size, ' ' * blank_size, ']'])
#		
#		sys.stdout.write('\b' * len(bar))
#		sys.stdout.write(bar)
#		sys.stdout.flush()
#		
#	def step(self, step_size=1):
#		self.value += step_size
#		self.draw()
#		
#	def end(self):
#		sys.stdout.write('\n\n')
#		sys.stdout.flush()
#

#Define Global Variables used
#Define Time Constants
#snmp_community = funcSNMPCommunity().encode('ascii', 'ignore')
start_time = time.localtime()
print("Script started at %s \n" % str(time.strftime(
		'%Y-%m-%d %H:%M:%S', start_time)
))

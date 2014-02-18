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
		
#Function to use the Default Gateway, and run a MAC scan using SNMP 
#against the DG
def defaultgateway_snmp_mac_pull():
    #Define a dictionary of IP's to MAC Addresses
    ip_mac = {}
    #Pull DG IP Address for the MAC pull from the Router
    default_gateway = default_gateway_pull()
    #Pull a list of MAC Address from the DG and dump into a Dictionary
    snmp = os.popen('snmpwalk -v 2c -c %s %s .1.3.6.1.2.1.4.22.1.2' \
                    %(snmp_community, default_gateway))
    #Loop through the objSNMP results
    while 1:
        snmp_line = snmp.readline()
        #If there are no more lines quit the while loop
        if not snmp_line: break
        #If the OID Line has a Hex-String then pull the IP and the MAC
        if snmp_line.find('Hex-STRING:') != -1:
            #Pull the IP address from the end of the OID 
                #".1.3.6.1.2.1.3.1.1.2.8.1.10.1.110.61"
            #'.'join(strSNMPLine.split()[0].split('.')
                #[len(strSNMPLine.split()[0].split('.'))-4:])
            #strSNMPLine[regMAC.search(strSNMPLine).start():
                #regMAC.search(strSNMPLine).end()].replace(' ', '-')
            #Assign the MAC address to a dic where the IP address is the key
            ip_mac['.'.join(snmp_line.split()[0].split('.')\
                      [len(snmp_line.split()[0].split('.'))-4:])] = \
                      snmp_line[regMAC.search(snmp_line).start():\
                      regMAC.search(snmp_line).end()].replace(' ', '-')
    #Close the SNMP object
    objSNMP.close
    #Clear variables used
    del(snmp_line)
    del(default_gateway)
    return ip_mac
		
#Function to parse variables by a single split
def variable_parse(variable, split_by):
    #Take the variable, split it by split_by then strip quotes and spaces
    split_variable = variable.split(split_by)[1].replace('"', '')\
                     .replace("'", '').strip()
    #Clear variables used
    del(split_variable)
    del(split_by)
    return split_variable
	
#Function t oget the Default Gateway
def default_gateway_pull():
    #Check to see if the system is Linux
    if sys.platform == 'linux2':
        #Run the route command like a file
        with open("/proc/net/route") as socket_routes:
            #Loop through the open "file"
            for socket_route in socket_routes:
                routes = socket_route.strip().split()
                #Pull the IP that is just the active default gateway
                if routes[1] != '00000000' or not int(routes[3], 16) & 2:
                    #Continue the endian translation exiting the if
                    continue
                    #Translate the endian results back to an IP Address
                default_gateway_ip = socket.inet_ntoa(struct.pack("<L", \
                                     int(routes[2], 16)))
                #Clear variables used
                del(routes)
    #Check to see if the system is Windows
    elif sys.platform == 'win32':
        routes = os.popen('ipconfig /all | find "Default Gateway"', 'r')
        while 1:
            routes_line = routes.readline()
            if not routes_line: break
            #Pull the IP using a regex for the beginning and end of the IP
            default_gateway_ip = routes_line[regIP.search(routes_line)\
                                 .start():regIP.search(routes_line).end()]
        #Close the IPConfig object
        routes.close
        #Clear variables used
        del(routes_line)
    return default_gateway_ip
		
#Function to pull the Community String by reading the 
#DocScan.XML file located in the same directory
def snmp_community_string():
    with open("DocScan.xml") as doc_scan:
        #Open the XML document in the minidom parser
        xml_docscan = minidom.parse(doc_scan)
        #Search for the Community Element, take the 
        #first Child Node and convert to XML
        snmp_community = xml_docscan.getElementsByTagName('Community')\
                         [0].childNodes[0].toxml().strip()
    #Clear variables		
    del(doc_scan)
    return snmp_community
				
#Function to pull the network segments from DocScan.xml 
def network_segment():
    #Create an empty array for use in multiple networks
    network_segments = []
    #"with" opens reads and cloes DocScan.xml
    with open("DocScan.xml") as doc_scan:
        #Open the XML document in the minidom parser
        xml_docscan = minidom.parse(doc_scan)
        #Loop through the VLAN Elements
        for xml_vlan in xml_docscan.getElementsByTagName('VLAN'):
            #Convert, strip whitespace and the childNodes from
            #getElementsByTagName and append to the array
            network_segments.append(xml_vlan.childNodes[0].toxml().strip())
    #Clear variables
    del(doc_scan)
    #Return all of the Network Segments from DocScan.xml
    return network_segments
			
#Function to pull UserName and Password with Admin rights
def windows_user_password():
    #Create an empty array for UserName and Password
    users_passwords = []	
    with open("DocScan.xml") as doc_scan:
        #Open the XML document in the minidom parser
        xml_docscan = minidom.parse(doc_scan)
        #Search for the Community Element, take the first Child Node and
        # convert to XML then strip the extra white spaces
        user_id.append(xml_docscan.getElementsByTagName('WinUserID')[0]\
                       .childNodes[0].toxml().strip())
        user_password.append(xml_docscan.getElementsByTagName\
                             ('WinPassword')[0].childNodes[0].toxml()\
                             .strip())
    return users_passwords
	
def snmp_walk(retries, version, vlan, ip, oid):
    oid_vars = []
    snmp_command = "snmpwalk -r %i -v %s -c %s%s %s %s"\
                    %(retries, version, snmp_community, vlan, ip, oid)
    snmp = subprocess.Popen(
            snmp_command, stdin=None, stdout=-1, stderr=-1, shell=True
    )
    while True:
        read_line = snmp.stdout.readline()
        if not read_line: break
        oid_vars.append(read_line.strip())
    return oid_vars
	
def snmp_get(retries, version, vlan, ip, oid):
    snmp_command = "snmpget -r %i -v %s -c %s%s %s %s"\
                %(retries, version, snmp_community, vlan, ip, oid)
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
	
class ProgressBar(object):
    def __init__(
            self, max_value, max_part, current_part, size=80
    ):
        self.max_value = max_value
        self.size = size
        self.value = 0
        print("Part %i of %i \n" % (current_part, max_part))
		
    def draw(self):
        fill_size = self.size * self.value // self.max_value
        if fill_size > self.size -2:
            fill_size = self.size -2
        blank_size = self.size - fill_size - 2
        bar = ''.join(['[', '=' * fill_size, ' ' * blank_size, ']'])
		
        sys.stdout.write('\b' * len(bar))
        sys.stdout.write(bar)
        sys.stdout.flush()
		
    def step(self, step_size=1):
        self.value += step_size
        self.draw()
		
    def end(self):
        sys.stdout.write('\n\n')
        sys.stdout.flush()


#Define Global Variables used
#Define Time Constants
snmp_community = snmp_community_string().encode('ascii', 'ignore')
start_time = time.localtime()
print("Script started at %s \n" % str(time.strftime(
		'%Y-%m-%d %H:%M:%S', start_time)
))

#!/usr/local/bin/python
import array
import nmap
from PyFunc import *

#Call function to create a SQL Connection
sql_connection = funcSQLConnect()
sql_cursor = sql_connection.cursor()

#Global variables are pulled from PyFunc.py

#Define Constants
script_name = sys.argv[0]
fqdns_ips = {}
nmap_ips_no_fqdns = {}
max_part = 4
current_part = 1
nm = nmap.PortScanner()

#Pull the network segments for DocScan.xml
network_segments = funcNetworkSeg()

#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(network_segments), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

nmap_ips = []
for network_segment in network_segments:
	progress_bar.step()
		
	nm.scan(hosts=network_segment, arguments='-sP')
	for host in nm.all_hosts():
		if nm[host].hostname():
			fqdns_ips[host] = nm[host].hostname()
		else:
			nmap_ips_no_fqdns[host] = ""
progress_bar.end()

progress_bar = ProgressBar(
		len(nmap_ips_no_fqdns), max_part, current_part
)		
current_part = current_part + 1
progress_bar.draw()

sql_already_scanned_ip = sql_cursor.execute(
			"SELECT IPAddress FROM tblDocIP "
			"WHERE DateStamp = CURDATE()"
	)
sql_already_scanned_ips = sql_cursor.fetchall()

if len(sql_already_scanned_ips) > 1:
	for scanned_ip in sql_already_scanned_ips:
		sql_scanned_ip = scanned_ip[0]
		if sql_scanned_ip in nmap_ips_no_fqdns:
			nmap_ips_no_fqdns.pop(sql_scanned_ip)
			pass
		if sql_scanned_ip in fqdns_ips:
			fqdns_ips.pop(sql_scanned_ip)

for nmap_ip_no_fqdn in nmap_ips_no_fqdns:
	progress_bar.step()
	
	snmp_fqdn_get = snmp_get(
			2, "1", "", nmap_ip_no_fqdn, ".1.3.6.1.2.1.1.5.0"
	)
	try:
		snmp_fqdns = (snmp_oid(
				snmp_fqdn_get, -1, "= STRING:")[1]
		)
		fqdns_ips[nmap_ip_no_fqdn] = snmp_fqdns
	except TypeError:
		pass
progress_bar.end()

#Function to pull the Default Gateway and run a 
#MAC scan using SNMP against the Default Gateway
ips_macs = defaultgateway_snmp_mac_pull()

fqdns_ips.update(nmap_ips_no_fqdns)

sql_insert_fqdn_ip_mac = []

progress_bar = ProgressBar(
		len(fqdns_ips), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()
for ip, fqdn in fqdns_ips.iteritems():
	progress_bar.step()
	if ip in ips_macs:
		sql_insert_fqdn_ip_mac.append(
				"INSERT INTO tblDocIP (DeviceName, " 
				"IPAddress, MACAddress, DateStamp) " 
				"VALUES('%s', '%s', '%s', CURDATE())" 
				% (fqdn, ip, ips_macs[ip])
		)
	else:
		sql_insert_fqdn_ip_mac.append(
				"INSERT INTO tblDocIP (DeviceName, "
				"IPAddress, DateStamp) "
				"VALUES('%s', '%s', CURDATE())" 
				% (fqdn, ip)
		)
progress_bar.end()

progress_bar = ProgressBar(
		len(sql_insert_fqdn_ip_mac), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

for sql_insert in sql_insert_fqdn_ip_mac:
	progress_bar.step()
	#~ print sql_insert
	sql_cursor.execute(sql_insert)
progress_bar.end()

#Insert into DocScripts the approximate run time
sql_cursor.execute(
		"INSERT INTO tblDocScripts (ScriptName, "
		"RunTime, DateStamp) VALUES('%s', '%s', "
		"CURDATE())" 
		%(script_name, str(time.mktime(time.localtime()) 
		- time.mktime(start_time)))
)

#Commit the SQL changes and close the connection
sql_connection.commit()
sql_connection.close()

#Call function to display the script run time
print funcPythonRunTime(time.localtime())

#Clear all varaibles the script has used
locals().clear()

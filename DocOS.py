from PyFunc import *

#Call function to create a SQL Connection
sql_connection = funcSQLConnect()
sql_cursor = sql_connection.cursor()

#Global variables are pulled from PyFunc.py

#Define Constants
script_name = sys.argv[0]
max_part = 5
current_part = 1

#Query tblDocIP for a list of IP Address from last IP Scan
sql_ip_query = sql_cursor.execute(
		"SELECT tblDocIP.DeviceName, tblDocIP.IPAddress "
		"FROM tblDocIP WHERE tblDocIP.DeviceName "
		"NOT IN (SELECT tblDocOS.DeviceName FROM "
		"tblDocOS WHERE tblDocOS.DateStamp = CURDATE()) "
		"AND tblDocIP.DateStamp = (SELECT "
		"MAX(DateStamp) FROM tblDocIP)"
)
sql_ips_query = sql_cursor.fetchall()

ips_fqdns = {}
for sql_ip_query in sql_ips_query:
	query_ip = sql_ip_query[1]
	query_fqdn = sql_ip_query[0]
	ips_fqdns[query_ip] = query_fqdn

#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(ips_fqdns), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

fqdns_scans_raw = {}
for ip, fqdn in ips_fqdns.iteritems():
	progress_bar.step()
	#Verify that the IP Address is online
	ping_status = verify_online_ping(ip)
	if ping_status == "Success":
		snmp_os_get = snmp_get(
				2, "1", "", ip, ".1.3.6.1.2.1.1.1.0"
		)
		try:
			snmp_os = (snmp_oid(
					snmp_os_get, -1, "= STRING:")[1]
			)
			fqdns_scans_raw[ip] = (fqdn, "snmp", snmp_os)
		except TypeError:
			pass
	else:
		fqdns_scans_raw[ip] = (fqdn, "ping", "Unknown")
progress_bar.end()

for ip in fqdns_scans_raw:
	ips_fqdns.pop(ip)
	
fqdns_nmap_raw = {}
nmap_command = ("sudo nmap %s -O -n -oX nmap_os.xml" 
		% ", ".join(ips_fqdns)
)
nmap_os_scan = subprocess.Popen(
		nmap_command, stdin=None, stdout=-1, 
		stderr=-1, shell=True
)
nmap_os_scan_wait = nmap_os_scan.communicate()

xml_tree = xml.etree.ElementTree.parse("nmap_os.xml")
xml_root = xml_tree.getroot()

#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(xml_root.findall("host")), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

for xml_host in xml_root.findall("host"):
	progress_bar.step()
	nmap_os = "Unknown"
	if xml_host.find("address").attrib["addrtype"] == "ipv4":
		nmap_ip = xml_host.find("address").attrib["addr"]
	try:
		if xml_host.find("./os/osmatch").attrib["accuracy"] == "100":
			nmap_os = xml_host.find("./os/osmatch").attrib["name"]
	except AttributeError:
		fqdns_nmap_raw[nmap_ip] = (
				ips_fqdns[nmap_ip], "nmap", nmap_os
		)
	fqdns_nmap_raw[nmap_ip] = (
			ips_fqdns[nmap_ip], "nmap", nmap_os
	)

os.remove("nmap_os.xml")
progress_bar.end()

os_parsed = {
		"Windows 2000 Version 5.0": "Windows Server 2000", 
		"Windows Version 5.2": "Windows Server 2003", 
		"Windows 2000 Version 5.1": "Windows XP Professional", 
		"Microsoft Windows": "Windows Unknown", 
		"Windows Version 6.1": "Windows Check", 
		"Windows Version 6.0": "Windows Server 2008", 
		"JETDIRECT": "HP Printer", 
		"HP ETHERNET": "HP Printer", 
		"Zebra": "Zebra Printer", 
		"Avaya Phone": "Avaya Phone", 
		"Cisco IOS Software": "Cisco Check", 
		"Ethernet Switch with PoE": "Cisco PoE Switch", 
		"Avaya S8300 Server": "Avaya Phone Server", 
		"Raritan Dominion PX": "Raritan Dominion PX", 
		"DKX2": "Raritan KVM", 
		"Xerox WorkCentre": "Xerox Printer", 
		"Tape Library": "Tape Library", 
		"NetApp": "NetApp SAN", 
		"Linux": "Linux", 
		"Unknown": "Unknown"
	}

#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(fqdns_scans_raw), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

fqdns_scan_os_parsed = {}
for ip, fqdns_scans_oss in fqdns_scans_raw.iteritems():
	progress_bar.step()
	os = fqdns_scans_oss[2]
	fqdns = fqdns_scans_oss[0]
	scan_type = fqdns_scans_oss[1]
	not_in_os_parsed = 0
	
	for raw, parsed in os_parsed.iteritems():
		if raw in os:
			if parsed == "Windows Check":
				win_auth = funcUserPass()
				win_cmd = (
						"/usr/local/wmi/bin/wmic -U %s%%%s \
						//%s 'SELECT OperatingSystemSKU \
						FROM Win32_OperatingSystem'"
						%(win_auth[0], win_auth[1], ip)
				)
				win_os_scan = subprocess.Popen(
						win_cmd, stdin=None, stdout=-1, 
						stderr=-1, shell=True
				)
				while True:
					read_line = win_os_scan.stdout.readline()
					if not read_line: break
					if "'CP850' unavailable" not in read_line and "48" in read_line:
						fqdns_scan_os_parsed[ip] = (
							fqdns, scan_type, "Windows 7 Professional"
						)
					elif "'CP850' unavailable" not in read_line and "8" in read_line:
						fqdns_scan_os_parsed[ip] = (
							fqdns, scan_type, "Windows Server 2008"
						)
					elif "'CP850' unavailable" not in read_line and "7" in read_line:
						fqdns_scan_os_parsed[ip] = (
							fqdns, scan_type, "Windows Server 2008"
						)
					else:
						fqdns_scan_os_parsed[ip] = (
							fqdns, scan_type, "Unknown"
						)
				not_in_os_parsed = 1
				break
			elif parsed == "Cisco Check":
				if "C1200" in os or "C1240" in os or "C1310" in os:
					fqdns_scan_os_parsed[ip] = (
							fqdns, scan_type, "Cisco WAP"
					)
				else:
					fqdns_scan_os_parsed[ip] = (
							fqdns, scan_type, "Cisco Switch"
					)
				not_in_os_parsed = 1
				break
			else:
				fqdns_scan_os_parsed[ip] = (
						fqdns, scan_type, parsed
				)
				not_in_os_parsed = 1
				break
	if not_in_os_parsed == 0:
		fqdns_scan_os_parsed[ip] = (
				fqdns, scan_type, "Unknown"
		)
progress_bar.end()
		

#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(fqdns_nmap_raw), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()
			
for ip, fqdns_nmap_raws in fqdns_nmap_raw.iteritems():
	progress_bar.step()
	os = fqdns_nmap_raws[2]
	fqdns = fqdns_nmap_raws[0]
	scan_type = fqdns_nmap_raws[1]

	for raw, parsed in os_parsed.iteritems():
		if raw in os:
			fqdns_scan_os_parsed[ip] = (
					fqdns, scan_type, parsed
			)
			break
		else:
			fqdns_scan_os_parsed[ip] = (
					fqdns, scan_type, "Unknown"
			)
progress_bar.end()
			
#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(fqdns_scan_os_parsed), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()
for ip, fqdn_scan_os in fqdns_scan_os_parsed.iteritems():
	#~ progress_bar.step()
	fqdn = fqdn_scan_os[0]
	scan_type = fqdn_scan_os[1]
	os = fqdn_scan_os[2]
	
	sql_insert = "INSERT INTO tblDocOS \
			(DeviceName, OS, ScanType, DateStamp) \
			VALUES('%s', '%s', '%s', CURDATE())" \
			%(fqdn, os, scan_type)
	
	#Queue for insertion into the DB
	#~ print sql_insert
	sql_cursor.execute(sql_insert)
progress_bar.end()
		
#Insert into DocScripts the approximate run time
sql_cursor.execute("INSERT INTO tblDocScripts (ScriptName, RunTime, DateStamp) \
	VALUES('%s', '%s', CURDATE())" \
	%(script_name, str(time.mktime(time.localtime()) - time.mktime(start_time))))
	
#Run the SQL Update query and close the conection
sql_connection.commit()
sql_connection.close

#Call function to display the script run time
print funcPythonRunTime(time.localtime())

#Clear all variables the script has used
locals().clear()

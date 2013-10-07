from PyFunc import *

#Call function to create a SQL Connection
sql_connection = funcSQLConnect()
sql_cursor = sql_connection.cursor()

#Global variables are pulled from PyFunc.py

#Define Constants
script_name = sys.argv[0]
part_total_counter = 2
current_part_running = 1

#Query tblDocIP for a list of IP Address from last IP Scan
sql_ip_query = sql_cursor.execute(\
	"SELECT DISTINCT \
			  a.DeviceName \
			, a.IPAddress  \
		FROM tblDocIP  a  \
		WHERE \
			IPAddress = ( \
				SELECT IPAddress FROM tblDocIP WHERE DeviceName = a.DeviceName LIMIT 1 \
			) \
		AND \
			a.DeviceName IN ( \
				SELECT DISTINCT DeviceName FROM tblDocOS WHERE OS = 'Cisco Switch' \
			) \
		 AND \
			DateStamp = (SELECT MAX(DateStamp) FROM tblDocIP)")
sql_ips_query = sql_cursor.fetchall()

#Ping all devices everywhere to populate the MAC table on the switches
#Pull the network segments for DocScan.xml
network_segments = funcNetworkSeg()
for network_segment in network_segments:
	#Run nmap scan using the Network Segments from DocScan.xml
	nmap_command = "nmap %s -sP 1>/dev/null 2>&1" % network_segment
	nmap_ip_scan = subprocess.Popen(
			nmap_command, stdin=None, stdout=-1, stderr=None, shell=True
	)
	nmap_ip_scan.wait()

snmp_mac_bp_ii_port = {}

total_parts = len(sql_ip_query)
for sql_ip_query_results in sql_ips_query:
	current_part = 1
	progress_bar = funcProgressBar(current_part, part_total_counter, current_part_running, total_parts)
	if progress_bar is not None:
		sys.stdout.write(str(progress_bar))
	current_part_running = current_part_running + 1
	
	ip = str(sql_ip_query_results[1])
	sql_switch_name = str(sql_ip_query_results[0])
	snmp_mac_bp_ii_port[sql_switch_name] = []
	
	ping_status = funcPingDevice(ip)
	if ping_status == "Success " + ip:
		snmp_vlan_walk = snmp_walk(5, "2c", "", ip, "1.3.6.1.4.1.9.9.46.1.3.1.1.4.1")
		snmp_vlans = [snmp_oid(snmp_vlan, -1, "= STRING:") for snmp_vlan in snmp_vlan_walk]
		snmp_oid_macs = []
		snmp_oid_bps = []
		snmp_oid_iis = []
		snmp_oid_ports = []
		for snmp_vlan in snmp_vlans:
			snmp_vlan_prefix = "@"
			snmp_vlan_number = ''.join([snmp_vlan_prefix, snmp_vlan[0]])
			snmp_oid_switch_macs = snmp_walk(5, "2c", snmp_vlan_number, ip, ".1.3.6.1.2.1.17.4.3.1.1")
			snmp_oid_switch_bps = snmp_walk(5, "2c", snmp_vlan_number, ip, ".1.3.6.1.2.1.17.4.3.1.2")
			snmp_oid_switch_iis = snmp_walk(5, "2c", snmp_vlan_number, ip, ".1.3.6.1.2.1.17.1.4.1.2")
			snmp_oid_switch_ports = snmp_walk(5, "2c", snmp_vlan_number, ip, ".1.3.6.1.2.1.31.1.1.1.1")
			
			snmp_oid_macs.extend(snmp_oid_switch_macs)
			snmp_oid_bps.extend(snmp_oid_switch_bps)
			snmp_oid_iis.extend(snmp_oid_switch_iis)
			snmp_oid_ports.extend(snmp_oid_switch_ports)
		snmp_mac_bp_ii_port[sql_switch_name].append(snmp_oid_macs)
		snmp_mac_bp_ii_port[sql_switch_name].append(snmp_oid_bps)
		snmp_mac_bp_ii_port[sql_switch_name].append(snmp_oid_iis)
		snmp_mac_bp_ii_port[sql_switch_name].append(snmp_oid_ports)
		
switches_ports_macs = []
for switch_name in snmp_mac_bp_ii_port.keys():
	oid_macs = snmp_mac_bp_ii_port[switch_name][0]
	oid_bps = snmp_mac_bp_ii_port[switch_name][1]
	oid_iis = snmp_mac_bp_ii_port[switch_name][2]
	oid_ports = snmp_mac_bp_ii_port[switch_name][3]
	oid_macs_parsed = dict(
			snmp_oid(oid_mac, -6, "= Hex-STRING:") for oid_mac in oid_macs
	)
	oid_bps_parsed = dict(
			snmp_oid(oid_bp, -6, "= INTEGER:") for oid_bp in oid_bps
	)
	oid_iis_parsed = dict(
			snmp_oid(oid_ii, -1, "= INTEGER:") for oid_ii in oid_iis
	)
	oid_ports_parsed = dict(
			snmp_oid(oid_port, -1, "= STRING:") for oid_port in oid_ports
	)
	
	for mac_key, mac_address in oid_macs_parsed.iteritems():
		if mac_key in oid_bps_parsed:
			if oid_bps_parsed[mac_key] in oid_iis_parsed:
				if oid_iis_parsed[oid_bps_parsed[mac_key]] in oid_ports_parsed:
					switches_ports_macs.append((
							switch_name, 
							oid_ports_parsed[oid_iis_parsed[oid_bps_parsed[mac_key]]], 
							mac_address.replace(" ", "-")
					))
				
#The set fuction removes all duplicates from a list, 
#and the list function turns the set string back into a list
switches_ports_macs = list(set(switches_ports_macs))

current_part_running = 1
#Loop through SQL insert intormation and insert into the DB
total_parts = len(switches_ports_macs)
for switch_port_mac in switches_ports_macs:
	current_part = 2
	progress_bar = funcProgressBar(current_part, part_total_counter, current_part_running, total_parts)
	if progress_bar is not None:
		sys.stdout.write(str(progress_bar))
	current_part_running = current_part_running + 1
	
	#Queue for insertion into the DB
	print (
			"INSERT INTO tblDocPortMAC \
			(DeviceName, PortName, MACAddress, DateStamp) VALUES(%s, %s, %s, CURDATE())" 
			%(switch_port_mac[0], switch_port_mac[1], switch_port_mac[2])
	)
	#sql_cursor.execute("INSERT INTO tblDocPortMAC \
		#(DeviceName, PortName, MACAddress, DateStamp) VALUES(%s, %s, %s, CURDATE())" \
		#%(switch_port_mac[0], switch_port_mac[1], switch_port_mac[2]))
		
#Insert into DocScripts the approximate run time
#sql_cursor.execute("INSERT INTO tblDocScripts (ScriptName, RunTime, DateStamp) \
#	VALUES('%s', '%s', CURDATE())" \
#	%(script_name, str(time.mktime(time.localtime()) - time.mktime(start_time))))
	
#Run the SQL Update query and close the conection
#sql_connection.commit()
sql_connection.close

#Call function to display the script run time
print funcPythonRunTime(time.localtime())

#Clear all variables the script has used
locals().clear()



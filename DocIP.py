#!/usr/local/bin/python3.3
import array
import nmap
import argparse
from PyFunc import *

#Global variables are pulled from PyFunc.py

#Define Constants
script_name = sys.argv[0]
fqdns_ips = {}
nmap_ips_no_fqdns = {}
network_segments = []
max_part = 4
current_part = 1
nm = nmap.PortScanner()

#Create variables for Commnad line arguments
arg_parser = argparse.ArgumentParser(description="Usage %(prog)s -I " \
             + "<Network> -N <No SQL>")
arg_parser.add_argument("-I", dest="network_segments", help="Specify " \
          + "either the IP or a CIDR for nmap")
arg_parser.add_argument("-N", dest="no_sql", help="Specify not to " \
          + "insert into SQL", action="store_true")
args = arg_parser.parse_args()

if(args.network_segments is None):
    #Pull the network segments for DocScan.xml
    network_segments = pull_network_segment()
else:
    network_segments.append(args.network_segments)

#Run nmap scans on all network_segments
progress_bar = ProgressBar(
    len(network_segments), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

for network_segment in network_segments:
    progress_bar.step()
		
    nm.scan(hosts=network_segment, arguments='-sP')
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            if nm[host].hostname():
                fqdns_ips[host] = nm[host].hostname()
            else:
                nmap_ips_no_fqdns[host] = ""
progress_bar.end()

#Verify the IP wasn't previously scanned, then pull DNS info from SNMP
progress_bar = ProgressBar(
    len(nmap_ips_no_fqdns), max_part, current_part
)		
current_part = current_part + 1
progress_bar.draw()

sql_scanned_ip_query = "SELECT "\
                         "tblDocIP.IPAddress "\
                       "FROM tblDocIP "\
                       "WHERE "\
                         "DATEStamp = CURDATE()"

sql_scanned_ip_results = sql_query('Monitoring', \
                                   sql_scanned_ip_query, 'Read')

if len(sql_scanned_ip_results) > 1:
    for scanned_ip in sql_scanned_ip_results[2]:
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

#Create SQL queries for insertion
progress_bar = ProgressBar(
    len(fqdns_ips), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()
for ip, fqdn in fqdns_ips.items():
    progress_bar.step()
    if ip in ips_macs:
        sql_insert_fqdn_ip_mac.append(
            "INSERT "\
            "INTO tblDocIP ("\
              "DeviceName"\
              ", IPAddress"\
              ", MACAddress"\
              ", DateStamp"\
            ") "\
            "VALUES("\
              "'%s'"\
              ", '%s'"\
              ", '%s'"\
              ", CURDATE()"\
            ")" 
            % (fqdn, ip, ips_macs[ip])
        )
    else:
        sql_insert_fqdn_ip_mac.append(
            "INSERT "\
            "INTO tblDocIP ("\
              "DeviceName"\
              ", IPAddress"\
              ", DateStamp"\
            ") "
            "VALUES("\
              "'%s'"\
              ", '%s'"\
              ", CURDATE()"\
            ")" 
            % (fqdn, ip)
        )
progress_bar.end()

#Insert SQL queries into the database
progress_bar = ProgressBar(
    len(sql_insert_fqdn_ip_mac), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

for sql_insert in sql_insert_fqdn_ip_mac:
    progress_bar.step()
    if(args.no_sql == True):
        print(sql_insert)
    else:
        sql_query('Monitoring', sql_insert, 'Write')
progress_bar.end()

#Insert into DocScripts the approximate run time
sql_runtime_query = "INSERT "\
    "INTO tblDocScripts ("\
      "ScriptName"\
      ", RunTime"\
      ", DateStamp"\
    ")"\
    "VALUES("\
      "'%s'"\
      ", '%s'"\
      ", CURDATE())" %(script_name, str(time.mktime(time.localtime()) 
        - time.mktime(start_time)))

if(args.no_sql == False):
    sql_runtime_results = sql_query('Monitoring', sql_runtime_query, 
                                    'Write')

#Call function to display the script run time
print(python_run_time(time.localtime()))

#Clear all varaibles the script has used
locals().clear()

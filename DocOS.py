#!/usr/local/bin/python3.3
import argparse
from PyFunc import *

#Global variables are pulled from PyFunc.py

#Define Constants
script_name = sys.argv[0]
max_part = 5
current_part = 1

#Create variables for Command Line arguments
arg_parser = argparse.ArgumentParser(description="Usage %prog)s -I " \
                     + "<Network> -N <No SQL>")
arg_parser.add_argument("-I", dest="ip_address", help="Specify " \
          + "the IP address for nmap OS Scan")
arg_parser.add_argument("-N", dest="no_sql", help="Specify not to " \
          + "insert into SQL", action="store_true")
args = arg_parser.parse_args()

#Query tblDocIP for a list of IP Address from last IP Scan
sql_ip_query = "SELECT "\
                 "tblDocIP.DeviceName"\
                 ", tblDocIP.IPAddress "\
               "FROM tblDocIP "\
               "WHERE "\
                 "tblDocIP.DeviceName NOT IN ("\
                   "SELECT "\
                     "tblDocOS.DeviceName "\
                   "FROM tblDocOS "\
                   "WHERE "\
                     "tblDocOS.DateStamp = CURDATE()"\
                   ") "\
                 "AND "\
                   "tblDocIP.DateStamp = ("\
                     "SELECT "\
                       "MAX(DateStamp) "\
                     "FROM tblDocIP"\
                   ")"
sql_ip_results = sql_query('Monitoring', sql_ip_query, 'Read')

ips_fqdns = {}
if(args.ip_address is None):
    for sql_ip_result in sql_ip_results:
        query_ip = sql_ip_result[1]
        query_fqdn = sql_ip_result[0]
        ips_fqdns[query_ip] = query_fqdn
else:
    ips_fqdns[args.ip_address] = args.ip_address

#Check for the OS using SNMP first (fastest out of all of the OS scans)
progress_bar = ProgressBar(
    len(ips_fqdns), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

fqdns_scans_raw = {}
for ip in ips_fqdns:
    progress_bar.step()
    #Verify that the IP Address is online then try to pull the OS from SNMP
    ping_status = verify_online_ping(ip)
    if ping_status == "Success":
        snmp_os_get = snmp_get(
                2, "1", "", ip, ".1.3.6.1.2.1.1.1.0"
        )
        try:
            snmp_os = (snmp_oid(
                    snmp_os_get, -1, "= STRING:")[1]
            )
            fqdns_scans_raw[ip] = (ips_fqdns[ip], "snmp", snmp_os)
        except TypeError:
            pass
    else:
        fqdns_scans_raw[ip] = (ips_fqdns[ip], "ping", "Unknown")
progress_bar.end()

#Remove any IP addresses that the OS was pulled from SNMP
for ip in fqdns_scans_raw:
    ips_fqdns.pop(ip)

fqdns_nmap_raw = {}
if(len(ips_fqdns) > 0):
    #Try to pull the OS from NMAP
    nmap_command = ("sudo /usr/bin/nmap %s -O -n -oX nmap_os.xml" 
                    % ", ".join(ips_fqdns)
    )
    nmap_os_scan = subprocess.Popen(
            nmap_command, stdin=None, stdout=-1, 
            stderr=-1, shell=True
    )
    nmap_os_scan_wait = nmap_os_scan.communicate()
    
    xml_tree = xml.etree.ElementTree.parse("nmap_os.xml")
    xml_root = xml_tree.getroot()
    
    progress_bar = ProgressBar(
        len(xml_root), max_part, current_part
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
            if nmap_ip in ips_fqdns.keys() == True:
                fqdns_nmap_raw[nmap_ip] = (
                    ips_fqdns[nmap_ip], "nmap", nmap_os
                )
        if nmap_ip in ips_fqdns.keys() == True:
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
        "Canon": "Canon Printer",
        "Unknown": "Unknown"
    }

#Parse out generic OS response and identify exact OS
progress_bar = ProgressBar(
    len(fqdns_scans_raw), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

fqdns_scan_os_parsed = {}
#Parse out the fqdns_scans_raw for comparisons
for ip in fqdns_scans_raw:
    progress_bar.step()
    os = fqdns_scans_raw[ip][2]
    fqdns = fqdns_scans_raw[ip][0]
    scan_type = fqdns_scans_raw[ip][1]
    not_in_os_parsed = 0
    
    for raw in os_parsed:
        if raw in os:
            if os_parsed[raw] == "Windows Check":
                win_auth = windows_user_password()
                win_cmd = (
                        "/usr/bin/wmic -U %s%%%s " \
                        "//%s 'SELECT OperatingSystemSKU " \
                        "FROM Win32_OperatingSystem'"
                        %(win_auth[0], win_auth[1], ip)
                )
                win_os_scan = subprocess.Popen(
                        win_cmd, stdin=None, stdout=-1, 
                        stderr=-1, shell=True
                )
                #Compare the WMIC output to identify the specific OS
                while True:
                    read_line = win_os_scan.stdout.readline().decode("utf-8")
                    if not read_line: break
                    if "'CP850' unavailable" not in read_line and \
                       "48" in read_line:
                        fqdns_scan_os_parsed[ip] = (
                            fqdns, scan_type, "Windows 7 Professional"
                        )
                    elif "'CP850' unavailable" not in read_line and \
                         "8" in read_line:
                        fqdns_scan_os_parsed[ip] = (
                            fqdns, scan_type, "Windows Server 2008"
                        )
                    elif "'CP850' unavailable" not in read_line and \
                         "7" in read_line:
                        fqdns_scan_os_parsed[ip] = (
                            fqdns, scan_type, "Windows Server 2008"
                        )
                    else:
                        fqdns_scan_os_parsed[ip] = (
                            fqdns, scan_type, "Unknown"
                        )
                not_in_os_parsed = 1
                break
            elif os_parsed[raw] == "Cisco Check":
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
                        fqdns, scan_type, os_parsed[raw]
                )
                not_in_os_parsed = 1
                break
    if not_in_os_parsed == 0:
        fqdns_scan_os_parsed[ip] = (
                fqdns, scan_type, "Unknown"
        )
progress_bar.end()

#Refactor the lists into a single list        
progress_bar = ProgressBar(
    len(fqdns_nmap_raw), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()
            
for ip in fqdns_nmap_raw:
    progress_bar.step()
    os = fqdns_nmap_raw[ip][2]
    fqdns = fqdns_nmap_raw[ip][0]
    scan_type = fqdns_nmap_raw[ip][1]

    for raw in os_parsed:
        if raw in os:
            fqdns_scan_os_parsed[ip] = (
                    fqdns, scan_type, os_parsed[raw]
            )
            break
        else:
            fqdns_scan_os_parsed[ip] = (
                    fqdns, scan_type, "Unknown"
            )
progress_bar.end()

#Build query and insert records into the DB.            
progress_bar = ProgressBar(
    len(fqdns_scan_os_parsed), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

for ip in fqdns_scan_os_parsed:
    if(args.no_sql == False):
        progress_bar.step()
    fqdn = fqdns_scan_os_parsed[ip][0]
    scan_type = fqdns_scan_os_parsed[ip][1]
    os = fqdns_scan_os_parsed[ip][2]
    
    sql_insert = "INSERT "\
                 "INTO tblDocOS " \
                   "(DeviceName, OS, ScanType, DateStamp)" \
                 "VALUES(" \
                   "'%s', '%s', '%s', CURDATE())" \
            %(fqdn, os, scan_type)
    if(args.no_sql == True): 
        print(sql_insert)
    else:
        sql_query('Monitoring', sql_insert, 'Write')
progress_bar.end()
        
#Insert into DocScripts the approximate run time
sql_runtime_query = "INSERT " \
                    "INTO tblDocScripts (" \
                      "ScriptName" \
                      ", RunTime" \
                      ", DateStamp" \
                    ")" \
                    "VALUES(" \
                      "'%s'" \
                      ", '%s'" \
                      ", CURDATE())" %(script_name, 
                                      str(time.mktime(time.localtime())
                                      - time.mktime(start_time)))
if(args.no_sql == False):
    sql_runtime_results = sql_query('Monitoring', sql_runtime_query, 
                                    'Write')
    
#Call function to display the script run time
print(python_run_time(time.localtime()))

#Clear all variables the script has used
locals().clear()

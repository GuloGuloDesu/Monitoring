from PyFunc import *

#Call function to create a SQL Connection
sql_connection = funcSQLConnect()
sql_cursor = sql_connection.cursor()

#Global variables are pulled from PyFunc.py

#Define Constants
script_name = sys.argv[0]
max_part = 2
current_part = 1

#Query DocIP and DocOS for WIndows boxes
sql_ip_fqdn_query = sql_cursor.execute(
		"SELECT tblDocIP.IPAddress, tblDocIP.DeviceName FROM \
		tblDocIP WHERE tblDocIP.DeviceName IN (\
		SELECT tblDocOS.DeviceName FROM \
		tblDocOS WHERE tblDocOS.OS IN (\
		'Windows 2008 Server', 'Windows Server 2003', \
		'Windows 7 Professional', \
		'Windows XP Professional') AND \
		tblDocOS.DateStamp = (SELECT \
		MAX(tblDocOS.DateStamp) FROM \
		tblDocOS)) AND tblDocIP.DateStamp = (\
		SELECT MAX(tblDocIP.DateStamp) FROM tblDocIP)"
)
		
sql_ips_fqdns = sql_cursor.fetchall()

#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(sql_ips_fqdns), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

fqdn_logon_raw  = {}
for sql_ip_fqdn in sql_ips_fqdns:
	progress_bar.step()
	ip = sql_ip_fqdn[0]
	fqdn = sql_ip_fqdn[1]
	#Verify that the IP Address is online
	ping_status = verify_online_ping(ip)
	if ping_status == "Success":
		#Pull Windows Authentication
		win_auth = funcUserPass()
		
		#WMI Query to pull the Last Logon
		win_query = "'SELECT UserName FROM \
				Win32_ComputerSystem'"
		win_cmd = (
				"/usr/local/wmi/bin/wmic -U %s%%%s //%s %s"
				%(win_auth[0],win_auth[1], ip, win_query)
		)
		win_logons = subprocess.Popen(
				win_cmd, stdin=None, stdout=-1, 
				stderr=-1, shell=True
		)
		del(win_auth)
		while True:
			read_line = win_logons.stdout.readline()
			if not read_line: break
			fqdn_logon_raw[fqdn] = read_line
progress_bar.end()
			
#Assign a total size for the progress bar
progress_bar = ProgressBar(
	len(sql_ips_fqdns), max_part, current_part
)
current_part = current_part + 1
progress_bar.draw()

fqdn_logon = {}
for fqdn, logon_raw in fqdn_logon_raw.iteritems():
	progress_bar.step()
	if (
			"'CP850' unavailable" not in logon_raw and
			"Win32_ComputerSystem" not in logon_raw and
			"Name|UserName" not in logon_raw and
			"ERROR:" not in logon_raw and
			"(null)" not in logon_raw
	):
		fqdn_logon[fqdn] = logon_raw.split("|")[1].strip().replace("\\", "/")
	else:
		fqdn_logon[fqdn] = "Unknown"
progress_bar.end()

#Loop through dictionary and insert into DB
for fqdn, logon in fqdn_logon.iteritems():
	sql_insert = (
			"INSERT INTO tblDocLogon (DeviceName, \
			UserID, DateStamp) VALUES('%s', '%s', \
			CURDATE())"
			%(fqdn, logon)
	)
	#~ print sql_insert
	#Insert results into the table
	sql_cursor.execute(sql_insert)

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

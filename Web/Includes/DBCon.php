<?php

#Disable the website from being directly accessed
	#Create an array of the Website location
	$SelfParts = explode("/", htmlentities($_SERVER["PHP_SELF"]));
	
	#Createan array of the webpage OS file location
	$FileParts = explode("/", __FILE__);
	
	#Compare the last variable of the arrays to see if they match
	if(end($SelfParts) == end($FileParts)) {
		print "You do not have access to this web page";
		
		#Clear variables
		unset($SelfParts);
		unset($FileParts);
	}

    #Function to create a SQL Connection
    function SQLConnection($XMLUserID, $XMLPassword, $Database) {
        #Pull SQL Credentials from XML
        $XMLCredentials = simplexml_load_file('Includes/Credentials.xml'); 
        $UserID = trim($XMLCredentials->Credentials[0]->$XMLUserID);
        $Password = trim($XMLCredentials->Credentials[0]->$XMLPassword);

        #Connect to MySQL Server
        $DBCon = mysql_connect("localhost", $UserID, $Password)
            or die("Could not connect to SQL Server: " .mysql_error());
        #Connect to MySQL Database
        mysql_select_db($Database, $DBCon)
            or die("Could not connect to DB: " .mysql_error());

        #Clear variables
        unset($XMLCredentials);
        unset($UserID);
        unset($Password);

        return $DBCon;
    }



<?php
#Disable the website from being directly accessed
	#Create an array of the Website location
	$arrSelfParts = explode("/", htmlentities($_SERVER["PHP_SELF"]));
	
	#Createan array of the webpage OS file location
	$arrFileParts = explode("/", __FILE__);
	
	#Compare the last variable of the arrays to see if they match
	if(end($arrSelfParts) == end($arrFileParts)) {
		print "You do not have access to this web page";
		
		#Clear variables
		unset($arrSelfParts);
		unset($arrFileParts);
	}
	
	#Clean variables fro HTML and SQL
	function funcHTMLSQL($strVarClean) {
		$strVarClean = mysql_real_escape_string($strVarClean);
		$strVarClean = htmlspecialchars($strVarClean);
		#Return the cleaned string
		return $strVarClean;
	}
	
	#Verify that only a number has been submitted
	function funcIntValidate($intInteger) {
		if(!filter_var($intInteger, FILTER_VALIDATE_INT)) {
			#Create an array, (Error Code, Error Message, Value)
			$arrInteger = array(1, "Only numbers are allowed to be submitted" . 
				" to this form field", $intInteger);
		}
		else {
			#Create an array, (Error Code, Error Message, Value)
			$arrInteger = array(0, '', $intInteger);
		}
		#Clear variables
		unset($intInteger);
		
		#Return the array
		return $arrInteger;
	}
	
	#Verify that only an IP Address has been submitted
	function funcIPValidate($strIPAddress) {
		if(!filter_var($strIPAddress, FILTER_VALIDATE_IP)) {
			#Create an array, (Error Code, Error Message, Value)
			$arrIPAddress = array(1, "Your IP Address does not appear to be " . 
				"a valid IP Address", $strIPAddress);
		}
		else {
			#Create an array, (Error Code, Error Message, Value)
			$arrIPAddress = array(0, '', $strIPAddress);
		}
		#Clear variables
		unset($strIPAddress);
		
		#Return an array
		return $arrIPAddress;
	}
	
	#Verify that only an Email Address has been submitted
	function funcEMailValidate($strEMailAddress) {
		if(!filter_var($strEMailAddress, FILTER_VALIDATE_EMAIL)) {
			#Create an array, (Error Code, Error Message, Value)
			$arrEMailAddress = array(1, "Your E-mail Address does not appear" . 
				" to be a valid E-mail Address", $strEMailAddress);
		}
		else {
			#Create an array, (Error Code, Error Message, Value)
			$arrEMailAddress = array(0, '', $strEMailAddress);
		}
		#Clear variables
		unset($strEMailAddress);
		
		#Return an array
		return $arrEMailAddress;
	}

    #Function for salting and hasing passwords
    function PasswordSalt($Password) {
        #Hash the password to avoid any character incompatibilities
        $Hash = hash('sha256', $Password);

        #Generate a pseudo random IV size
        $MCryptSize = mcrypt_get_iv_size(MCRYPT_CAST_256, MCRYPT_MODE_CFB);

        #Generate a random salt based on the pseudo random IV size
        #You must remove the + otherwise BCrypt will fail
        $Salt = str_replace('+', '.', base64_encode(
            mcrypt_create_iv($MCryptSize, MCRYPT_DEV_URANDOM)));

        #Generate teh hashed and salted password
        $PasswordHash = crypt($Hash, '$2y$13$' . $Salt);
        unset($Hash);
        unset($MCryptSize);

        #Verify there were no errors in generating the hash
        if(strlen($PasswordHash) < 5) {
            exit('Salting failure<br>Please try again.');
        }

        return array($PasswordHash, $Salt);
    }

    #Function for running SQL Queries
    function SQLQuery($Database, $Query, $QueryType) {
        #Determine Type of SQL Connection and Query Type
        if($QueryType = 'Admin') {
            #Verify if SQL Connection already exists
            if(!mysql_ping($DBConAdmin) {
                $DBConAdmin = SQLConnection('UserIDSQLAdmin', 
                                            'PasswordSQLAdmin', $Database);
            }
            $SQLQueryRun = mysql_query($Query, $DBConAdmin);
            return $SQLQueryRun;
        }
        elseif($QueryType = 'Write') {
            if(!mysql_ping($DBConWrite) {
                $DBConWrite = SQLConnection('UserIDSQLWrite', 
                                            'PasswordSQLWrite', $Database);
            }
            $SQLQueryRun = mysql_query($Query, $DBConWrite);
            return $SQLQueryRun;
        }
        elseif($QueryType = 'Read') {
            if(!mysql_ping($DBConRead) {
                $DBConRead = SQLConnection('UserIDSQLRead', 
                                           'PasswordSQLRead', $Database);
            }
            $SQLQueryRun = mysql_query($Query, $DBConRead);
            while($SQLQueryResults = mysql_fetch_array($SQLQueryRun));
            return $SQLQueryResults;
    }

<?php
	#Include Header information this includes layout and DB connections
	include "Includes/Header.php";
	
	#Connect to the SQL Database
	$objDBConRead = funcDBRead();
	
	#Query for all the Port, Patch, Cable matchings
	$strQueryPatch = "SELECT
									  pk
									, DeviceName
									, PortName
									, Cable
								FROM tblDocPortPatch";
								
	#Execute the Query
	$objQueryPatch = mysql_query($strQueryPatch, $objDBConRead);
	
	#Loop through SQL results and populate the table
	while($lpQueryPatch = mysql_fetch_object($objQueryPatch)) {
		$arrSQL[] = array(
			  $lpQueryPatch->pk
			, $lpQueryPatch->DeviceName
			, $lpQueryPatch->PortName 
			, $lpQueryPatch->Cable);
	}
	
	#Clear variables
	unset($strQueryPatch);
	unset($objQueryPatch);
	unset($intColor);
	unset($strTab);
	
	#Close SQL Connection
	mysql_close($objDBConRead);	
	
	#Loop through all of the $_POST values (array)
	foreach($_POST as $lpKey => $lpValue) {
		#Clean for SQL and HTML on POST variables
		$CLNlpDeviceName = funcHTMLSQL($lpValue[0]);
		$CLNlpPortName = funcHTMLSQL($lpValue[1]);
		$CLNlpCable = funcHTMLSQL($lpValue[2]);
		
		#Verify that the PK is an Integer
		#array returns (Error Code, Error Message, value)
		$arrInteger = funcIntValidate($lpKey);
		if($arrInteger[0] == 0) {
			#Assign verified integer
			$CLNintPK = $arrInteger[2];
			
			#Clear variables
			unset($arrInteger);
		}
		elseif($arrInteger[0] == 1) {
			#Print Error Message
			print $arrInteger[1];
			
			#Clear variables and exit
			unset($arrInteger);
			unset($CLNlpDeviceName);
			unset($CLNlpPortName);
			unset($CLNlpCable);
			unset($arrSQL);
			exit;
		}
		
		#Check to see if the PK, Device, Port, Cable is in the SQL results
		if(!in_array(
			array(
				  $CLNintPK
				, $CLNlpDeviceName
				, $CLNlpPortName
				, $CLNlpCable
			), $arrSQL)) {
			#Create an array to update the table	
			$arrSQLUpdate[] = "UPDATE 
				  tblDocPortPatch 
				SET 
				  DeviceName = '" . $CLNlpDeviceName . "'
				, PortName = '" . $CLNlpPortName . "'
				, Cable = '" . $CLNlpCable . "'
				, DateStamp = CURDATE()
				WHERE
					pk = '" . $CLNintPK . "'";
		}
	}
	
	#Connect to the SQL Database
	$objDBConWrite = funcDBWrite();

	#Loop through the SQL array and update the table
	foreach($arrSQLUpdate as $lpSQLUpdate) {
		#Update the table
		mysql_query($lpSQLUpdate, $objDBConWrite);
		print $lpSQLUpdate . "<br>";
	}
	
	#Clear variables
	unset($arrSQLUpdate);
	unset($arrSQL);
	unset($CLNlpDeviceName);
	unset($CLNlpPortName);
	unset($CLNlpCable);
	unset($CLNintPK);
	
	#Close SQL Connection
	mysql_close($objDBConWrite);
?>

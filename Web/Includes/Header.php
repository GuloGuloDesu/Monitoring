<?php
	error_reporting(E_ALL);
	ini_set("display_errors", 1);
	
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
	
	#DBCon.php for DB Connections and PHPFunc for PHP Functions
	require "DBCon.php";
	require "PHPFunc.php";
	
	#Define Constants
	$intColor = 0;
	$Tabs = "   ";
?>
<!DOCTYPE html>
<html lang='en'>
	<head>
		<meta charset='utf-8'>
		<link rel='stylesheet' type='text/css' href='Main.css'>
		<meta http-equiv='expires' content='0'>
		<title>
			
		</title>
	</head>
	<body>

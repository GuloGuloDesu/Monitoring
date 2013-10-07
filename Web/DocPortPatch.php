<?php
	#Include Header information this includes layout and DB connections
	include "Includes/Header.php";
?>
		<form action='DocPortPatchUpdate.php' method='post'>
			<p>
				<table>
					<thead>
						<tr>
							<th>
								Device Name
							</th>
							<th>
								Port Name
							</th>
							<th>
								Patch Number
							</th>
							<th>
								Cable Label
							</th>
							<th>
								Date Stamp
							</th>
						</tr>
					</thead>
					<tbody>		
<?php	
	#Connect to the SQL Database
	$objDBConRead = funcDBRead();
	
	#Query for all the Port, Patch, Cable matchings
	$strQueryPatch = "SELECT
									  pk
									, DeviceName
									, PortName
									, Patch
									, Cable
									, DateStamp
								FROM tblDocPortPatch";
								
	#Execute the Query
	$objQueryPatch = mysql_query($strQueryPatch, $objDBConRead);
	
	#Loop through SQL results and populate the table
	while($lpQueryPatch = mysql_fetch_object($objQueryPatch)) {
		$intColor++;
		print str_repeat($strTab, 6) . 
			"<tr class='color"  . ($intColor & 1) . "'>\n";
		print str_repeat($strTab, 7) . "<td>\n";
		print str_repeat($strTab, 8) . 
			"<input id='" . $lpQueryPatch->pk . "[]'" .  
			"type='text' name='" . $lpQueryPatch->pk . "[]'" . 
			"value='" . $lpQueryPatch->DeviceName . 
			"' placeholder='" . $lpQueryPatch->DeviceName . "'>\n";
		print str_repeat($strTab, 7) . "</td>\n";
		print str_repeat($strTab, 7) . "<td>\n";
		print str_repeat($strTab, 8) . 
			"<input id='" . $lpQueryPatch->pk . "[]'" . 
			"type='text' name='" . $lpQueryPatch->pk . "[]'" . 
			"value='" . $lpQueryPatch->PortName . 
			"' placeholder='" . $lpQueryPatch->PortName . "'>\n";
		print str_repeat($strTab, 7) . "</td>\n";
		print str_repeat($strTab, 7) . "<td>\n";
		print str_repeat($strTab, 8) . $lpQueryPatch->Patch . "\n";
		print str_repeat($strTab, 7) . "</td>\n";
		print str_repeat($strTab, 7) . "<td>\n";
		print str_repeat($strTab, 8) . 
			"<input id='" . $lpQueryPatch->pk . "[]'" . 
			"type='text' name='" . $lpQueryPatch->pk . "[]'" . 
			"value='" . $lpQueryPatch->Cable . 
			"' placeholder='" . $lpQueryPatch->Cable . "'>\n";
		print str_repeat($strTab, 7) . "</td>\n";
		print str_repeat($strTab, 7) . "<td>\n";
		print str_repeat($strTab, 8) . $lpQueryPatch->DateStamp . "\n";
		print str_repeat($strTab, 7) . "</td>\n";
		print str_repeat($strTab, 6) . "</tr>\n";
	}
	
	#Clear variables
	unset($strQueryPatch);
	unset($objQueryPatch);
	unset($intColor);
	unset($strTab);
	
	#Close SQL Connection
	mysql_close($objDBConRead);			
?>
					</tbody>
				</table>
				<input id='Button2' type='submit' value='Update'>
			</p>
		</form>
	</body>
</html>

<?php
	#Include Header information this includes layout and DB connections
	include "Includes/Header.php";
?>
		<p>
			<table>
				<thead>
					<tr>
						<th>
							User Name
						</th>
						<th>
							Device Name
						</th>
						<th>
							OS
						</th>
						<th>
							Scan Type
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
	$strQueryLogon = "SELECT DISTINCT
			  tblDocLogon.UserID 
			, tblDocOS.DeviceName 
			, tblDocOS.OS 
			, tblDocOS.ScanType 
			, tblDocLogon.DateStamp 
		FROM tblDocLogon 
		INNER 
		  JOIN tblDocOS 
			ON tblDocOS.DeviceName = tblDocLogon.DeviceName 
		WHERE 
			tblDocLogon.DateStamp = ( 
				SELECT MAX(DateStamp) FROM tblDocLogon 
			) 
		ORDER BY tblDocLogon.UserID";
								
	#Execute the Query
	$objQueryLogon = mysql_query($strQueryLogon, $objDBConRead);
	
	#Loop through SQL results and populate the table
	while($lpQueryLogon = mysql_fetch_object($objQueryLogon)) {
		$intColor++;
		print str_repeat($strTab, 5) . 
			"<tr class='color"  . ($intColor & 1) . "'>\n";
		print str_repeat($strTab, 6) . "<td>\n";
		print str_repeat($strTab, 7) . $lpQueryLogon->UserID . "\n";
		print str_repeat($strTab, 6) . "</td>\n";
		print str_repeat($strTab, 6) . "<td>\n";
		print str_repeat($strTab, 7) . $lpQueryLogon->DeviceName . "\n";
		print str_repeat($strTab, 6) . "</td>\n";
		print str_repeat($strTab, 6) . "<td>\n";
		print str_repeat($strTab, 7) . $lpQueryLogon->OS . "\n";
		print str_repeat($strTab, 6) . "</td>\n";
		print str_repeat($strTab, 6) . "<td>\n";
		print str_repeat($strTab, 7) . $lpQueryLogon->ScanType . "\n";
		print str_repeat($strTab, 6) . "</td>\n";
		print str_repeat($strTab, 6) . "<td>\n";
		print str_repeat($strTab, 7) . $lpQueryLogon->DateStamp . "\n";
		print str_repeat($strTab, 6) . "</td>\n";
		print str_repeat($strTab, 6) . "</tr>\n";
	}
	
	#Clear variables
	unset($strQueryLogon);
	unset($objQueryLogon);
	unset($intColor);
	unset($strTab);
	
	#Close SQL Connection
	mysql_close($objDBConRead);			
?>
				</tbody>
			</table>
		</p>
	</body>
</html>

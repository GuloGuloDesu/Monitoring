<?php
	#Inclue Header information, this includes Layout, and DB Connections
	include "Includes/Header.php";
?>
		<div id='LogonBoxForm'>
			<h2>Monitoring Logon</h2>
			<form id='Logon' name='Logon' action='Login.php' method='post'>
				<fieldset>
					<p>
						<label for='UserID'>
							User Name
						</label>
                        <input 
                            id='UserID' type='text' name='UserID' 
                            class='text' placeholder='User Name'>
					</p>
					<p>
						<label for='Password'>
							Password
						</label>
                        <input 
                            id='Password' type='password' name='Password' 
                            clase='text' placeholder='Password'>
					</p>
					<p>
						<input id='Button1' type='submit' value='Logon'>
					</p>
				</fieldset>
			</form>
		</div>
	</body>
</html>

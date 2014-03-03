<?php
    #Include Header information, this includes Layout, and DB connections
    include 'Includes/Header.php';

    #Clean UserID for SQL and HTML
    $CLEANUserID = CleanHTMLSQL($_POST['UserID']);

    #Verify IP Address (Array returns error code, error message, value)
    $IPAddresses = IPValidate($_SERVER['REMOTE_ADDR']);
    if($IPAddresses[0] == 0) {
        $CLEANIPAddress = $IPAddresses[2];
        unset($IPAddresses);
    }
    elseif($IPAddresses[0] == 1) {
        print $IPAddresses[1];
        unset($IPAddresses);
        unset($CLEANUserID);
        exit;
    }
    $FTPPasswordQuery = "SELECT
                           (SELECT
                             COUNT(tblWebAuthLogonLog.FailedLogon)
                           FROM tblWebAuthLogonLog
                           WHERE
                             tblWebAuthLogonLog.UserID = '{$CLEANUserID}'
                           AND
                             tblWebAuthLogonLog.TimeAttempt > DATE_ADD(
                               CURRENT_TIMESTAMP, INTERVAL -15 MINUTE))
                             AS FailedLogonCount
                           , tblWebAuthUsers.Password
                           , tblWebAuthUsers.Salt
                           , tblWebAuthUserGroup.MonGroup
                         FROM tblWebAuthUsers
                         LEFT
                           JOIN tblWebAuthUserGroup
                             ON tblWebAuthUserGroup.UserID = 
                                tblWebAuthUsers.UserID
                         WHERE
                           tblWebAuthUsers.UserID = '{$CLEANUserID}'
                         AND
                           tblWebAuthUsers.UserActive = 1";
    $FTPPasswordResults = SQLQuery('Monitoring', $FTPPasswordQuery, 'Read');
    foreach($FTPPasswordResults[1] as $FTPPasswordResult) {
        $Password = $FTPPasswordResult['Password'];
        $FailedLogon = $FTPPasswordResult['FailedLogonCount'];
        $Salt = $FTPPasswordResult['Salt'];
        $UserGroup = $FTPPasswordResutl['MonGroup'];
    }
    unset($FTPPasswordQuery);
    unset($FTPPassowrdResult);
    SQLClose($FTPPasswordResults[0]);

    #Verify the SQL Query returned results
    if(isset($FailedLogon)) {
        if($FailedLogon < 3) {
            #If the passwords match then update the database with a 
            #successful login, and set the session vairables and send the
            #user to the correct home page based on their UserGroup
            if($Password == PasswordVerify($_POST['Password'], $Salt)) {
                $LogInsertQuery = "INSERT
                                   INTO tblWebAuthLogonLog (
                                       UserID
                                     , TimeAttempt
                                     , IPAddress
                                     , DateStamp
                                   )
                                   VALUES (
                                       '{$CLEANUserID}'
                                     , ' CURRENT_TIMESTAMP
                                     , '{$CLEANIPAddress}'
                                     , CURDATE()
                                   )";
                $LogInsertResults = SQLQuery('Monitoring', 
                                              $LogInsertQuery, 'Write');
                SQLClose($LogInsertResults[0]);

                #Assign Session variables
                $_SESSION['UserID'] = $CLEANUserID;
                $_SESSION['UserGroup'] = $UserGroup;

                unset($CLEANUserID);
                unset($CLEANIPAddress);
                unset($Password);
                unset($FailedLogon);
                unset($Salt);
                unset($UserGroup);
                unset($LogInsertyQuery);

                if($_SESSION['UserGroup]' == 'Corporate Admin') {
                        header('Location:/DocDevices.php');
                }
                print 'You have successfully logged on! <br>' . 
                       'Now transferring you to your homepage.';
            }
            #If UserID and password do not match then insert failed logon
            else {
                $ErrorMessage = 'Invalid UserID or Password<br>' . 
                      'This was attempt ' . $FailedLogon + 1 . ' of 3<br>' .
                      'After 4 failed attempts your account will be ' . 
                      'locked out for 15 minutes' . 
                      'Please go <a href="Logon.php">Back</a> and retry';
            }
        }
        #Continue to update failed log in attempts
        else {
            $ErrorMessage = 'You have had more than 3 failed logon ' . 
                            'attempts in the last 15 minutes<br>' . 
                            'Please try again in another 15 minutes';
        }
        unset($CLEANUserID);
        unset($CLEANIPAddress);
        unset($Password);
        unset($FailedLogon);
        unset($Salt);
        unset($UserGroup);
        unset($LogInsertQuery);
    }
    else {
        $ErrorMessage = 'Invalid UserID or password<br>' . 
                        'Please go <a href="Logon.php">Back</a> and retry';
        unset($CLEANUserID);
        unset($CLEANIPAddress);
    }
    $LogInsertQuery = "INSERT
                       INTO tblWebAuthLogonLog (
                           UserID
                         , FailedLogon
                         , TimeAttempt
                         , IPAddress
                         , DateStamp
                      )
                      VALUES (
                          '{$CLEANUserID}'
                        , 1
                        , CURRENT_TIMESTAMP
                        , '{$CLEANIPAddress}'
                        , CURDATE()
                      )";
    $LogInsertResults = SQLQuery('Monitoring', 
                                  $LogInsertQuery, 'Write');
    SQLClose($LogInsertResults[0]);
?>
    </body>
</html>

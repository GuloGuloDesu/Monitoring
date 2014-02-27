<?php
    #Include Header information, this includes layout, and DB connections
    include 'Includes/Header.php';

    #Create UserID and Group Arrays
    $UserIDs = array();
    $UserGroups = array(); 

    #Clean all variables for SQL and HTML
    if(isset($_POST['FirstName'])) {
        $CleanFirstName = funcHTMLSQL($_POST['FirstName']);
    }
    if(isset($_POST['LastName'])) {
       $CleanLastName = funcHTMLSQL($_POST['LastName']);
    }
    if(isset($_POST['UserID'])) {
       $CleanUserID = funcHTMLSQL($_POST['UserID']);
    }
    if(isset($_POST['EMailAddress'])) {
        $CleanEMailAddress = funcHTMLSQL($_POST['EMailAddress']);
        #Verify EMail Address Array returns error code, error message, value
        $EMailAddresses = funcEMailValidate($CleanEMailAddress);
        if($EMailAddresses[0] == 0) {
            #Assign verified EMail Address
            $CleanEMailAddress = $EMailAddresses[2];
            unset($EMailAddresses);
        }
        elseif($EMailAddresses[0] == 1) {
            #Print Error message
            print $EMailAddresses[1];
            #Clear variables and exit
            unset($EMailAddresses);
            exit;
         }
    }
    if(isset($_POST['MonGroup'])) {
            $CleanMonGroup = funcHTMLSQL($_POST['MonGroup']);
    }
    if(isset($_POST['VerifyMonGroup'])) {
            $CleanVerifyMonGroup = funcHTMLSQL($_POST['VerifyMonGroup']);
    }
    if(isset($_POST['MonUserID'])) {
            $CleanMonUserID = funcHTMLSQL($_POST['MonUserID']);
    }

    #Connect to the SQL Database
    $DBConRead = SQLConnection('UserIDSQLRead', 'PasswordSQLRead', 
                               'Monitoring'); 

    $GroupsQuery = "SELECT
                      DISTINCT(tblWebAuthUserGroup.MonGroup)
                    FROM tblWebAuthUserGroup";
    $GroupsResults = mysql_query($GroupsQuery, $DBConRead);
    while($GroupsResult = mysql_fetch_object($GroupsResults)) {
        $UserGroups[] = $GroupsResult->MonGroup;
    }

    unset($GroupsQuery);
    unset($GroupsResults);
    unset($GroupsResult);

    $UsersQuery = "SELECT
                     DISTINCT(tblWebAuthUsers.UserID)
                   FROM tblWebAuthUsers";
    $UsersResults = mysql_query($UsersQuery, $DBConRead);
    while($UsersResult = mysql_fetch_object($UsersResults)) {
        $UserIDs[] = $UsersResult->UserID;
    }

    unset($UsersQuery);
    unset($UsersResults);
    unset($UsersResult);

    mysql_close($DBConRead);

    #Check to see if this is a New User Submission
    if(isset($CleanFirstName) && isset($CleanUserID)) {
        #Verify that the UserID does not already exist
        if(!in_array($CleanUserID, $UserIDs)) {
            if($_POST['Password'] == $_POST['VerifyPassword']) {
                #Generate Password and Salt
                $PassSalts = PasswordSalt($_POST['Password']);
                $DBConAdmin = SQLConnection('UserIDSQLAdmin', 
                                                'PasswordSQLAdmin',
                                                'Monitoring');

                $UserInsertQuery = "INSERT
                                      INTO tblWebAuthUsers (
                                          FirstName
                                        , LastName
                                        , UserID
                                        , Password
                                        , Salt
                                        , EMailAddress
                                        , UserActive
                                        , DateStamp
                                      )
                                      VALUES (
                                          '{$CleanFirstName}'
                                        , '{$CleanLastName}'
                                        , '{$CleanUserID}'
                                        , '{$PassSalts[0]}'
                                        , '{$PassSalts[1]}'
                                        , '{$CleanEMailAddress}'
                                        , 1
                                        , CURDATE()
                                      )";
                #Insert into the DB
                $UserInsertResults = mysql_query($UserInsertQuery, $DBConAdmin);
                echo '<br>' . $UserInsertResults . '<br>';

                $GroupInsertQuery = "INSERT
                                       INTO tblWebAuthUserGroup (
                                           UserID
                                         , MonGroup
                                         , DateStamp
                                       )
                                       VALUES (
                                           '{$CleanUserID}'
                                         , '{$CleanMonGroup}'
                                         , CURDATE()
                                       )";
                #Insert into the DB
                #mysql_query($GroupInsertQuery, $DBConAdmin);
                echo '<br>' . $GroupInsertQuery . '<br>';

                print 'Your new user has been successfully created<br>';

                #Clear Variables
                unset($CleanEMailAddress);
                unset($CleanMonGroup);
                unset($CleanFirstName);
                unset($CleanLastName);
                unset($CleanUserID);
                unset($UserIDs);
                unset($UserGroups);
                mysql_close($DBConAdmin);
            }
            else {
                print 'Your passwords do not match<br>';
                print 'Please go back and try again<br>';
            }
        }
        else {
            print 'Your UserID already exists<br>';
        }
        unset($CleanEMailAddress);
        unset($CleanMonGroup);
        unset($CleanFirstName);
        unset($CleanLastName);
        unset($CleanUserID);
        unset($UserIDs);
        unset($UserGroups);
    }
    #Check to see if this is a new group submission
    if(isset($CleanMonGroup) && isset($CleanVerifyMonGroup)) {
        #Verify the group does not already exist
        if(!in_array($CleanMonGroup, $UserGroups)) {
            #Check to see that the Group Names match
            if($CleanMonGroup == $CleanVerifyMonGroup) {
                $DBConAdmin = SQLConnection('UserIDSQLAdmin', 
                                                'PasswordSQLAdmin',
                                                'Monitoring');
                $NewGroupInsert = "INSERT 
                                     INTO tblWebAuthUserGroup (
                                         MonGroup
                                       , DateStamp
                                     )
                                     VALUES (
                                         '{$CleanMonGroup}'
                                       , CURDATE()
                                     )";
                #Insert into the DB
                mysql_query($NewGroupInsert, $DBConAdmin);

                print 'Your new group has been successfully created<br>';

                unset($NewGroupInsert);
                mysql_close($DBConAdmin);
            }
            else {
                print 'Your Group Names do not match<br>';
                print 'Please go back and try again<br>';
            }
        }
        else {
            print 'Your Group already exists<br>';
        }
        unset($CleanMonGroup);
        unset($CleanVerifyMonGroup);
        unset($UserIDs);
        unset($UserGroups);
    }
    #Check to see if it is a password change or a group change
    if(isset($CleanMonUserID)) {
        #Verify that the UserID already exists in the DB
        if(in_array($CleanMonUserID, $UserIDs)) {
            #Check to see if there is a password reset
            if(strLen($_Post['Password']) > 1) {
                #Verify that the password match
                if($_POST['Password'] == $_POST['VerifyPassword']) {
                    #Generate Password and Salt
                    $PassSalts = PasswordSalt($_POST['Password']);
                    $DBConAdmin = SQLConnection('UserIDSQLAdmin', 
                                                'PasswordSQLAdmin',
                                                'Monitoring');
                    $PasswordUpdateQuery = "UPDATE
                                              tblWebAuthUsers
                                            SET
                                                Password = '{$PassSalts[0]}'
                                              , Salt = '{$PassSalts[1]}'
                                              , DateStamp = CURDATE()
                                            WHERE
                                              UserID = '{$CleanMonUserID}'
                                            ";
                    #Insert into the DB
                    mysql_query($PasswordUpdateQuery, $DBConAdmin);

                    print 'Your password has been successfully updated<br>';
                    unset($PassSalts);
                    unset($PasswordUpdateQuery);
                    mysql_close($DBConAdmin);
                }
                else {
                    print 'Your passwords do not match<br>';
                    print 'Please go back and try again<br>';
                }
            }
            #Check to see if a Group Change has been submitted
            if($CleanMonGroup != "No Change") {
               #Verify that the Group already exists
               if(in_array($CleanMonGroup, $UserGroups)) {
                    $DBConAdmin = SQLConnection('UserIDSQLAdmin', 
                                                'PasswordSQLAdmin',
                                                'Monitoring');
                    $GroupUpdateQuery = "UPDATE
                                           tblWebAuthUserGroup
                                         SET
                                             MonGroup = '{$CleanMonGroup}'
                                           , DateStamp = CURDATE()
                                         WHERE
                                           UserID = '{$CleanMonUserID}'
                                         ";
                    mysql_query($GroupUpdateQuery, $DBConAdmin);
                    print 'Your Group has been successfully updated<br>';

                    unset($GroupUpdateQuery);
                    mysql_close($DBConAdmin);
               }
            }
            #If the form is submitted blank then print no info
            if(strlen($_POST['Password']) < 2 &&
               $CleanMonGroup == "No Change") {
                   print 'No password or group change submitted<br>';
                   print 'Please go back and try again<br>';
            }
            unset($UserIDs);
            unset($UserGroups);
        }
    }
?>
</body>
</html>

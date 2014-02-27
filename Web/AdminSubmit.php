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

    $GroupQuery = "SELECT
                      DISTINCT(tblWebAuthUserGroup.MonGroup)
                    FROM tblWebAuthUserGroup";
    $GroupResults = SQLQuery('Monitoring', $GroupQuery, 'Read');
    foreach($GroupResults[1] as $GroupResult) {
        $UserGroups[] = $GroupResult['MonGroup'];
    }

    unset($GroupQuery);
    unset($GroupResult);

    $UserQuery = "SELECT
                     DISTINCT(tblWebAuthUsers.UserID)
                   FROM tblWebAuthUsers";
    $UserResults = SQLQuery('Monitoring', $UserQuery, 'Read');
    foreach($UserResults[1] as $UserResult) {
        $UserIDs[] = $UserResult['UserID'];
    } 

    unset($UserQuery);
    unset($UserResult);

    SQLClose($UserResults[0]);

    #Check to see if this is a New User Submission
    if(isset($CleanFirstName) && isset($CleanUserID)) {
        #Verify that the UserID does not already exist
        if(!in_array($CleanUserID, $UserIDs)) {
            if($_POST['Password'] == $_POST['VerifyPassword']) {
                #Generate Password and Salt
                $PassSalts = PasswordSalt($_POST['Password']);

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
                $UserInsertResults = SQLQuery('Monitoring',
                                              $UserInsertQuery, 'Admin');


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
                $GroupInsertResults = SQLQuery('Monitoring', 
                                               $GroupInsertQuery, 'Admin');

                print 'Your new user has been successfully created<br>';

                #Clear Variables
                unset($CleanEMailAddress);
                unset($CleanMonGroup);
                unset($CleanFirstName);
                unset($CleanLastName);
                unset($CleanUserID);
                unset($UserIDs);
                unset($UserGroups);
                unset($UserInsertQuery);
                unset($GroupInsertQuery);
                SQLClose($GroupInsertResults[0]);
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
                $NewGroupResults = SQLQuery('Monitoring', 
                                            $NewGroupInsert, 'Admin');

                print 'Your new group has been successfully created<br>';

                unset($NewGroupInsert);
                SQLClose($NewGroupResults[0]);
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
                    $PasswordUpdateResults = SQLQuery('Monitoring', 
                                                      $PasswordUpdateQuery,
                                                      'Admin');

                    print 'Your password has been successfully updated<br>';
                    unset($PassSalts);
                    unset($PasswordUpdateQuery);
                    SQLClose($PasswordUpdateResults[0]);
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
                    $GroupUpdateQuery = "UPDATE
                                           tblWebAuthUserGroup
                                         SET
                                             MonGroup = '{$CleanMonGroup}'
                                           , DateStamp = CURDATE()
                                         WHERE
                                           UserID = '{$CleanMonUserID}'
                                         ";
                    mysql_query($GroupUpdateQuery, $DBConAdmin);
                    $GroupUpdateResults = SQLQuery('Monitoring', 
                                                   $GroupUpdateQuery,
                                                   'Admin');
                    print 'Your Group has been successfully updated<br>';

                    unset($GroupUpdateQuery);
                    SQLClose($GroupUpdateResults[0]);
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

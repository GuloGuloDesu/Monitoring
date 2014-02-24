<?php
    #Include Header information, this includes layout, and DB Connections
    include 'Includes/Header.php';

    #Create UserID and Group Arrays
    $UserIDs = array();
    $UserGroups = array(); 

    #Connect to the SQL Database and pull the results
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
?>

        <div id="BlueBoxForm">
            <h2>Create User</h2>
            <form 
                id="CreateUser" name="CreateUser" action="AdminSubmit.php"
                 method="post">
            <fieldset>
                <p>
                    <label for="FirstName">
                        First Name:
                    </label>
                    <br>
                    <input
                         id="FirstName" type="text" name="FirstName"
                         class="text" placeholder="First Name" required>
                </p>
                <p>
                    <label for="UserID">
                        User Name:
                    </label>
                    <br>
                    <input
                        id="UserID" type="text" name="UserID"
                        class="text" placeholder="User Name" required>
                </p>
                <p>
                    <label for="Password">
                        Password:
                    </label>
                    <br>
                    <input
                        id="Password" type="password" name="Password"
                        class="text" placeholder="Password" required>
                </p>
                <p>
                    <label for="VerifyPassword">
                        Verify Password:
                    </label>
                    <br>
                    <input
                        id="VerifyPassword" type="password"
                        name="VerifyPassword"
                        class="text" placeholder="Verify Password" required>
                </p>
                <p>
                    <label for="EMailAddress">
                        E-mail Address:
                    </label>
                    <br>
                    <input
                        id="EMailAddress" type="text" name="EMailAddress"
                        class="text" placeholder="JoeBob@BillyBob.com"
                        required>
                </p>
                <p>
                    <label for="UserGroups">
                        User Groups:
                    </label>
                    <br>
                    <select id="UserGroups" name="UserGroups">
                        <?php
                            #Loop through all of the User Groups
                            foreach($UserGroups as $UserGroup) {
                                echo "<option> {$UserGroup} </option>";
                            }
                            unset($UserGroup);
                        ?>
                    </select>
                </p>
                <p>
                    <input id="Button1" type="submit" value="Create User">
                </p>
            </fieldset>
        </form>
    </div>
    <br>
    <br>
    <div id="BlueBoxForm">
        <h2>Create Group</h2>
        <form
            id="CreateGroup" name="CreateGroup" action="AdminSubmit.php"
            method="post">
            <fieldset>
                <p>
                    <label for="UserGroups">
                        User Group:
                    </label>
                    <br>
                    <input
                        id="UserGroups" type="text" name="UserGroups"
                        class="text" placeholder="User Group Name" required>
                </p>
                <p>
                    <label for="VerifyUserGroups">
                        Verify User Group:
                    </label>
                    <br>
                    <input
                        id="VerifyUserGroups" type="text"
                        name="VerifyUserGroups" class="text"
                        placeholder="Verify User Group" required>
                </p>
                <p>
                    <input id="Button1" type="submit" value="Create Group">
                </p>
            </fieldset>
        </form>
    </div>
    <br>
    <br>
    <div id="BlueBoxForm">
       <h2>Change Password or User Group</h2>
        <form
            id="ChangeUser" name="ChangeUser" action="AdminSubmit.php"
            method="post">
            <fieldset>
                <p>
                    <label for="UserID">
                        UserID:
                    </label>
                    <br>
                    <select id="UserID" name="UserID">
                        <?php
                            #Loop through all of the User IDs
                            foreach($UserIDs as $UserID) {
                               print "<option> {$UserID} </option>";
                            }
                            unset($UserID);
                            unset($UserIDs); 
                        ?>
                    </select>
                </p>
                <p>
                    <label for="Password">
                        Password:
                    </label>
                    <br>
                    <input
                        id="Password" type="password" name="Password"
                        class="text" placeholder="Password">
                </p>
                <p>
                    <label for="VerifyPassword">
                        VerifyPassword:
                    </label>
                    <br>
                    <input
                        id="VerifyPassword" type="password"
                        name="VerifyPassword" class="text"
                        placeholder="Verify Password">
                </p>
                <p>
                    <label for="UserGroups">
                        User Groups:
                    </label>
                    <br>
                    <select id="UserGroups" name="UserGroups">
                        <option selected> No Change </option>
                        <?php
                            #Loop through all of the User Groups
                            foreach($UserGroups as $UserGroup) {
                                echo "<option> {$UserGroup} </option>";
                            }
                            unset($UserGroups);
                            unset($UserGroup);
                        ?>
                    </select>
                </p>
                <p>
                    <input id="Button1" type="submit" value="Change User">
                </p>
            </fieldset>
        </form>
    </div>
</body>
</html>


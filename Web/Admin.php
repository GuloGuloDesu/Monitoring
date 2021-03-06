<?php
    #Include Header information, this includes layout, and DB Connections
    include 'Includes/Header.php';

    #Create UserID and Group Arrays
    $UserIDs = array();
    $UserGroups = array(); 

    #Connect to the SQL Database and pull the results
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
                    <label for="LastName">
                        Last Name:
                    </label>
                    <br>
                    <input
                         id="LastName" type="text" name="LastName"
                         class="text" placeholder="Last Name" required>
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
                    <label for="MonGroup">
                        User Groups:
                    </label>
                    <br>
                    <select id="MonGroup" name="MonGroup">
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
                    <label for="MonGroup">
                        User Group:
                    </label>
                    <br>
                    <input
                        id="MonGroup" type="text" name="MonGroup"
                        class="text" placeholder="User Group Name" required>
                </p>
                <p>
                    <label for="VerifyMonGroup">
                        Verify User Group:
                    </label>
                    <br>
                    <input
                        id="VerifyMonGroup" type="text"
                        name="VerifyMonGroup" class="text"
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
                    <label for="MonUserID">
                        UserID:
                    </label>
                    <br>
                    <select id="MonUserID" name="MonUserID">
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
                    <label for="MonGroup">
                        User Groups:
                    </label>
                    <br>
                    <select id="MonGroup" name="MonGroup">
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


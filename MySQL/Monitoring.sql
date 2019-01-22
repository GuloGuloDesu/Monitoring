/* Gulo's idempotent Monitoring Database Script

Example Debug Query:
    SELECT @query AS 'Debug:';

/* Create the Monitoring Database */
CREATE DATABASE IF NOT EXISTS Monitoring;
USE Monitoring;

/* Check for Procedures and Functions, if they exist delete them */
DROP PROCEDURE IF EXISTS Monitoring_Change;

DELIMITER ;;

/* Stored Procedure for building / updating tables */
CREATE PROCEDURE Monitoring_Change (IN tbl VARCHAR(32), IN query VARCHAR(10000))
BEGIN
    /* Check to see if the table exists */
    IF EXISTS(SELECT table_name
        FROM information_schema.tables
        WHERE information_schema.tables.table_schema = 'Monitoring'
          AND information_schema.tables.table_name = tbl)
    THEN
        /* Create the temp table variable */
        SET @temp_table = CONCAT(tbl, 'Temp');

        /* Delete the temp table if it exists */
        SET @drop_temp = CONCAT('DROP TABLE IF EXISTS ', @temp_table);
        PREPARE stmt_drop_table FROM @drop_temp;
        EXECUTE stmt_drop_table;
        DEALLOCATE PREPARE stmt_drop_table;

        /* Create the temp table based off the primary table */
        SET @create_temp = CONCAT('CREATE TABLE ', @temp_table, ' LIKE ', tbl);
        PREPARE stmt_create_temp FROM @create_temp;
        EXECUTE stmt_create_temp;
        DEALLOCATE PREPARE stmt_create_temp;

        /* Copy all the records from the primary table to the temp table */
        SET @copy_table = CONCAT('INSERT ', @temp_table, ' SELECT * FROM ', tbl);
        PREPARE stmt_copy_table FROM @copy_table;
        EXECUTE stmt_copy_table;
        DEALLOCATE PREPARE stmt_copy_table;

        /* Delete the primary table */
        SET @drop_primary = CONCAT('DROP TABLE ', tbl);
        PREPARE stmt_drop_primary FROM @drop_primary;
        EXECUTE stmt_drop_primary;
        DEALLOCATE PREPARE stmt_drop_primary;

        /* Run the Create table query */
        SET @create_query = CONCAT(query);
        PREPARE stmt_create_primary FROM @create_query;
        EXECUTE stmt_create_primary;
        DEALLOCATE PREPARE stmt_create_primary;

        /* Pull a list of all of the columns from the temp table */
        SELECT GROUP_CONCAT(column_name)
            FROM information_schema.columns
            WHERE information_schema.columns.table_name = @temp_table
            INTO @columns_temp;
        /* Pull a list of all of the columns from the primary table */
        SELECT GROUP_CONCAT(column_name)
            FROM information_schema.columns
            WHERE information_schema.columns.table_name = tbl
            INTO @columns_primary;
        /* Count all of the temp table columns */
        SELECT 
            (LENGTH(@columns_temp) 
            - LENGTH(REPLACE(@columns_temp, ',', '')) + 1)
            INTO @columns_temp_count;
        /* Count all of the primary table columns */
        SELECT 
            (LENGTH(@columns_primary) 
            - LENGTH(REPLACE(@columns_primary, ',', '')) + 1)
            INTO @columns_primary_count;

        /* Compare the column counts of primary and temp tables */
        IF (@columns_temp_count < @columns_primary_count)
        THEN
            /* If primary table has more columns use temp table as the formatter */
            SET @copy_back = CONCAT('INSERT INTO ', tbl, '(', @columns_temp, 
                    ') SELECT ', @columns_temp, ' FROM ', @temp_table);
        ELSE
            /* Else use the temp table as the formatter */
            SET @copy_back = CONCAT('INSERT INTO ', tbl, '(', @columns_primary, 
                    ') SELECT ', @columns_primary, ' FROM ', @temp_table);
        END IF;
        SELECT @copy_back AS '\n';
        /* Copy the data back to the primary table */
        PREPARE stmt_copy_back FROM @copy_back;
        EXECUTE stmt_copy_back;
        DEALLOCATE PREPARE stmt_copy_back;

        /* Delete the temp table */
        SET @drop_temp = CONCAT('DROP TABLE ', @temp_table);
        PREPARE stmt_drop_temp FROM @drop_temp;
        EXECUTE stmt_drop_temp;
        DEALLOCATE PREPARE stmt_drop_temp;

    /* If table doesn't exist, build the table */
    ELSE
        SET @create_query = CONCAT(query);
        PREPARE stmt_create_primary FROM @create_query;
        EXECUTE stmt_create_primary;
        DEALLOCATE PREPARE stmt_create_primary;
        END IF;

END;;
DELIMITER ;

SET @tblDocIPQuery = 
    'CREATE TABLE tblDocIP
    (
        pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        DeviceName VARCHAR(64),
        IPAddress VARCHAR(64),
        MACAddress VARCHAR(32),
        DateStamp DATETIME
    )';
CALL Monitoring_Change('tblDocIP', @tblDocIPQuery);

SET @tblDocOSQuery =
    'CREATE TABLE tblDocOS
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            DeviceName VARCHAR(64),
            OS VARCHAR(64),
            ScanType VARCHAR(8),
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblDocOS', @tblDocOSQuery);

SET @tblDocScriptsQuery = 
    'CREATE TABLE tblDocScripts
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            ScriptName VARCHAR(64),
            RunTime VARCHAR(32),
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblDocScripts', @tblDocScriptsQuery);

SET @tblDocLogonQuery = 
    'CREATE TABLE tblDocLogon
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            DeviceName VARCHAR(64),
            UserID VARCHAR(64),
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblDocLogon', @tblDocLogonQuery);

SET @tblDocFileHashQuery = 
    'CREATE TABLE tblDocFileHash
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            DeviceName VARCHAR(64),
            FilePath VARCHAR(10000),
            FileName VARCHAR(1000), 
            FileMD5 VARCHAR(32),
            DateCreated DATETIME,
            DateModified DATETIME,
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblDocFileHash', @tblDocFileHashQuery);

SET @tblWebAuthUsersQuery = 
    'CREATE TABLE tblWebAuthUsers
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            FirstName VARCHAR(64),
            LastName VARCHAR(64), 
            UserID VARCHAR(64), 
            Password VARCHAR(256), 
            Salt VARCHAR(256), 
            EMailAddress VARCHAR(128), 
            UserActive SMALLINT, 
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblWebAuthUsers', @tblWebAuthUsersQuery);

SET @tblWebAuthLogonLogQuery = 
    'CREATE TABLE tblWebAuthLogonLog
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            UserID VARCHAR(64), 
            FailedLogon SMALLINT, 
            TimeAttempt DATETIME, 
            IPAddress VARCHAR(64), 
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblWebAuthLogonLog', @tblWebAuthLogonLogQuery);

SET @tblWebAuthUserGroupQuery =
    'CREATE TABLE tblWebAuthUserGroup
        (
            pk BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            UserID VARCHAR(64), 
            MonGroup VARCHAR(64), 
            DateStamp DATETIME
        )';
CALL Monitoring_Change('tblWebAuthUserGroup', @tblWebAuthUserGroupQuery);

CREATE DATABASE Monitoring;

USE Monitoring;

CREATE TABLE tblDocIP
(
    pk bigint not null auto_increment primary key,
    DeviceName varchar(64),
    IPAddress varchar(64),
    MACAddress varchar(32),
    DateStamp datetime
);

CREATE TABLE tblDocOS
(
    pk bigint not null auto_increment primary key,
    DeviceName varchar(64), 
    OS varchar(64), 
    ScanType varchar(8), 
    DateStamp datetime
);

CREATE TABLE tblDocScripts
(
    pk bigint not null auto_increment primary key, 
    ScriptName varchar(64), 
    RunTime varchar(32), 
    DateStamp datetime
);

CREATE TABLE tblDocLogon
(
    pk bigint not null auto_increment primary key,
    DeviceName varchar(64), 
    UserID varchar(64), 
    DateStamp datetime
);

CREATE TABLE tblDocFileHash
(
    pk bigint not null auto_increment primary key,
    DeviceName varchar(64),
    FilePath varchar(10000),
    FileName varchar(1000),
    FileMD5 varchar(32),
    DateCreated datetime,
    DateModified datetime,
    DateStamp datetime
);

CREATE TABLE tblWebAuthUsers
(
            pk bigint not null auto_increment primary key,
            FirstName varchar(64),
            LastName varchar(64), 
            UserID varchar(64), 
            Password varchar(256), 
            Salt varchar(256), 
            EMailAddress varchar(128), 
            UserActive smallint, 
            DateStamp date
);
CREATE TABLE tblWebAuthLogonLog
(
            pk bigint not null auto_increment primary key, 
            UserID varchar(64), 
            FailedLogon smallint, 
            TimeAttempt datetime, 
            IPAddress varchar(64), 
            DateStamp date
);
CREATE TABLE tblWebAuthUserGroup
(
            pk bigint not null auto_increment primary key, 
            UserID varchar(64), 
            MonGroup varchar(64), 
            DateStamp date
);

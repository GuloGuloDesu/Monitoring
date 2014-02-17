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

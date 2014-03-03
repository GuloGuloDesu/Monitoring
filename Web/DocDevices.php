<?php
    include 'Includes/Header.php';

    $DeviceListQuery = "SELECT DISTINCT
                            tblDocIP.DeviceName
                          , tblDocIP.IPAddress
                          , tblDocIP.MACAddress
                          , tblDocIP.DateStamp
                        FROM tblDocIP
                        WHERE
                          tblDocIP.DateStamp = (
                            SELECT MAX(DateStamp) FROM tblDocIP
                          )
                        ORDER BY
                          tblDocIP.DeviceName";
    $DeviceListResults = SQLQuery('Monitoring', $DeviceListQuery, 'Read');

    $Fields = array(
                      'DeviceName' => 'Device Name' 
                    , 'IPAddress' => 'IP Address'
                    , 'MACAddress' => 'MAC Address'
                    , 'DateStamp' => 'Date Stamp'
              );

    HTMLTable($Fields, $DeviceListResults[1]);
    SQLClose($DeviceListResults[0]);
?>
    </body>
</html>

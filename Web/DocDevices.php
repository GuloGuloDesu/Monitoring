<?php
    include 'Includes/Header.php';
?>
        <p>
            <table>
                <thead>
                    <tr>
                        <th>
                            Device Name
                        </th>
                        <th>
                            IP Address
                        </th>
                        <th>
                            MAC Address
                        </th>
                        <th>
                            Date Stamp
                        </th>
                    </tr>
                </thead>
                <tbody>
<?php
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

    foreach($DeviceListResults[1] as $DeviceListResult) {
        $Color++;
        print str_repeat($Tab, 5) . 
            "<tr class='color" . ($Color & 1) . "'>\n";
        print str_repeat($Tab, 6) . '<td>';
        print str_repeat($Tab, 7) . $DeviceListResult['DeviceName'] . "\n";
        print str_repeat($Tab, 6) . "</td>\n";
        print str_repeat($Tab, 6) . "<td>\n";
        print str_repeat($Tab, 7) . $DeviceListResult['IPAddress'] . "\n";
        print str_repeat($Tab, 6) . "</td>\n";
        print str_repeat($Tab, 6) . "<td>\n";
        print str_repeat($Tab, 7) . $DeviceListResult['MACAddress'] . "\n";
        print str_repeat($Tab, 6) . "</td>\n";
        print str_repeat($Tab, 6) . "<td>\n";
        print str_repeat($Tab, 7) . $DeviceListResult['DateStamp'] . "\n";
        print str_repeat($Tab, 6) . "</td>\n";
        print str_repeat($Tab, 5) . "</tr>\n";
    }
    unset($DeviceListQuery);
    unset($DeviceListResult);
    SQLClose($DeviceListResults[0]);
?>
                </tbody>
            </table>
        </p>
    </body>
</html>

## Usage

The first script getPrimeInfraDevices.py, performs device list extraction from Prime Infrastructure server(s) and imports them into the MySQL database, 'inventory' table.
The second script getDNACDevices.py, performs device list extraction from DNA Center server(s) and imports them into the MySQL database, 'inventory' table.
The third script getACIAPICDevices.py, performs device list extraction from ACI APIC controller(s) and imports them into the MySQL database, 'inventory' table.
The forth script PingandUpdateInventory.py, extracts the device list from the MySQL database and submits the list of devices to fping.  It also collects the results and updates the database.
The fifth script CreateAvailabilityDashboard.py, creates the dashboard from the MySQL database results.


Run the following Python scripts at least once manually or schedule in a crontab, as needed, based on your rate of network device change.  These scripts extract the network inventory and put them into the MySQL database.

    $ python getPrimeInfraDevices.py
    $ python getDNACDevices.py
    $ python getACIAPICDevices.py

Run the following Python scripts in a crontab, based on how often you'd like to update the dashboard - every 5 minutes, every minute, etc.

    $ python PingandUpdateInventory.py && python CreateAvailabilityDashboard.py

A standard crontab model could be:

    $ crontab -e
    #minute hour day_of_month month day_of_week command_to_run
    #Example of running every two minutes, every day
    */2 * * * * python PingandUpdateInventory.py  && python CreateAvailabilityDashboard.py


If you are extracting devices from your management tools/controllers that you can't or don't want to ping for availability, use the mysql shell to update the 'inventory' table.  Specifically, set the do_ping column value to 0 (zero) and it will not be pinged.

<kbd>

    $ mysql

    mysql> use devnet_dashboards;

    Reading table information for completion of table and column names
    You can turn off this feature to get a quicker startup with -A

    Database changed
    mysql> update inventory
      -> SET do_ping = 0
      -> WHERE mgmt_ip_address = '30.1.1.1';
    Query OK, 1 row affected (0.00 sec)
    Rows matched: 1  Changed: 1  Warnings: 0

    mysql>  
</kbd>

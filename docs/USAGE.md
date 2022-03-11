## Usage

The pptx2dashboard.py is the main and only Python script for this project.
Make sure the (installation instructions)[INSTALLATION.md] are reviewed 
and the [env.yaml](../src/env.yaml) file is modified, if necessary.

Start by developing a Powerpoint file to suit your dashboard/visualization 
requirements.  Use text placeholders with unique variable names where 
dynamic data should be placed. E.g. Total: ##VAR-TOTAL
See [Powerpoint-Example](example.pptx) for an example.
Note: Ensure the variable placeholders are truly unique and aren't a subset 
string of any other, as string replacements are being done.
- Good choices: ##VAR-TOTAL, ##VAR-FLOOR1
- Bad choices: ##FLOOR, ##FLOOR1TOTAL [FLOOR is inside FLOOR1TOTAL]

Save the .pptx file to the project directory.

Use other scripts or orchestration methods to extract the instrumentation/
telemetry desired (via SNMP, REST APIs, automated CLI capture, etc). Define 
a mapping of the placeholder variable to the dynamic value as key, value 
entries in a JSON file.
See [variables.json](../src/variables.json) for an example.

Save the JSON file to the project directory.

Execute the conversion as such:

    $ python pptx2dashboard.py --webName MyDashboard template-dashboard.pptx variables.json

A dashboard will be created and hosted on the local Apache webserver as 
http://<IP>/MyDashboard.html

Run the Python script in a periodic scheudule with a crontab, as needed, 
based on your desire to update the dashboard.
A standard crontab model could be:

    $ crontab -e
    #minute hour day_of_month month day_of_week command_to_run
    #Example of running every five minutes, every day
    */5 * * * * python pptx2dashboard.py --webName MyDashboard template-dashboard.pptx variables.json
    
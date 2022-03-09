## Configuration

An 'optionsconfig.yaml' file defines the Prime Infrastructure, DNA Center and ACI APIC controller IP addresses and authorized API user credentials.  The supplied optionsconfig.yaml file is currently pointing to DevNet Always-On Sandbox systems.  Please note, the devices extracted from those inventories are NOT generally reachable from the public Internet, so your dashboards will have a lot of RED until you reconfigure it to point to EMS/controllers that have access to your network devices.

Edit the [src/optionsconfig.yaml](./src/optionsconfig.yaml) file to suit your environment's inventory sources.  Multiple entries are allowed.  Comment out entries that are not currently used, preserving them for future options.  Enter each server's hostname/IP Address, authorized API username and password and any other parameters of interest.

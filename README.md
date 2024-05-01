# wirelesswizard

## Description
WirelessWizard allows you to use your wireless interface using python.

## Installation
You can install WirelessWizard using `pip3`:
```bash
$ pip3 install wirelesswizard
```

## Basic Usage
### 1. Listing your wireless interfaces
```python
import wirelesswizard

# get a list of the currently available wireless interface in your system
interfaces = wirelesswizard.get_wireless_interfaces()

# selecting an interface
interface_0 = interfaces[0]

# showing information of your wireless interface
interface_0.show_info()

# you can use the attributes of the wireless interface too
print(interface_0.name)
```
### 2. Scanning networks
```python
import wirelesswizard

# selecting an interface
interfaces = wirelesswizard.get_wireless_interfaces()
interface = interfaces[0]

# scanning networks
interface.scan_networks()  

# Getting scan results
scan_result = interface.get_last_scan()

# showing scan result
print(scan_result)

# you can also get the scan result in different formats. 
# ["raw","table","html","json"]
scan_result = interface.get_last_scan(format="json")

# the history of network scans
print(interface.scan_history)

# select the last scan history (list of NetworkInfo objects)
interface.scan_history[0]
```
### 3. Setting monitor mode 
```python
import wirelesswizard

# selecting an interface
interfaces = wirelesswizard.get_wireless_interfaces()
interface = interfaces[0]

# changing interface to monitor mode
interface.change_mode("monitor")
```
### 4. Changing state
```python
import wirelesswizard

# selecting an interface
interfaces = wirelesswizard.get_wireless_interfaces()
interface = interfaces[0]

# executing ip link set <iface> down
interface.change_state("down")

# executing ip link set <iface> up
interface.change_state("up")
```
### 5. Changing
```python
import wirelesswizard

# selecting an interface
interfaces = wirelesswizard.get_wireless_interfaces()
interface = interfaces[0]

# changing to channel 11
interface.change_channel(11)
```
## License
This proyect is under GPL v3 license.

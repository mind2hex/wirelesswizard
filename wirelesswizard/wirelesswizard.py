#!/usr/bin/env python3

"""
WirelessWizard.py

This module allows you to manipulate wireless network interfaces using system commands.

Author: mind2hex <neodeus8@gmail.com>
"""

import subprocess
import pandas as pd
import re
import datetime
from os import listdir
from sys import platform
from time import sleep


class NetworkInfo:
    """
    NetworkInfo as its name suggest, is a class to store information about networks scanned using a wireless interface.

    Attributes:
        ssid (str): Name of the wireless network.
        bssid (str): Mac address of the wireless network.
        channel (int): Channel of the wireless network (calculated using self.calculate_channel(frequency) method)
        frequency (int): Frequency of the wireless network in MHz.
        signal (float): Signal power in dbm.
        manufacturer (str): ...
        model_number (str): ...
        serial_number (str): ...
        enc (str): Encryption used for the wireless network (WPA1|WPA2|...).
        cipher (str): Cipher used for the wireless network.
    """

    # this attribute contain all other attribute names
    current_fields = [
        "ssid",
        "bssid",
        "channel",
        "frequency",
        "signal",
        "manufacturer",
        "model_number",
        "serial_number",
        "enc",
        "cipher",
    ]

    def __init__(
        self,
        ssid: str,
        bssid: str,
        frequency: int,
        signal: str,
        manufacturer: str,
        model_number: str,
        serial_number: str,
        enc: str,
        cipher: str,
    ):
        self.ssid = ssid
        self.bssid = bssid
        self.channel = calculate_channel(frequency)
        self.frequency = frequency
        self.signal = signal
        self.manufacturer = manufacturer
        self.model_number = model_number
        self.serial_number = serial_number
        self.enc = enc
        self.cipher = cipher

    def get_info(self):
        """
        Returns:
            dict: dictionary containing every attribute with his value as key:value.
        """

        info = dict()
        for field in self.current_fields:
            info[field] = getattr(self, field)

        return info


class WirelessInterface:
    """
    This class Represents a wireless network interface.

    Attributes: [attributes updated using self.update_interface_info() method]
        name (str): 
            Wireless interface name.

        state (str): 
            Actual state of the interface [see Operational States ].

        phy  (int): 
            Phy index used by `iw` command.

        addr (str): 
            Mac address of the wireless interface.

        mode (str): 
            Operational mode of the wireless interface. [see Operational Modes]

        flags (list): 
            Operational flags of the wireless interface. [See Operational Flags]

        channel (int): 
            Current channel of the wireless interface.

        frequency (int): 
            Current frequency of the wireless interface in MHz.

        width (int): 
            Current operational width of the wireless interface in MHz.

        txpower (float): 
            Transmission power of the wireless interface in dBm.

        driver (str): 
            Current driver in use by the wireless interface.

        chipset (str): 
            Current chipset of the wireless interface.

        capabilities (dict): 
            Dictionary with capabilities information of the wireless interface.

        last_scan_result (list): 
            This list stores the result of the last call to scan_networks() method.

        scan_history (list): 
            This list stores all the scans during runtime.

    Operational Modes:
        ap: 
            Acess Point mode, used to transform our wireless device in an AP.

        managed: 
            Used for connecting to home, enterprise, or public Wi-Fi networks.

        ibss: 
            Used for setting up peer-to-peer wireless networks directly between devices.

        monitor: 
            Used for conducting security audits, wireless network debugging, and traffic analysis.

        mesh: 
            Used in large-scale wireless network applications such as community networks, sensor networks, and emergency infrastructure networks.

        wds: 
            Used for creating long-range wireless links between remote locations, such as buildings or campuses.

        p2p-client: 
            ...

        p2p-go: 
            ...

    Operational States:
        UP: 
            The interface is enabled. It means it is configured to send and receive data.

        DOWN: 
            The interface is disabled. Can't send or receive data.

        DORMANT: 
            The interface is enabled, but in wait mode for an external event to start data transmission.

    Operational Flags:
        ARP:
            Enables or disables the use of the ARP protocol on this interface. When ARP is enabled (on), the system can resolve
            IP addresses to MAC addresses on this network segment. When disabled (off), the interface will not use ARP, which might
            be useful in specific setups, such as when configuring a static ARP entry.

        DYNAMIC:
            Indicates if the interface has a dynamically assigned MAC address. When this flag is enabled (on),
            the MAC address can change, for instance, as a result of a driver operation or in response to
            specific network conditions. When disabled (off), the MAC address is static.

        MULTICAST:
            Enables or disables the reception of multicast packets on this interface. When enabled (on), the interface
            can receive packets sent to multicast addresses. Disabling it (off) prevents the interface from processing
            multicast traffic, which can reduce unnecessary processing for interfaces that do not need to participate
            in multicast communication.

        ALLMULTICAST:
            When this flag is enabled (on), the network interface enters a mode where it accepts all multicast packets,
            not just those addressed to multicast addresses the interface has explicitly joined.
            Useful for certain types of network monitoring or when acting as a multicast router.
            When disabled (off), the interface only accepts multicast traffic for groups it has joined.

        PROMISC:
            Enables or disables promiscuous mode on the interface. In promiscuous mode (on), the interface passes all traffic
            it receives to the CPU rather than just the traffic addressed to it, which is useful for network packet
            sniffing and analysis. When disabled (off), the interface filters out packets not addressed to it.

        TRAILERS:
            Refers to the use of trailer encapsulations on the interface, a feature that is now largely obsolete.
            Enabling trailers (on) historically was used to improve performance by allowing the payload of packets
            to be aligned with memory boundaries. Typically left disabled (off) in modern configurations as the technique
            is not widely supported or beneficial with current hardware.

        CARRIER:
            Reflects the presence of a physical link carrier. Manually enabling or disabling the carrier (on/off) is not
            common practice through ip link settings as it typically represents the actual physical state of the connection
            (e.g., whether a cable is plugged in and detected by the hardware).
    """

    operational_modes = [
        "ap",
        "managed",
        "ibss",
        "monitor",
        "mesh",
        "wds",
        "p2p-client",
        "p2p-go",
    ]

    operational_states = ["UP", "DOWN", "DORMANT"]

    operational_flags = [
        "ARP",
        "DYNAMIC",
        "MULTICAST",
        "ALLMULTICAST",
        "PROMISC",
        "TRAILERS",
        "CARRIER",
    ]

    def __init__(self, name: str, verbose=False):
        """construct function for WirelessInterface class.

        Args:
            name (str): name of the wireless interface.
            verbose (bool)
        """

        # see Attributes in the class docstring to get more info about attributes
        self.name = name
        self.state = "UNK"
        self.phy = "UNK"
        self.addr = "00:de:ad:be:ef:00"
        self.mode = "UNK"
        self.flags = list()
        self.channel = 0
        self.frequency = 0
        self.width = 0
        self.txpower = 0.0
        self.driver = "UNK"
        self.chipset = "UNK"
        self.capabilities = dict()
        self.last_scan_result = list()
        self.scan_history = list()

        # first call to update_interface_info()
        self.update_interface_info(verbose=verbose)

    def show_info(self):
        """show information recolected of the wireless interface.
        """
        for attribute in vars(self).keys():
            if isinstance(vars(self)[attribute], dict):
                print("[!] %15s:  "%(attribute))
                for key in vars(self)[attribute].keys():
                    print(f"\t\t {key}: ")
                    if isinstance(vars(self)[attribute][key], list):
                        for item in vars(self)[attribute][key]:
                            print(f"\t\t\t{item} ")
                    else:
                        print(f"\t\t\t{vars(self)[attribute][key]} ")
            else:
                print("[!] %15s: %s "%(attribute ,vars(self)[attribute]))

    def update_interface_info(self, verbose=False):
        """update/fill the  info of the current wireless interface object using its name

        This function simply calls the following commands:

        # to get general info about <iface>
        $ iw dev <iface> info

        # to get operational flags
        $ ip link show <iface>

        # to get driver
        $ cat /sys/class/net/<iface>/device/uevent

        # to get device capabilities
        $ iw list
        """
        if verbose:
            print("\n", "-" * 50, "INTERFACE INFO UPDATE REQUESTED")

        try:
            output = subprocess.check_output(["iw", "dev", self.name, "info"]).decode()
        except Exception as e:
            self.log(f"Unable to get interface information. {e}", True)
            exit(0)

        try:
            interface_state = subprocess.check_output(
                ["ip", "link", "show", self.name]
            ).decode()
        except Exception as e:
            self.log(f"unable to update wireless interface status. {e}", True)
            exit(0)

        self.log("Updating interface info: ", verbose)

        self.state = re.findall(
            f"state ({'|'.join(self.operational_states)})", interface_state
        )[0]
        self.log(f"\tSTATE: {self.state}", verbose)

        self.phy = re.findall("wiphy ([0-9]*)", output)[0]
        self.log(f"\tPHY: {self.phy}", verbose)

        self.addr = re.findall("addr (.*)", output)[0]
        self.log(f"\tADDR: {self.addr}", verbose)

        self.mode = re.findall("type (.*)", output)[0]
        self.log(f"\tMODE: {self.mode}", verbose)

        # if interface is down, channel is set to 0
        if self.state == "UP" or self.state == "DORMANT":
            self.channel = re.findall("channel ([0-9]*)", output)[0]
            self.frequency = re.findall("channel [0-9]* \(([0-9]*) MHz\)", output)[0]
            self.width = re.findall("width: ([0-9]*) MHz", output)[0]
        else:
            self.channel = 0
            self.frequency = 0
            self.width = 0

        self.log(f"\tCHANNEL: {self.channel}", verbose)
        self.log(f"\tFREQ: {self.frequency}", verbose)
        self.log(f"\tWIDTH: {self.width}", verbose)

        self.txpower = re.findall("txpower ([0-9\.]*) dBm", output)[0]
        self.log(f"\tTXPOWER: {self.txpower}", verbose)

        # extracting driver info
        with open(f"/sys/class/net/{self.name}/device/uevent", "r") as handler:
            output = handler.read()
            self.driver = re.findall("DRIVER=(.*)", output)[0]

        # extracting operational flags
        output = subprocess.check_output(["ip", "link", "show", self.name]).decode()
        self.flags = re.findall("\<(.*)\>", output)[0].split(",")

        # extracting capabilities info
        output = subprocess.check_output(["iw", "list"]).decode()
        output = output.split("Wiphy")
        output.pop(0)

        # updating capabilities
        if len(self.capabilities.keys()) == 0:
            capabilities = {}
            for interface_info in output:
                if re.search(f"phy{self.phy}", interface_info):
                    # supported ciphers
                    pattern = r"Supported Ciphers:(.*?)Available Antennas"
                    result = re.search(pattern, interface_info, re.DOTALL).group(1)
                    capabilities["ciphers"] = re.findall("\* ([0-9a-zA-Z\-]*)", result)

                    # available antennas
                    capabilities["antennas"] = re.findall(
                        "Available Antennas: (.*)", interface_info
                    )[0]

                    # supported modes
                    pattern = r"Supported interface modes:(.*?)Band"
                    result = re.search(pattern, interface_info, re.DOTALL).group(1)
                    capabilities["modes"] = [
                        mode.lower()
                        for mode in re.findall("\* ([0-9a-zA-Z\-]*)", result)
                    ]

                    # supported commands
                    pattern = r"Supported commands:(.*?)(software|WoWLAN)"
                    result = re.search(pattern, interface_info, re.DOTALL).group(1)
                    capabilities["commands"] = re.findall("\* ([0-9a-zA-Z\_]*)", result)

                    # TODO: extract more capabilities here

            self.capabilities = capabilities

    def change_mode(self, mode: str, verbose=False):
        """change the operational mode of the WirelessInterface.

        This function change the operational mode (if available and supported) of the
        network interface (WirelessInterface) using `iw` and `ip` command as follow:

        # to change mode, <iface> must be turned down
        $ sudo ip link <iface> down

        # changing the mode of <iface>
        $ sudo iw dev <iface> set type <mode>

        # turning up <iface>
        $ sudo ip link <iface> up

        Args:
            mode (str): the mode to change the interface. [See operational modes.]
            verbose (bool, optional): show verbose messages. Defaults to False.

        Raises:
            Exception: if mode not in self.operational_modes.
            Exception: if mode not in supported modes (self.capabilities["modes"]).
            Exception: if an error ocurred during the change process.
        """
        if verbose:
            print("\n", "-" * 50, "CHANGE MODE REQUESTED")

        if mode not in self.operational_modes:
            self.log(
                f"Invalid operational mode specified {mode}. Supported modes: {str(self.capabilities['modes'])}",
                verbose,
            )

        elif mode not in self.capabilities["modes"]:
            self.log(
                f"Mode {mode} not supported by the interface {self.name}. Supported modes {str(self.capabilities['modes'])}",
                verbose,
            )

        elif mode == self.mode:
            self.log(f"The wireless interface is already in {self.mode} mode", verbose)

        else:
            # setting down interface before changing mode
            self.log(f"Turning DOWN interface.", verbose)
            self.change_state("DOWN")

            self.log(f"Changing interface mode from {self.mode} to {mode}", verbose)
            try:
                # changing mode
                subprocess.check_call(
                    ["sudo", "iw", "dev", self.name, "set", "type", mode]
                )

            except Exception as e:
                self.log(f"Unable to change mode: {e}", True)

            self.log(f"Turning UP interface.", verbose)
            self.change_state("UP")

            self.log(f"Updating interface info.", verbose)
            self.update_interface_info()

    def change_state(self, new_state: str, verbose=False):
        """
        This function uses `ip link set <iface> [up|down|dormant...]` command to change state of the current wireless interface

        Args:
            new_status (str): New status to set interface. [see Operational States]
            verbose (bool, optional): show verbose messages. Defaults to False.
        """

        if verbose:
            print("\n", "-" * 50, "CHANGE STATE REQUESTED")

        # Unblocking wifi devices before changing state of the wireless interface
        self.log(
            f"Enabling wireless devices with `rfkill unblock wifi` command to change state",
            verbose,
        )
        subprocess.check_call(["sudo", "rfkill", "unblock", "wifi"])

        # changing state of the wireless interface
        self.log(f"Changing state from {self.state} to {new_state}", verbose)
        subprocess.check_call(
            ["sudo", "ip", "link", "set", self.name, new_state.lower()]
        )
        self.update_interface_info()

    def change_channel(self, channel: int, verbose=False):
        """Change the current channel of the wireless interface with a new channel

        This function change the channel of the wireless interface using the command:
        $ sudo iw dev <iface> set channel <channel>

        The process to change the channel of a wireless interface involves next steps:
            1. $ sudo ip link set <iface> down
            2. $ iw dev <iface> set type monitor
            3. $ sudo ip link set <iface> up
            4. $ iw dev <iface> set channel <channel>

        Args:
            channel (int): the new channel to change the interface
            verbose (bool, optional): show verbose messages. Defaults to False.

        Raises:
            Exception: if the interface is unable to change the channel.
        """

        if verbose:
            print("\n", "-" * 50, "CHANGE CHANNEL REQUESTED")
        
        if self.mode != "monitor":
            self.log(f"Changing mode from {self.mode} to monitor", verbose)
            self.change_mode("monitor")

        if self.state == "DOWN":
            self.log("Changing state to UP", verbose)
            self.change_state("UP")
        
        self.log(f"Changing interface channel to {channel}", verbose)

        try:
            subprocess.call(
                ["sudo", "iw", "dev", self.name, "set", "channel", str(channel)]
            ).decode()
        except Exception as e:
            self.log(f"unable to change channel {e}")

        # updating interface info after changing channel
        self.update_interface_info()

    def scan_networks(self, verbose=False):
        """scan_networks(self) scan networks with the specified wifi interface

        this method scan networks using command `$ iw dev {self.name} scan`  and store its result
        in self.last_scan_result using a list filled with NetworkInfo objects.

        Args:
            verbose (bool, optional): show verbose messages. Defaults to False.

        Example:
            self.last_scan_result = [NetworkInfo(), NetworkInfo(), ...]

        """

        if verbose:
            print("\n", "-" * 50, "NETWORK SCAN REQUESTED")

        self.log("Stopping ongoin network scans.", verbose)
        try:
            subprocess.check_call(["sudo", "iw", "dev", self.name, "scan", "abort"])
        except Exception as e:
            self.log(f"Unable to stop ongoin scan. {e}", True)

        if self.mode != "managed":
            self.log(
                f"Changing mode from {self.mode} to managed to be able to scan WiFi networks.",
                verbose,
            )
            self.change_mode("managed")

        self.change_state("UP")

        self.log("Scanning WiFi networks.", verbose)
        try:
            scan_result_raw = subprocess.check_output(
                ["sudo", "iw", "dev", self.name, "scan"]
            ).decode()
        except Exception as e:
            self.log(
                f"Interface {self.name} is currently unavailable or busy. {e}", True
            )
            exit(0)

        self.log(
            "Saving scan result. Use get_last_scan() method to get the scan results.",
            verbose,
        )
        scan_result_raw = scan_result_raw.split("\nBSS ")
        scan_result_raw.pop(0)

        scan_result = []
        for network_info in scan_result_raw:
            # extracting ssid info
            tmp = re.findall("SSID: (.*)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                ssid = tmp[0]
            else:
                ssid = "HIDDEN"

            # extracting bssid info
            tmp = re.findall(f"(.*)\(on {self.name}\)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                bssid = tmp[0]
            else:
                bssid = "00:00:00:00:00:00"

            # extracting frequency info
            tmp = re.findall(f"freq: (.*)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                frequency = int(tmp[0])
            else:
                frequency = 0

            # exctracting signal info
            tmp = re.findall("signal: (.*) dBm", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                signal = float(tmp[0])
            else:
                signal = 0.0

            # extracting manufacturer info
            tmp = re.findall("Manufacturer: (.*)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                manufacturer = tmp[0]
            else:
                manufacturer = "UNKNOWN"

            # extracting model_number info
            tmp = re.findall("Model Number: (.*)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                model_number = tmp[0]
            else:
                model_number = "unknown"

            # extracing serial_number info
            tmp = re.findall("Serial Number: (.*)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                serial_number = tmp[0]
            else:
                serial_number = "UNKNOWN"

            # extracing enc info
            if re.findall("Group cipher: (CCMP)", network_info):
                enc = "WPA2"
            else:
                enc = "WPA1"

            # extracting cipher info
            tmp = re.findall("Group cipher: (\w+)", network_info)
            if len(tmp) > 0 and len(tmp[0]) > 0:
                cipher = tmp[0]

            # appending NetowkrInfo into scan results
            scan_result.append(
                NetworkInfo(
                    ssid,
                    bssid,
                    frequency,
                    signal,
                    manufacturer,
                    model_number,
                    serial_number,
                    enc,
                    cipher,
                )
            )

        self.last_scan_result = scan_result
        self.scan_history.append(scan_result)

    def get_last_scan(self, format="raw", show=False):
        """returns the result from the last call to WirelessInterface.scan_network() method

        Args:
            format (str, optional): Specified format to return results. ["raw","table","html","json"].
            show (bool, optional): Print results in console before return. Defaults to False.

        Raises:
            KeyError: If invalid format specified.

        Returns:
            DataFrame: Dataframe containing the results of the wireless networks scan.
        """

        formats = ["raw", "table", "html", "json"]

        if format not in formats:
            raise KeyError(f"Invalid format specified {format}")

        networks_info = []
        for network in self.last_scan_result:
            networks_info.append(network.get_info())

        df = pd.DataFrame(networks_info, columns=NetworkInfo.current_fields)

        if format == "table":
            df = df.to_string(index=False)
        elif format == "html":
            df = df.to_html(index=False)
        elif format == "json":
            df = df.to_json(orient="records")

        if show == True:
            print(df)

        return df

    def log(self, msg: str, show=False):
        """
        Simply show log messages (print msg) if show is True

        Args:
            msg (_type_): The message to show.
            show (bool, optional): If True, then prints msg to terminal. Defaults to False.
        """
        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        log_msg = "[%-17s CH:%-3s STATE:%-6s MODE:%-10s][%s] " % (
            self.name,
            self.channel,
            self.state,
            self.mode,
            date,
        )
        log_msg += msg
        if show:
            print(log_msg)


def calculate_channel(frequency: int):
    """
    Returns the channel for the specified frequency in MHz.

    Args:
        freq (int): the frequency to calculate channel in MHz.

    Returns:
        int: the channel for the frequency specified.
    """

    # valid range for 2.4 GHz
    if 2400 <= frequency <= 2483.5:
        if frequency == 2484:
            return 14  # specific case for japan (channel 14)
        else:
            return (frequency - 2407) // 5

    # valid range for 5 GHz (generally from 5150 MHz to 5875 MHz)
    if 5150 <= frequency <= 5875:
        return (frequency - 5000) // 5

    return 0


def get_wireless_interfaces(verbose=False):
    """Return a list of WirelessInterface objects of the current wireless interfaces available on the system.

    This function first check all network interfaces available in /sys/class/net
    $ ls /sys/class/net
    lo wlan0 wlan1 enp8s0 ...

    Then selects all interface that contains DEVTYPE=wlan
    $ cat /sys/class/net/<iface>/uevent
    DEVTYPE=wlan   <--
    INTERFACE=wlan0
    IFINDEX=7

    Args:
        verbose (bool, optional): show verbose messages. Defaults to False.

    Returns:
        interfaces (list): this function returns a list of WirelessInterface objects.
    """

    if verbose:
        print("\n", "-" * 50, "GETTING INTERFACES")

    interfaces = list()
    interface_names = listdir("/sys/class/net")
    for interface in interface_names:
        with open(f"/sys/class/net/{interface}/uevent", "r") as handler:
            info = handler.read()
            DEVTYPE = re.findall("DEVTYPE=(.*)", info)

            if len(DEVTYPE) > 0 and DEVTYPE[0] == "wlan":
                if verbose:
                    print(f"[!] Wireless Interface Found: {interface}")

                interfaces.append(WirelessInterface(interface))

    return interfaces


def main():
    pass
    
if __name__ == "__main__":
    if platform != "linux":
        print("WirelessWizard only supports Linux platforms.")

    main()


# TODO:
# - Add custom error classes.
# - Add change_name method using command `$ ip link set <iface> name <new_name>`
# - Add change_flag method using command `$ ip link set <iface> FLAG {on|off}`
# - Add chipset attribute to WirelessInterface class.

# FIXME:
# - Sometimes a wireless interface cant scan networks after being changed to monitor.
# - Sometimes after changing channels, network services stop working.. No fucking clue.

# SYSTEM COMMAND USED:
# $ ip link
# $ iw


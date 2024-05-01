
"""
WirelessWizard.py

This module allows you to manipulate wireless network interfaces using system commands.

Author: mind2hex https://github.com/mind2hex
"""

from .wirelesswizard import NetworkInfo, WirelessInterface, calculate_channel, get_wireless_interfaces

__all__=[
    "NetworkInfo",
    "WirelessInterface",
    "calculate_channel",
    "get_wireless_interfaces"
]
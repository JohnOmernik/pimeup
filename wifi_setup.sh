#!/bin/bash

# Scan for networks

WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf "

sudo iwlist wlan0 scan|grep -P "(Address|Channel|Encryption key|ESSID|Mode)"


echo ""
echo ""
read -e -p "Please enter the Network Name (ESSID) of the network you wish to add: " ESSID
read -e -p "Is this ESSID a hidden network? (Y/N): " -i "N" HIDDEN
read -e -p "Please enter the password (will be visible) (Leave blank for no password): " PSK

if [ "$HIDDEN" == "Y" ]; then
    HID_STR="scan_ssid=1"
else
    HID_STR=""
fi

if [ "$PSK" == "" ]; then
    KEY_MGMT="NONE"
else
    KEY_MGMT="WPA-PSK"
fi

if [ "$PSK" == "" ]; then
    PSK_STR=""
else
    PSK_STR="psk=\"$PSK\""
fi

echo "Adding network $ESSID with PSK $PSK (using $KEY_MGMT) to $WPA_CONF"

read -e -p "Are you sure you wish to do this? (Y/N): " -i "N" CHK

if [ "$CHK" != "Y" ]; then
    echo "Not adding!"
    exit 1
fi

sudo tee -a $WPA_CONF << EOF

network={
    ssid="$ESSID"
    key_mgmt=$KEY_MGMT
    $PSK_STR
    $HID_STR
}
EOF

echo ""
echo "Wireless network added, WPA normally identifies that it has a new network, but you may need to reboot or restart WPA with sudo wpa_cli reconfigure"
echo ""




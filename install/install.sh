#!/bin/bash

# Stop at the first sign of an error
set -e

# Change root password
echo -e "ludwigvanbeethoven\nludwigvanbeethoven" | passwd -q

# Set up initial wireless connection to obtain Internet access
cp lagniappe/wlan0-* /etc/netctl/
netctl start wlan0-valinor
netctl start wlan0-valinor

# Upgrade system
pacman -Syu --noconfirm
sync

# Install packages for WiFi access point and Python 3
pacman -S dnsmasq hostapd haveged --noconfirm
pacman -S python3 python-pyserial python-bottle --noconfirm
pacman -S sudo --noconfirm

# Set up static network configuration for wireless
netctl stop wlan0-valinor
netctl start wlan0-static
netctl enable wlan0-static

# Set hostname
echo mixmaestro > /etc/hostname
hostname mixmaestro

# Configure hosts file
mv /etc/hosts /etc/hosts.orig
cp lagniappe/hosts /etc/

# Configure dnsmasq to serve as DNS and DHCP servers
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
cp lagniappe/dnsmasq.conf /etc/
systemctl start dnsmasq
systemctl enable dnsmasq

# Configure hostapd to serve as wireless bridge. We use a custom-built
# executable from adafruit that's compatible with our USB WiFi module.
mv /usr/sbin/hostapd /usr/sbin/hostapd.orig
tar zxvf lagniappe/hostapd.tar.gz -C /usr/sbin/
chown root: /usr/sbin/hostapd
mv /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.orig
cp lagniappe/hostapd.conf /etc/hostapd/
systemctl start hostapd
systemctl enable hostapd

# Route port 80 to 8080 so software doesn't need to bind to high port
cp lagniappe/iptables.rules 
systemctl start iptables
systemctl enable iptables

# Disable video output via system service
cp lagniappe/tvoff.service /etc/systemd/system/
systemctl start tvoff
systemctl enable tvoff

# Copy software files to their final resting place
cp -r mixmaestro /opt/
cp lagniappe/mixmaestro /usr/bin/

# Make software start at boot with systemd scripts
cp lagniappe/mixmaestro.service /etc/systemd/system/
systemctl start mixmaestro
systemctl enable mixmaestro

# Create non-privileged user and set a default password
useradd -g users -s /sbin/nologin -G tty howardshore
echo -e "ludwigvanbeethoven\nludwigvanbeethoven" | passwd -q howardshore

# Give members of the tty group permission to talk to the serial port
chmod 660 /dev/ttyAMA0

# Disable serial port console output
sed -i 's/console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 //' /boot/cmdline.txt

# Erase the installer and its support files
rm -f install.sh
rm -rf lagniappe
rm -rf mixmaestro

# Reboot to make things take effect
reboot

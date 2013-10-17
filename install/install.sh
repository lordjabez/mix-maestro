#!/bin/bash

# Stop at the first sign of an error, and print debug messages
set -ex

# Change root password
echo -e "ludwigvanbeethoven\nludwigvanbeethoven" | passwd -q

# Set up initial wireless connection to obtain Internet access
cp -f lagniappe/wlan0-* /etc/netctl/
netctl start wlan0-valinor

# Upgrade system
pacman -Syu --noconfirm
sync

# Install packages for WiFi access point and Python 3
pacman -S dnsmasq hostapd haveged --noconfirm
pacman -S python3 python-pyserial python-bottle --noconfirm
pacman -S sudo --noconfirm

# Enable the static network configuration for wireless on next reboot
netctl enable wlan0-static

# Set hostname
echo mixmaestro > /etc/hostname
hostname mixmaestro

# Configure hosts file
mv -f /etc/hosts /etc/hosts.orig
cp -f lagniappe/hosts /etc/

# Configure dnsmasq to serve as DNS and DHCP servers
mv -f /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
cp -f lagniappe/dnsmasq.conf /etc/
systemctl enable dnsmasq

# Configure hostapd to serve as wireless bridge. We use a custom-built
# executable from adafruit that's compatible with our USB WiFi module.
mv -f /usr/sbin/hostapd /usr/sbin/hostapd.orig
mv -f /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.orig
tar zxvf lagniappe/hostapd.tar.gz -C /usr/sbin/
chown root: /usr/sbin/hostapd
cp -f lagniappe/hostapd.conf /etc/hostapd/
systemctl enable hostapd

# Route port 80 to 8080 so software doesn't need to bind to high port
cp -f lagniappe/iptables.rules /etc/iptables/
systemctl enable iptables

# Disable video output via system service
cp -f lagniappe/tvoff.service /etc/systemd/system/
systemctl enable tvoff

# Copy software files to their final resting place
cp -rf mixmaestro /opt/
cp -f lagniappe/mixmaestro /usr/bin/

# Make software start at boot with systemd scripts
cp -f lagniappe/mixmaestro.service /etc/systemd/system/
systemctl enable mixmaestro

# Create non-privileged user and set a default password
useradd -g users -s /sbin/nologin -G tty howardshore
echo -e "ludwigvanbeethoven\nludwigvanbeethoven" | passwd -q howardshore

# Set up a udev rule so that the serial port has the proper permissions
echo 'KERNEL=="ttyAMA0" MODE="660"' > /etc/udev/rules.d/99-ttyAMA0.rules

# Disable serial port console output
sed -i 's/console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 //' /boot/cmdline.txt
systemctl disable serial-getty@ttyAMA0

# Erase the installer and its support files
rm -f install.sh
rm -rf lagniappe
rm -rf mixmaestro

# Reboot to make things take effect
reboot

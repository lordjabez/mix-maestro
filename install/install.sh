#!/bin/bash


################################################################################
# Manual steps

# Expand partition to use full capacity of memory card
# For now this is a manual step. Run fdisk as shown below,
# then delete partition 2, and recreate an extended partition
# and logical partition with exactly the same start values.
#echo -e d\n2\nn\ne\n\n\n\nn\nl\n\n\nw\n | fdisk /dev/mmcblk0
#reboot

################################################################################
# Automatic steps

# Resize the file system to match the partition size.
resize2fs /dev/mmcblk0p5

# Change root password
echo -e "ludwigvanbeethoven\nludwigvanbeethoven" | passwd -q

# Set up initial wireless connection to obtain Internet access
cp lagniappe/wlan0-* /etc/netctl/
netctl start wlan0-valinor

# Upgrade system
pacman -Syu --noconfirm
sync

# Install additional packages (TBD)
pacman -S dnsmasq hostapd haveged --noconfirm
# python3 with pyserial and bottle
# encryption for home folder

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

# Create non-privileged user and set a default password
useradd -m -g users -s /sbin/nologin -G tty howard
echo -e "shore\nshore" | passwd -q howard

# Encrypt that user's home folder (TBD)

# Disable video output via system service
cp lagniappe/tvoff@.service /etc/systemd/system/
systemctl start tvoff
systemctl enable tvoff

# TBD Copy software (pyo files only + web stuff + systemd scripts)

# TBD Make software start at boot with systemd scripts

# TBD disable serial port console output

# Give members of the tty group permission to talk to the serial port
chmod 660 /dev/ttyAMA0

# Reboot to make things take effect
reboot

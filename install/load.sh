#!/bin/bash -e

# Get the SD card device from the command line
diskdev=${1}

# Unmount the partitions if they're mounted already
umount ${diskdev}1 || true
umount ${diskdev}2 || true
umount ${diskdev}3 || true
umount ${diskdev}4 || true

# Set up the partitions
echo -e "o\nn\np\n1\n\n+100M\nt\nc\nn\np\n2\n\n\nw\n" | fdisk ${diskdev}

# Format the partitions and mount them
mkfs.vfat ${diskdev}1
mkfs.ext4 ${diskdev}2
mkdir -p /mnt/sdcard/boot /mnt/sdcard/root
mount ${diskdev}1 /mnt/sdcard/boot
mount ${diskdev}2 /mnt/sdcard/root

# Download and install the Arch Linux disto
wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-latest.tar.gz
tar -xvf ArchLinuxARM-rpi-latest.tar.gz -C /mnt/sdcard/root
rm ArchLinuxARM-rpi-latest.tar.gz
mv /mnt/sdcard/root/boot/* /mnt/sdcard/boot
sync

# Copy the needed install files
cp install.sh "/mnt/sdcard/boot/"
cp -r lagniappe "/mnt/sdcard/boot/"
mkdir -p  "/mnt/sdcard/boot/app"
cp -r ../*.py ../web "/mnt/sdcard/boot/app/"

# Write the proper version string to the index html file
version=$(git describe --always --abbrev=8)
version=${version/-*g/+}
echo "var version='${version}'" > "/mnt/sdcard/boot/app/web/js/version.js"

# Unmount the partitions
sync
umount ${diskdev}1
umount ${diskdev}2

#!/bin/bash -e

# Get the SD card device from the command line
diskdev=$(readlink -e /dev/disk/by-id/usb-Generic_Mass-Storage-0\:0)
archbuild=${1-rpi-2}

# Unmount the partitions if they're mounted already
umount ${diskdev}1 || true
umount ${diskdev}2 || true
umount ${diskdev}3 || true
umount ${diskdev}4 || true

# Set up the partitions
echo -e "o\nn\np\n1\n\n+100M\nt\nc\nn\np\n2\n\n\nw\n" | fdisk ${diskdev}
sync
sleep 1

# Format the partitions and mount them
mkfs.vfat ${diskdev}1
mkfs.ext4 -F ${diskdev}2
sync
sleep 1
mkdir -p /mnt/sdcard/boot /mnt/sdcard/root
mount ${diskdev}1 /mnt/sdcard/boot
mount ${diskdev}2 /mnt/sdcard/root

# Download and install the Arch Linux distro
pushd arch
archfile=ArchLinuxARM-$archbuild-latest.tar.gz
archurl=http://os.archlinuxarm.org/os/$archfile
rm -f $archfile.md5
wget $archurl.md5
md5sum --check --status $archfile.md5 || wget $archurl
tar -xvf $archfile -C /mnt/sdcard/root
popd

# Populate the boot folder
mv /mnt/sdcard/root/boot/* /mnt/sdcard/boot

# Enable root SSH logins so initial setup can be done
echo "PermitRootLogin yes" >> /mnt/sdcard/root/etc/ssh/sshd_config

# Copy the needed install files
cp install.sh /mnt/sdcard/boot/
cp -r lagniappe /mnt/sdcard/boot/

# Copy the code and data files
mkdir -p  "/mnt/sdcard/boot/mixmaestro"
cp -r ../*.py ../web "/mnt/sdcard/boot/mixmaestro/"

# Write the proper version string to the index html file
version=$(git describe --always --abbrev=8)
version=${version/-*g/+}
echo "var version='${version}';" > "/mnt/sdcard/boot/mixmaestro/web/js/version.js"

# Make sure everything's flushed and then unmount the partitions
sync
sleep 1
umount ${diskdev}1
umount ${diskdev}2

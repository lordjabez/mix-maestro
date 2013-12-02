#!/bin/bash

sudo umount /dev/sdd*

sudo dd bs=4M if=../../mix-maestro-img/mixmaestro-base-4gb.img of=/dev/sdd

sudo mount /dev/sdd5 /mnt/sdcard

sudo cp install.sh /mnt/sdcard/root/
sudo cp -r lagniappe /mnt/sdcard/root/
sudo mkdir -p  /mnt/sdcard/root/mixmaestro/
sudo rsync -avm --include='*.py' -f 'hide,! */' .. /mnt/sdcard/root/mixmaestro/
sudo cp -r ../web /mnt/sdcard/root/mixmaestro/

sudo umount /dev/sdd*

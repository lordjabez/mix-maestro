#!/bin/bash

SDCARD_ID=e06c801a-90c3-474c-8484-8ac426b4f92b

sudo cp install.sh /media/jud/$SDCARD_ID/root/
sudo cp -r lagniappe /media/jud/$SDCARD_ID/root/
sudo mkdir -p  /media/jud/$SDCARD_ID/root/mixmaestro
sudo cp ../*.py /media/jud/$SDCARD_ID/root/mixmaestro/
sudo cp -r ../web /media/jud/$SDCARD_ID/root/mixmaestro/

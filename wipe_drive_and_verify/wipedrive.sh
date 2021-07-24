#!/bin/bash
# Wipe a drive using dd, then read the drive back and confirm only zeroes are present
# Usage: sudo ./wipedrive.sh [disk name as listed in 'sudo fdisk -l', e.g. 'sdz']
# Usage example: sudo ./wipedrive.sh sdz
# A successful output from the pv command (i.e. disk read to confirm all zeroes) should look
# something like:
# 0000000 000000 000000 000000 000000 000000 000000 000000 000000
# *
# [total size of drive]
dd if=/dev/zero of=/dev/$1 bs=1M status=progress
pv /dev/$1 | od | head

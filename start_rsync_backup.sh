#!/bin/bash

rsync -avz --delete --exclude "eltern_backup.tar.gz" --exclude "mama_papa_backup" /mnt/x6/stuff/ till@100.78.27.125:/mnt/drive/till/backup/mnt/x6/stuff/

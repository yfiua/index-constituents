#!/bin/sh
year=$(date +%Y)
month=$(date +%m)
echo "Current Year : $year"
echo "Current Month : $month"

# create directory for current month
mkdir -p docs/$year/$month

# retrieve data
./get-constituents.py

# copy files
cp docs/*.json docs/$year/$month
cp docs/*.csv docs/$year/$month

#!/bin/bash

#
# This script has been tested on a 
# "fresh & default" installation of 32bit rasberry pi os "buster"
# installed onto a 32GB SD card using the imager.exe v1.3 from raspberrypi.org
# 27.07.2020
#

#
# Python3 and modules
#
sudo apt-get -y install python3
sudo python3 -m pip install matplotlib

#
# Webserver - Apache2
#
# In order to remotely access the datalogger's status page
# which is written to /home/pi/public_html, we need to 
# - create the public_html directory
# - install the apache2 webserver
# - enable the apache "userdir" module. 
#   as result, /home/pi/public_html/ will be accessible as http://localhost/~pi/ 
# - enable the apache "cgi" module to enable webpages created by scripts
#
# See also https://www.linux.com/training-tutorials/configuring-apache2-run-python-scripts/
#
mkdir /home/pi/public_html
mkdir /home/pi/public_html/cgi-bin
sudo apt-get -y install apache2
sudo a2enmod userdir
sudo a2enmod cgi
# now append manually : sudo -i ; cat Config/apache2.conf.append.txt >>/etc/apache2/apache2.conf ; exit
# and restart apache2 (or reboot) : sudo systemctl restart apache2

#
# Optional but useful
#
# GNUPLOT data plotting - will enable to use the provided .plt scripts
sudo apt-get -y install gnuplot
# JOE Text Editor
sudo apt-get -y install joe
# MIDNIGHT COMMANDER directory/file browser for the console
sudo apt-get -y install mc

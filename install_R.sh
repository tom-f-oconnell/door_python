#!/usr/bin/env bash

# get current user so we can explicitly run commands that don't require
# root privileges as that user
if [ $SUDO_USER ]; then
    USER=$SUDO_USER
else
    USER=`whoami`
fi

# TODO prevent this script from being run w/o root privileges

apt-key adv --keyserver keyserver.ubuntu.com --recv-keys \
    E298A3A825C0D65DFD57CBB651716619E084DAB9
add-apt-repository \
    'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu xenial/'

apt-get update
apt-get install -y r-base

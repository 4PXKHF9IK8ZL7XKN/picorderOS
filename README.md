<p align="center">
  <img width="203" height="273" src="https://raw.githubusercontent.com/directive0/picorderOS/master/assets/Picorder_Logo.png?raw=true">
</p>

# PicorderOS - Yellow stripe Fork

This Repro is a Fork / Rewrite of the famous [PicorderOS](https://github.com/directive0/picorderOS/tree/dev) from [Directive0](https://github.com/directive0)


The Projekt targets a "Modern Solution" for Performance optimisation. The Core Component is a local [Rabbitmq Service](https://www.rabbitmq.com/tutorials) to transmit Sensordata from Process to Process instead of Pipes.  

A set of python components provides functionality for a Raspberry Pi based [Tricorder](https://en.wikipedia.org/wiki/Tricorder) replica called a "picorder". A picorder is made of a Raspberry Pi, one or more sensor packages, a battery, a display, and supplemental components. The purpose of this project is to provide a simple, extensible method for quickly getting a Raspberry Pi to be a handheld sensor data collection and display device like the fictional device it is inspired by.

PicorderOS is experimental and in development. A lot of user configuration is required and you will probably need to "roll your own" solutions to some problems. PicorderOS is offered as a framework solution that can be built upon if desired or used as is.

For further information on hardware please visit the [Wiki](https://squaredwave.com/wiki/index.php?title=PicorderOS)

## Requirements:

PicorderOS was written to be run on a Raspberry Pi (of any kind) running Raspberry Pi OS - Legacy. 

Depending on hardware configuration picorderOS can use a number of existing third party libraries to communicate with i2c sensors. At present only a few sensors are currently officially supported like

- The [Sensehat](https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat/2) using the [sensehat library](https://pythonhosted.org/sense-hat/)
- The Bosch [BME680](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/) with an [Adafruit library](https://github.com/adafruit/Adafruit_CircuitPython_BME680)
- The Panasonic [AMG8833](https://www.digikey.ca/en/products/detail/panasonic-electronic-components/AMG8833/5825302) with an [Adafruit library](https://github.com/adafruit/Adafruit_CircuitPython_AMG88xx)

There is mostly stable support for the PocketGeiger and envirophat but detailed instructions are not available for those yet.

 For testing purposes picorderOS does not need to be run with real sensors, or even on a Raspberry Pi when put in "PC Mode".

Most installs will require:
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) (For various I/O functions)
- [os](https://pythonprogramming.net/python-3-os-module/) (For machine vitals)
- [psutil](https://psutil.readthedocs.io/en/latest/) (For simulating sensors when testing or demonstrating)
- [Adafruit Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) (Adafruit graciously offers a number of great python sensor libraries through their circuitpython platform)


For capacitive touch sensing the [Pimoroni cap1xxx library](https://github.com/pimoroni/cap1xxx) can be used for CAP1208 based capacitive touch buttons, and an [adafruit MPR121 Capacitive Sensor](https://github.com/adafruit/Adafruit_CircuitPython_MPR121) for MPR121 ones.

PicorderOS can run using an HDMI or Composite screen in some cases, and can also use TFT LCD displays. Depending on your choice of screen you may need:- [Pygame](https://www.pygame.org/wiki/GettingStarted) (For framebuffer screens)
- [Luma.lcd](https://pypi.org/project/luma.lcd/) (For a range of LCD options, thought not all are supported)


## Installation:

A requirements file is included, it can be used to install all the necessary python modules through pip.

Issue the following commands from within the picorderOS folder:

```
python3 -m pip install -r requirements.txt
```
RaspberryPi OS now ships with a version of pip that requires you install new modules in a virtual environment so as not to trash system modules.

For a simpler installation without virtual environment the flag --break-system-packages is needet.

A fresh Raspberry Pi OS image can usually be initialized to work with picorderOS with the following installation commands:

```

sudo apt update
sudo apt upgrade -y

sudo apt install -y \
python3-pip python3-psycopg2 libasound2-dev python3-dev build-essential git \
python3-virtualenv libsdl2-dev python3-pandas libsdl2-ttf-dev \
libjpeg-dev libsdl2-image-dev libsdl2-ttf-dev libsdl2-mixer-dev \ 
libportmidi-dev python3-dev python3-scipy python3-pygame \
libavcodec-dev libavfilter-dev libavdevice-dev ffmpeg \
rpicam-apps-opencv-postprocess rpicam-apps-opencv-postprocess 

mkdir ~/projekt

cd ~/projekt

git clone git@github.com:4PXKHF9IK8ZL7XKN/picorderOS.git 

cd picorderOS
```

# Install pip Packages on a small system like the pi zero 2w 

```
while read p; do pip install "$p" --break-system-packages ; done < requirements.txt
```

# a lgpio hack

```
pip uninstall RPi.GPIO --break-system-packages
```

# alternativ with virtualenv

```
python3 -m venv .picorderOS

source .picorder/bin/activate

sudo .picorder/bin/pip3 cache purge

while read p; do pip3 install "$p" --no-cache-dir ; done < requirements.txt
```


# The Next step is to setup the postgress database

```
sudo apt install -y postgresql-17 postgresql-17-postgis-3 postgresql-client-common postgresql-17-postgis-3-scripts postgresql-client-17
```

# setup of database access

```
sudo -u postgres psql

CREATE USER picorder_postgres WITH PASSWORD '[CREATEASAVELONGPASSWORD]';

CREATE DATABASE picorder_graph OWNER picorder_postgres;

CREATE DATABASE picorder_gis OWNER picorder_postgres;

GRANT CONNECT ON DATABASE picorder_graph TO picorder_postgres;

GRANT CONNECT ON DATABASE picorder_gis TO picorder_postgres;

\c picorder_gis

create extension postgis;

\q
```

# configure an database.ini & database_gisdata.ini

```
nano ~/database.ini

[postgresql]
host=localhost
database=picorder_graph
user=picorder_postgres
password=[USETHESAVELONGPASSWORD]

nano database_gisdata.ini 

[postgresql]
host=localhost
database=picorder_gis
user=picorder_postgres@
password=[USETHESAVELONGPASSWORD]
```

# Instert the Following Block , change the parameter arcordingly to your setup.


```
sudo apt-get install rabbitmq-server
```



# Installing Rabbitmq Backend

```
sudo apt-get install rabbitmq-server
```

# Raspi-Config

```
sudo raspi-config

3 Interface Options > I4 SPI -> ON
3 Interface Options > I5 I2C -> ON
```

# /boot/firmware/config.txt
```
[all]
dtoverlay=fbtft,spi0-0,st7789v,reset_pin=25,dc_pin=24,rotate=0,width=320,height=240
dtoverlay=i2c-mux,pca9548,addr=0x70,i2c-bus=1

# --- added by adafruit-pitft-helper Mon Nov 16 20:59:54 2026 ---
[all]
hdmi_force_hotplug=0
dtparam=spi=on
dtparam=i2c1=on
dtparam=i2c_arm=on
dtoverlay=mipi-dbi-spi,spi0-0,speed=40000000
dtparam=compatible=adafruit_st7789_drm\0panel-mipi-dbi-spi
dtparam=width=320,height=240
dtparam=dc-gpio=25,backlight-gpio=18
enable_tvout=0,drm
# --- end adafruit-pitft-helper Mon Nov 16 20:59:54 2026 ---
```



## Usage:

At present picorderOS supports a number of displays, sensors, and inputs. The user can mix and match their desired picorder load out. PicorderOS will generate an INI file on creation called ```config.ini```. By editing this file certain flags can be set for specific Picorder builds. Any sensors or peripherals not physically present must be turned off before picorderOS will run properly.

The software is started with ```python3 main.py``` from the project folder (run with sudo for full wifi features on 109 style builds), which starts the main loop. The main loop handles display directly, various ancillary elements like input detection, LED sequencing, and audio playback run as separate threads and communicate via flags set in the ```objects.py``` module.

Some experimentation may be necessary. PicorderOS is provided as free software and comes with no guarantee or warranty. This software is not to be used outside federation space, and is not suitable for use in environments that do not obey established laws of physics. Using this software could cause timeline damage, rocks exploding out of consoles, or blue barrels. Do not use PicorderOS if you have recently tested positive for Andorian Flu.

# setup linger

```
sudo loginctl enable-linger $USER
```


### Adding Systemd Units

# create folder for user services 
```
mkdir ~/.config/systemd/
mkdir ~/.config/systemd/user/
```

# Switch to Systemd-User-Folde
```
cd ~/.config/systemd/user/
```


# Symlink Projekt-Services
```
ln -s /home/[username]/projekt/picorderOS/systemd_units/picorder_rabbitmq.service picorder_rabbitmq.service
ln -s /home/christian/projekt/picorderOS/systemd_units/picorder_lcars.service picorder_lcars.service
```

# Reload Services
```
systemctl --user daemon-reload
```

# Enable run on system start
```
systemctl --user enable --now picorder_rabbitmq
systemctl --user enable --now picorder_lcars
```

# Enable run on system start


sudo apt install -y i2c-tools python3-pip
pip3 install adafruit-circuitpython-tca9548a --break-system-packages


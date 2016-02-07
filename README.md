# Warning

__This repository contains experimental code that is not ready for 
productive use. It is really not meant to be used on the daily basis and should be considered unstable. Use it on your own risk and only if you absolutely understand what you are doing!__

If you are looking for a stable branch, use the one from

https://github.com/tpfanco/tpfanco-legacy

# Disclaimer

By enabling software control of the system fan, you can void you warranty and damage or shorten the lifespan of your notebook. If you decide to use Tpfanco, you agree to hold us blameless for any damages or data loss that arise from the use of this software.

This project does not have any affiliation with Lenovo or IBM! 

# Tpfanco

## Description

Tpfanco is a free and open source fan control software for IBM/Lenovo ThinkPads running GNU/Linux. It consists of a fan control daemon and a GUI to monitor temperature sensor values and set thresholds. For selected ThinkPad models user-generated fan profiles are available. 

## Legacy

tpfanco-admin is a fork of ThinkPad Fan Control ([tp-fan](https://launchpad.net/tp-fan)) by Sebastian Urban.


## Tpfanco configuration GUI (tpfanco-admin)

tpfanco-admin is a GTK+ configuration and monitoring interface for tpfancod. tpfanco-admin communicates with tpfancod entirely over DBus.
## Requirements

* Python 2.7
* DBus, GTK+, libglade and GNU gettext with bindings for Python
* pkexec to obtain superuser privileges
* tpfancod

## Installation
### Dependencies
* Ubuntu users need to install the following packages: python-gtk2, python-glade2

Packages for the development version are currently not available. To install use

```
sudo make install
```

## Uninstall

You can uninstall tpfanco-admin by running

```
sudo make uninstall
```

## Usage

The installer will automatically create a shortcut to tpfanco-admin. To run from the command line, execute

```
tpfanco-admin_polkit
```

  
# License 

tpfanco-admin is covered by the GNU General Public License 3.

Copyright (C) 2011-2016 Vladyslav Shtabovenko
Copyright (C) 2007-2009 Sebastian Urban

tpfanco-admin is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

tpfanco-admin is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with tpfancod. If not, see http://www.gnu.org/licenses/.


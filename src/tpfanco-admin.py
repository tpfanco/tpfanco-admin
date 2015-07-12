#! /usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# tpfanco - controls the fan-speed of IBM/Lenovo ThinkPad Notebooks
# Copyright (C) 2011-2012 Vladyslav Shtabovenko
# Copyright (C) 2007-2009 Sebastian Urban
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import commands
import gettext
import logging
import os
import sys
import dbus
import gobject
import gtk
import gtk.glade
import pygtk

import gtk.gdk
from tpfanco_admin import temperaturedialog
pygtk.require('2.0')


class tpfan_admin(object):

    # data directory
    data_dir = '/usr/share/tpfanco-admin/'

    # path to executable that starts tpfanco-admin
    install_path = '/usr/bin/tpfanco-admin'

    # icon for window
    icon_filename = 'tpfanco-admin-128x128.png'

    # fan border picture
    fan_border_filename = 'fan_border.svg'

    # fan blades picture
    fan_blades_filename = 'fan_blades.svg'

    # name of per user preferences file
    pref_filename = '.tpfanco-admin'

    # gettext domain
    gettext_domain = 'tpfanco-admin'

    # gettext locale directory
    locale_dir = data_dir + 'locales'

    # profile submit enabled?
    profile_submit_enabled = True

    # profile submit url
    profile_submit_url = ''

    # program to open url
    #profile_url_opener = data_dir + '/open-url.sh'
    profile_url_opener = ''

    # required tpfand version
    required_daemon_version = '1.0.0'

    # version
    version = '1.0.0'

    def __init__(self):
        logging.basicConfig(stream=sys.stdout,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)

        self.parse_command_line_args()
        tdsettings = {}
        tdsettings['profile_submit_enabled'] = self.profile_submit_enabled
        tdsettings['pref_filename'] = self.pref_filename
        tdsettings['version'] = self.version
        tdsettings['locale_dir'] = self.locale_dir
        tdsettings['gettext_domain'] = self.gettext_domain
        tdsettings['debug'] = self.debug

        # i18n
        gettext.install(self.gettext_domain, self.locale_dir, unicode=1)
        gtk.glade.bindtextdomain(self.gettext_domain, self.locale_dir)
        gtk.glade.textdomain(self.gettext_domain)

        # D-Bus
        system_bus = dbus.SystemBus()

        # try connecting to daemon
        try:
            controller_proxy = system_bus.get_object(
                'org.tpfanco.tpfancod', '/Control')
            controller = dbus.Interface(
                controller_proxy, 'org.tpfanco.tpfancod.Control')
            act_settings_proxy = system_bus.get_object(
                'org.tpfanco.tpfancod', '/Settings')
            act_settings = dbus.Interface(
                act_settings_proxy, 'org.tpfanco.tpfancod.Settings')
            tdsettings['controller'] = controller
            tdsettings['act_settings'] = act_settings
        except Exception, ex:
            print 'Error connecting to tpfand: ', ex
            msgdialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                          _('Unable to connect to ThinkPad Fan Control daemon (tpfand).\n\n'
                                            'Please make sure you are running this program on a supported IBM/Lenovo ThinkPad, a recent thinkpad_acpi module is loaded with fan_control=1 and tpfand has been started.'))
            msgdialog.set_title(_('tpfanco configuration'))
            msgdialog.run()
            exit(1)

        # check required daemon version
        daemon_version = controller.get_version()
        if daemon_version < self.required_daemon_version:
            msgdialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                          _('The version of the tpfanco daemon (tpfancod) installed on your system is too old.\n\n'
                                            'This version of tpfanco-admin requires tpfancod %s or later, however tpfancod %s is installed on your system.') % (self.required_daemon_version, daemon_version))
            msgdialog.set_title(_('tpfanco configuration'))
            msgdialog.run()
            exit(2)

        # Load Glade file
        tdsettings['my_xml'] = gtk.glade.XML(
            self.data_dir + 'tpfanco-admin.glade')

        # Load icons
        gtk.window_set_default_icon_from_file(
            self.data_dir + self.icon_filename)

        temperature_dialog = temperaturedialog.TemperatureDialog(
            tdsettings)

        temperature_dialog.run()

    def parse_command_line_args(self):
        """evaluate command line arguments"""

        parser = argparse.ArgumentParser()

        parser.add_argument('-d', '--debug', help='enable debugging output',
                            action='store_true')
        parser.add_argument(
            '-s', '--share', help='alternate location for files that are usually located in /usr/share/tpfanco-admin/')

        args = parser.parse_args()

        self.debug = args.debug
        if args.share:
            self.data_dir = args.share


def main():

    app = tpfan_admin()

if __name__ == '__main__':
    main()

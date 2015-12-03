#! /usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# tpfanco - controls the fan-speed of IBM/Lenovo ThinkPad Notebooks
# Copyright (C) 2011-2015 Vladyslav Shtabovenko
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

import gettext
import logging
import os

import gobject
import gtk
import pygtk

import thermometer
#import fan
pygtk.require('2.0')


class ArgumentException(Exception):

    def __init__(self):
        pass


class TemperatureDialog:

    """main configuration dialog"""

    controller = None
    act_settings = None
    my_xml = None

    # True while controls are updated to show the current settings
    updating = False

    # Width of thermometers
    thermometer_width = 600

    # desired window height, if screen permits it
    desired_height = 680

    # reserved screen height
    reserved_screen_height = 50

    # disclaimer accepted?
    disclaimer_accepted = False

    # manual configuration is currently enabled?
    override = False

    def __init__(self, tdsettings):
        self.tdsettings = tdsettings
        self.my_xml = tdsettings['my_xml']
        self.controller = tdsettings['controller']
        self.act_settings = tdsettings['act_settings']
        self.pref_filename = tdsettings['pref_filename']
        self.locale_dir = tdsettings['locale_dir']
        self.gettext_domain = tdsettings['gettext_domain']
        self.version = tdsettings['version']
        self.debug = tdsettings['debug']

        self.logger = logging.getLogger(__name__)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)

        # i18n
        gettext.install(self.gettext_domain, self.locale_dir, unicode=1)
        self.load_text()

        # connect dialogs

        self.window = self.my_xml.get_widget('temperatureDialog')
        self.about_dialog = self.my_xml.get_widget('aboutDialog')
        self.add_sensor_dialog = self.my_xml.get_widget('addSensorDialog')

        self.cbEnable = self.my_xml.get_widget('checkbuttonEnable')
        self.cbEnable.connect('toggled', self.enable_changed, None)

        self.cbOverride = self.my_xml.get_widget('checkbuttonOverride')
        self.cbOverride.connect('toggled', self.override_changed, None)

        self.hsHysteresis = self.my_xml.get_widget('hscaleHysteresis')
        self.hsHysteresis.connect('value-changed', self.options_changed, None)

        self.swThermometers = self.my_xml.get_widget(
            'scrolledwindowThermometers')

        self.vbThermometers = self.my_xml.get_widget('vboxThermometers')

        self.init_thermos()

        self.rbCelcius = self.my_xml.get_widget('radiobuttonCelcius')
        self.rbFahrenheit = self.my_xml.get_widget('radiobuttonFahrenheit')
        self.rbFahrenheit.set_group(self.rbCelcius)
        self.rbCelcius.connect('toggled', self.temperature_unit_changed, None)

        self.eModel = self.my_xml.get_widget('entryModel')
        self.eProfile = self.my_xml.get_widget('entryProfile')
        self.tvProfileComments = self.my_xml.get_widget(
            'textviewProfileComments')
        self.lSpeed = self.my_xml.get_widget('labelSpeed')
        self.lLevel = self.my_xml.get_widget('labelLevel')
        self.dActionArea = self.my_xml.get_widget('dialog-action_area')

        self.bAbout = self.my_xml.get_widget('buttonAbout')
        self.bAbout.connect('clicked', self.about_clicked, None)

        self.dActionArea.set_child_secondary(self.bAbout, True)

        self.bAddSensor = self.my_xml.get_widget('buttonAddSensor')
        self.bAddSensor.connect('clicked', self.add_sensor_clicked, None)
        self.dActionArea.set_child_secondary(self.bAddSensor, True)

        self.bSubmitProfile = self.my_xml.get_widget('buttonSubmitProfile')
        self.bSubmitProfile.connect(
            'clicked', self.submit_profile_clicked, None)
        self.dActionArea.set_child_secondary(self.bSubmitProfile, True)

        self.bClose = self.my_xml.get_widget('buttonClose')

        self.update_model_info()
        self.update_limits()
        self.refresh_monitor()

        for therm in self.thermos:
            self.thermos[therm].end_animation()

        # refresh time is synced with the polling time of the daemon
        gobject.timeout_add(
            self.act_settings.get_settings()['poll_time'], self.refresh_monitor)

        # calculate initial size
        width, height = self.window.get_size()
        screen_height = gtk.gdk.screen_height()  # @UndefinedVariable
        height = min(
            screen_height - self.reserved_screen_height, self.desired_height)
        self.window.resize(width, height)
        self.read_preferences()

    def run(self):
        """shows the temperature dialog"""
        self.update_settings()
        self.update_sensor_names()
        self.update_triggers()
        self.update_sensitivity()
        retval = 0  # 1 = close
        while (not (retval == 1 or retval == gtk.RESPONSE_DELETE_EVENT)):
            retval = self.window.run()
        self.window.destroy()

    def init_thermos(self):
        self.thermos = {}

        for n in self.vbThermometers.get_children():
            self.vbThermometers.remove(n)
        for n in self.controller.get_temperatures():
            therm = thermometer.Thermometer(self.tdsettings)
            therm.sensor_id = n
            therm.dialog_parent = self.window
            therm.set_size_request(self.thermometer_width, therm.wanted_height)
            therm.connect('trigger-changed', self.triggers_changed, n)
            therm.connect('name-changed', self.sensor_name_changed, n)
            self.thermos[n] = therm
            self.vbThermometers.pack_start(therm)

    def load_text(self):

        self.disclaimer_text = _('By enabling software control of the system fan, you can damage '
                                 'or shorten the lifespan of your notebook.\n\n'
                                 'IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING '
                                 'WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR '
                                 'REDISTRIBUTE THE PROGRAM, BE LIABLE TO YOU FOR DAMAGES, '
                                 'INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING '
                                 'OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED '
                                 'TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY '
                                 'YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER '
                                 'PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE '
                                 'POSSIBILITY OF SUCH DAMAGES.\n\n'
                                 'Are you sure that you want to enable software control of the system fan?')

        self.override_off_warning_text = _('By disabling manual configuration your custom settings '
                                           'will be lost.\n\n'
                                           'Are you sure that you want to disable the manual configuration?')

        self.profile_submit_text = _('Submitting your fan profile to the developers of ThinkPad Fan Control '
                                     'allows them to integrate it into the next version of this software.\n\n'
                                     '%s\n\n'
                                     'Please make sure that your notebook is quiet and not overheating '
                                     'with your current settings.\n\n'
                                     'Are you sure that you want to submit your profile now?')

        self.profile_model_known_text = _('A fan profile for your notebook model already exists. '
                                          'Please only submit your custom fan profile if it leads to better results '
                                          'than the non-manual configuration of ThinkPad Fan Control on '
                                          'your notebook.')

        self.profile_model_unknown_text = _('No fan profile exists for your notebook at this time. '
                                            'Your submission is appreciated.')

    def celcius_to_fahrenheit(self, temp):
        """Converts temp from celcius to fahrenheit"""
        return float(temp) * 9. / 5. + 32.

    def celcius_to_celcius(self, temp):
        """Converts temp from celcius to celcius"""
        return temp

    def multiply_list(self, lst, factor):
        """Multiplies every item in lst with the given factor"""
        return [x * factor for x in lst]

    def write_preferences(self):
        """Writes user preferences to disk"""
        try:
            preffile = open(
                os.path.expanduser("~/" + self.pref_filename), "w")
            preffile.write(self.get_temperature_unit() + "\n")
            # preffile.write(
            #   str(temperature_dialog.fanGraph.get_do_animation()) + "\n")
            preffile.close()
        except IOError:
            pass

    def read_preferences(self):
        """Reads user preferences from disk"""
        try:
            preffile = open(
                os.path.expanduser("~/" + self.pref_filename), "r")
            unit = preffile.readline().strip()
            do_animation = preffile.readline().strip()
            self.set_temperature_unit(unit)
            preffile.close()
        except IOError:
            self.set_temperature_unit('celcius')

    def about_clicked(self, widget, data=None):
        """About was clicked"""
        ctext = _("Monitors the temperature and controls the \n"
                  "fan-speed of IBM/Lenovo ThinkPad Notebooks")
        text = _("Daemon (tpfand) version: %s\nGTK+ configuration UI (tpfanco-admin) version: %s\n\n") % (
            self.controller.get_version(), self.version) + ctext
        self.about_dialog.set_comments(text)
        self.about_dialog.set_transient_for(self.window)
        self.about_dialog.set_logo(None)
        self.about_dialog.run()
        self.about_dialog.hide()

    def add_sensor_clicked(self, widget, data=None):
        """Add sensor was clicked"""
        self.add_sensor_dialog.set_transient_for(self.window)
        # TODO: need to finish this

        def combobox_changed(widget, data=None):
            entry_sensor_path.set_text('')
            entry_sensor_scaling.set_text('')
            entry_sensor_name.set_text('')
            if combobox_sensor_type.get_active() != 0:
                entry_sensor_path.hide()
                label_sensor_path.hide()
                entry_sensor_scaling.hide()
                label_sensor_scaling.hide()
            else:
                entry_sensor_path.show()
                label_sensor_path.show()
                entry_sensor_scaling.show()
                label_sensor_scaling.show()

        def text_entries_changed(widget, data=None):
            button_add_sensor.set_sensitive(False)

            if combobox_sensor_type.get_active() != 0:
                if len(entry_sensor_name.get_text()) != 0:
                    button_add_sensor.set_sensitive(True)
            else:
                try:
                    float(entry_sensor_scaling.get_text())
                    scaling_is_valid = True
                except ValueError:
                    scaling_is_valid = False

                if self.act_settings.check_if_hwmon_sensor_exists(entry_sensor_path.get_text()) and \
                        scaling_is_valid and \
                        len(entry_sensor_name.get_text()) != 0:
                    button_add_sensor.set_sensitive(True)

        combobox_sensor_type = self.my_xml.get_widget('comboboxSensorType')
        entry_sensor_path = self.my_xml.get_widget('entrySensorPath')
        label_sensor_path = self.my_xml.get_widget('labelSensorPath')
        entry_sensor_scaling = self.my_xml.get_widget('entrySensorScaling')
        label_sensor_scaling = self.my_xml.get_widget('labelSensorScaling')
        entry_sensor_name = self.my_xml.get_widget('entrySensorName2')
        button_add_sensor = self.my_xml.get_widget('buttonAddSensorOK')

        combobox_sensor_type.append_text(_('hwmon sensor'))
        ibm_thermal_sensors = self.act_settings.get_available_ibm_thermal_sensors()
        for n in ibm_thermal_sensors:
            combobox_sensor_type.append_text('ibm_thermal_' + n)
        combobox_sensor_type.set_active(0)

        combobox_sensor_type.connect('changed', combobox_changed, None)
        entry_sensor_path.connect('changed', text_entries_changed, None)
        entry_sensor_scaling.connect('changed', text_entries_changed, None)
        entry_sensor_name.connect('changed', text_entries_changed, None)

        if self.add_sensor_dialog.run() == 1:      # OK was pressed
            try:
                new_sensor = {}
                sensor_type = combobox_sensor_type.get_active()
                if sensor_type != 0:
                    sensor_id = ibm_thermal_sensors[sensor_type - 1]
                else:
                    sensor_id = entry_sensor_path.get_text()
                new_sensor[sensor_id] = {'0': '255'}
                new_sensor['name'] = {sensor_id: entry_sensor_name.get_text()}
                new_sensor['scaling'] = {
                    sensor_id: entry_sensor_scaling.get_text()}
                self.logger.debug(
                    'Adding new sensors: ' + str(new_sensor))
                self.act_settings.add_new_sensor(new_sensor)
                self.init_thermos()
                #self.triggers_changed(None, sensor_id)
            except _, e:
                print e
                pass

        self.logger.debug(
            'Closed the new sensor dialog')

        self.add_sensor_dialog.hide()

    def submit_profile_clicked(self, widget, data=None):
        """Submit profile... was clicked"""
        # TODO: replace this with a file dialog
        if self.act_settings.is_profile_exactly_matched():
            submit_text = self.profile_submit_text % self.profile_model_known_text
        else:
            submit_text = self.profile_submit_text % self.profile_model_unknown_text
        submit_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_QUESTION,
                                          buttons=gtk.BUTTONS_YES_NO,
                                          message_format=submit_text)
        if submit_dialog.run() == gtk.RESPONSE_YES:
            profile = self.act_settings.get_profile_string()
            model_info = self.act_settings.get_model_info()
            path = '/tmp/tpfand-profile/' + \
                model_info['vendor'].lower() + '_' + model_info['id'].lower()
            if not os.path.exists('/tmp/tpfand-profile'):
                os.makedirs('/tmp/tpfand-profile')
            f = open(path, 'w')
            f.write(str(profile))
            f.close()
        submit_dialog.destroy()

    def update_sensor_names(self):
        """Updates the shown sensor names from the settings"""
        if not self.updating:
            self.updating = True
            names = self.act_settings.get_sensor_names()
            for n in self.thermos:
                self.thermos[n].set_sensor_name(names[n])
            self.updating = False

    def update_triggers(self):
        """Updates the shown triggers from the settings"""
        if not self.updating:
            self.updating = True
            triggers = self.act_settings.get_trigger_points()
            for n in self.thermos:
                therm = self.thermos[n]
                therm.set_triggers(triggers[n])
            self.updating = False

    def update_temperature_unit(self):
        """Updates the temperature unit"""
        if not self.updating:
            self.updating = True
            if self.temperature_unit == 'celcius':
                self.rbCelcius.set_active(True)
                cfunc = self.celcius_to_celcius
                decs = 0
            elif self.temperature_unit == "fahrenheit":
                self.rbFahrenheit.set_active(True)
                cfunc = self.celcius_to_fahrenheit
                decs = 1
            else:
                print "Unknown temperature unit: ", self.temperature_unit

            for therm in self.thermos:
                self.thermos[therm].set_temp_convert_func(cfunc, decs)

            self.updating = False

    def update_settings(self):
        """Updates the shown options from the settings"""
        if not self.updating:
            self.updating = True
            opts = self.act_settings.get_settings()
            self.logger.debug(
                'Updating tpfancod settings to ' + str(opts))
            if bool(opts['enabled']) == True:
                self.disclaimer_accepted = True
            self.cbEnable.set_active(bool(opts['enabled']))
            self.cbOverride.set_active(bool(opts['override_profile']))
            self.hsHysteresis.set_value(opts['hysteresis'])
            self.update_sensitivity()
            if self.cbOverride.get_active() == True:
                self.eProfile.set_text(
                    _("No profile is used because you enabled manual configuration."))
                comment = ""
            else:
                self.eProfile.set_text(self.profile_list)
                comment = self.act_settings.get_profile_comment()
            self.tvProfileComments.get_buffer().set_text(comment)
            self.updating = False

    def update_limits(self):
        """Updates the limits for the settings"""
        if not self.updating:
            self.updating = True
            self.hsHysteresis.set_range(
                *self.act_settings.get_setting_limits('hysteresis'))
            #self.hsIntervalDelay.set_range(*globals.multiply_list(self.act_settings.get_setting_limits('interval_delay'), 1.0/1000.0))
            #self.hsIntervalDuration.set_range(*globals.multiply_list(self.act_settings.get_setting_limits('interval_duration'), 1.0/1000.0))
            self.updating = False

    def update_model_info(self):
        """Updates the shown model info"""
        model_info = self.act_settings.get_model_info()
        self.eModel.set_text(
            "%s %s (%s)" % (model_info['vendor'].strip(), model_info['name'].strip(), model_info['id'].strip()))
        loaded_profiles = self.act_settings.get_loaded_profiles()
        if len(loaded_profiles) == 1:
            lp = str(loaded_profiles[0])
        else:
            # skip generic if profiles are loaded
            lp = ""
            for x in loaded_profiles[1:]:
                if lp != "":
                    lp += ", "
                lp += str(x)
        self.profile_list = lp

    def update_sensitivity(self):
        """sets if settings are changeable"""

        if self.cbEnable.get_active():
            self.cbOverride.set_sensitive(True)
            self.set_profile_override_controls_sensitivity(
                self.cbOverride.get_active())
        else:
            self.cbOverride.set_sensitive(False)
            self.set_profile_override_controls_sensitivity(False)

        self.bSubmitProfile.set_sensitive(self.cbOverride.get_active())

        for therm in self.thermos:
            self.thermos[therm].set_show_triggers(self.cbEnable.get_active())

    def set_profile_override_controls_sensitivity(self, override):
        """sets if profile settings are configurable by user"""
        # TODO: fixme
        # for control in [self.hsIntervalDuration, self.hsIntervalDelay,
        # self.hsHysteresis] + self.thermos:
        # for control in [self.hsHysteresis] + self.thermos:
        #   control.set_sensitive(override)

    def set_temperature_unit(self, unit):
        if unit == 'celcius':
            self.temperature_unit = 'celcius'
        elif unit == 'fahrenheit':
            self.temperature_unit = 'fahrenheit'
        else:
            raise ArgumentException()
        self.update_temperature_unit()
        self.write_preferences()

    def get_temperature_unit(self):
        return self.temperature_unit

    def temperature_unit_changed(self, widget, data=None):
        if self.rbCelcius.get_active():
            self.temperature_unit = 'celcius'
        else:
            self.temperature_unit = 'fahrenheit'
        self.update_temperature_unit()
        self.write_preferences()

    def enable_changed(self, widget, data=None):
        """the user has changed the enabled option"""
        self.logger.debug(
            'The user has changed enabled to ' + str(self.cbEnable.get_active()))
        # show disclaimer, if it hasn't been accepted before
        if self.cbEnable.get_active() and not self.disclaimer_accepted:
            disclaimer_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_WARNING,
                                                  buttons=gtk.BUTTONS_YES_NO, message_format=self.disclaimer_text)
            if disclaimer_dialog.run() == gtk.RESPONSE_YES:
                self.disclaimer_accepted = True
            else:
                self.cbEnable.set_active(False)
            disclaimer_dialog.destroy()
        # otherwise, update the settings
        self.options_changed(widget, data)

    def override_changed(self, widget, data=None):
        """the user has changed the override option"""
        # show warning
        if self.override and not self.cbOverride.get_active():
            warning_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_WARNING,
                                               buttons=gtk.BUTTONS_YES_NO,
                                               message_format=self.override_off_warning_text)
            if warning_dialog.run() != gtk.RESPONSE_YES:
                self.cbOverride.set_active(True)
            warning_dialog.destroy()
        self.override = self.cbOverride.get_active()
        self.options_changed(widget, data)

    def options_changed(self, widget, data=None):
        """the user has changed an option"""
        self.logger.debug('The user has changed an option')
        # every time an option is changed we read the status of
        # all options and send it to tpfancod
        if not self.updating:
            opts = {}
            opts['enabled'] = str(self.cbEnable.get_active())
            opts['override_profile'] = str(self.cbOverride.get_active())
            if self.cbOverride.get_active():
                opts['hysteresis'] = str(int(self.hsHysteresis.get_value()))
            self.logger.debug('Changing tpfancod settings to %s' % (opts))
            self.act_settings.set_settings(opts)
            self.logger.debug('Resetting trips')
            self.controller.reset_trips()
        self.update_settings()
        self.update_triggers()
        self.update_sensor_names()

    def triggers_changed(self, widget, sensor_id):
        """the user has changed a trigger temperature"""
        if not self.updating:
            therm = self.thermos[sensor_id]
            triggers = self.act_settings.get_trigger_points()
            triggers[sensor_id] = therm.get_triggers()
            self.act_settings.set_trigger_points(triggers)
            self.controller.reset_trips()
        self.update_triggers()
        self.refresh_monitor()

    def sensor_name_changed(self, widget, sensor_id):
        """the user has changed a sensor name"""
        if not self.updating:
            therm = self.thermos[sensor_id]
            names = self.act_settings.get_sensor_names()
            names[sensor_id] = therm.get_sensor_name()
            self.act_settings.set_sensor_names(names)
        self.update_sensor_names()

    def refresh_monitor(self):
        """Refreshes the temperature/fan monitor"""
        # temperatures
        temps = self.controller.get_temperatures()
        hys_temps, hys_levels = self.controller.get_trip_temperatures(
        ), self.controller.get_trip_fan_speeds()
        for n in temps:
            self.thermos[n].show()
            self.thermos[n].set_temperature(temps[n])
            if n in hys_temps:
                self.thermos[n].set_hysteresis_temperature(
                    hys_temps[n], hys_levels[n])
            else:
                self.thermos[n].set_hysteresis_temperature(None, None)

        # fan speed
        try:
            fan_state = self.controller.get_fan_state()

            self.lSpeed.set_text(_("%d RPM") % (fan_state['rpm']))
            self.lLevel.set_text(_("Level %d") % (fan_state['level']))
        except:
            self.lSpeed.set_text(_("Unknown"))
            self.lSpeed.set_text(_("Unknown"))

        return True

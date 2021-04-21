#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   AÜC Hardal <umit.hardal@ess.eu>
#
# *****************************************************************************

"""LoKI Experiment Configuration dialog."""

from nicos.clients.gui.utils import loadUi
from nicos.utils import findResource

from nicos_ess.loki.gui.loki_panel import LokiPanelBase
from nicos_ess.loki.gui.sample_environment import SampleEnvironmentBase


class LokiExperimentPanel(LokiPanelBase, SampleEnvironmentBase):
    panelName = 'LoKI Instrument Setup'

    def __init__(self, parent, client, options):
        LokiPanelBase.__init__(self, parent, client, options)
        SampleEnvironmentBase.__init__(self)
        loadUi(self, findResource('nicos_ess/loki/gui/ui_files/exp_config.ui'))

        self.window = parent

        self.holder_info = options.get('holder_info', [])
        self.instrument = options.get('instrument', 'loki')
        self.initialise_connection_status_listeners()
        self.initialise_environments()

        self.envComboBox.addItems(self.get_environment_names())
        # Start with a "no item", ie, empty selection.
        self.envComboBox.setCurrentIndex(-1)

        # Hide read-only properties and hide and disable reference cell
        # positions until a sample environment is chosen by the user.
        self.propertiesGroupBox.setVisible(False)
        self.refPosGroupBox.setVisible(False)
        self.refPosGroupBox.setEnabled(False)  # this is an extra safety measure

        self.envComboBox.activated.connect(self._activate_environment_settings)

        # Listen to changes in Aperture and Detector Offset values
        self.apXBox.textChanged.connect(self.set_apt_pos_x)
        self.apYBox.textChanged.connect(self.set_apt_pos_y)
        self.apWBox.textChanged.connect(self.set_apt_width)
        self.apHBox.textChanged.connect(self.set_apt_height)
        self.offsetBox.textChanged.connect(self.set_det_offset)

        # Disable apply buttons in both settings until an action taken by the
        # user.
        self.sampleSetApply.setEnabled(False)
        self.instSetApply.setEnabled(False)

    def initialise_environments(self):
        self.add_environment(
            {
                'name': 'Tumbler Sample Changer',
                'number_of_cells': '4',
                'cell_type': 'Titanium',
                'can_rotate_samples': 'Yes',
                'has_temperature_control': 'No',
                'has_pressure_control': 'No'
            }
        )
        self.add_environment(
            {
                'name': 'Peltier Sample Changer',
                'number_of_cells': '12',
                'cell_type': 'Copper',
                'can_rotate_samples': 'No',
                'has_temperature_control': 'Yes',
                'has_pressure_control': 'No'
            }
        )
        self.add_environment(
            {
                'name': 'Dome Cell Sample Changer',
                'number_of_cells': '4',
                'cell_type': 'Aluminium/Titanium',
                'can_rotate_samples': 'No',
                'has_temperature_control': 'Yes',
                'has_pressure_control': 'Yes'
            }
        )

    def setViewOnly(self, viewonly):
        pass

    def _activate_environment_settings(self):
        # Fill the read-only fields.
        self._map_environment_fields_to_properties()

        # Enable sample environments
        self.propertiesGroupBox.setVisible(True)
        self.refPosGroupBox.setVisible(True)
        self.refPosGroupBox.setEnabled(True)

        # Set focus to reference cell x-position
        self.refPosXBox.setFocus()
        # Enable apply button
        self.sampleSetApply.setEnabled(True)

    def _map_environment_fields_to_properties(self):
        for environment in self.environment_list:
            if environment.name == self.envComboBox.currentText():
                self.numCellBox.setText(environment.number_of_cells)
                self.cellTypeBox.setText(environment.cell_type)
                self.canRotateBox.setText(environment.can_rotate_samples)
                self.tempControlBox.setText(environment.has_temperature_control)
                self.pressControlBox.setText(environment.has_pressure_control)

    def set_det_offset(self, value):
        pass

    def set_apt_pos_x(self, value):
        pass

    def set_apt_pos_y(self, value):
        pass

    def set_apt_width(self, value):
        pass

    def set_apt_height(self, value):
        pass

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

"""LoKI Sample Environments"""

from collections import namedtuple


class SampleEnvironmentBase:
    """
    Base class for LoKI SANS sample environments. Each environment defined
    as a `namedtuple` with read-only properties. The settable properties of
    the environments should be fed in via corresponding Nicos devices.

    The read-only properties has a maximum length of five. This number
    optimized by the aesthetical considerations in the UI, though can be
    made different for each environment depending on the needs.

    The read-only properties should be hard-coded at the class level as a tuple.
    When adding a new environment, a type should be provided along with
    a dictionary with keys identical to that of defined in the property
    tuple of the corresponding environment. The type should be a string literal
    that is same as the environment name set in the environment
    object (`namedtuple`) declaration.
    """
    environment_types = ('SampleChanger',)
    # General schemas for environments that holds read-only properties.
    sample_changer_properties = (
        'name',
        'number_of_cells',
        'cell_type',
        'can_rotate_samples',
        'has_temperature_control',
        'has_pressure_control'
    )

    def __init__(self):
        self.environment_list = []
        # We create a subclasses for Sample Environments with corresponding
        # (read-only) properties.
        self.SampleChanger = namedtuple('SampleChanger',
                                        self.sample_changer_properties)

    def add_environment(self, environment_type, fields):
        self._validate(environment_type, fields)
        environment_switch = {
            'SampleChanger': self.SampleChanger
        }
        self.environment_list.append(
            (environment_type, environment_switch[environment_type](**fields))
        )

    def get_environment(self, env_name):
        if not env_name:
            raise ValueError('The name of the environment should be provided.')
        for environment in self.environment_list:
            if env_name == environment[1].name:
                return tuple(environment, environment[1]._asdict)
            else:
                raise ValueError(f'Requested environment, {env_name} does '
                                 f'not exist.')

    def get_environments(self):
        return self.environment_list

    def get_environments_as_dicts(self):
        """
        Convert each named tuple to a dictionary where field names shall be
        mapped to their corresponding values.
        """
        environments_as_dicts = [
            env[1]._asdict for env in self.environment_list
        ]
        return environments_as_dicts

    def get_environment_names(self):
        env_names = [env[1].name for env in self.environment_list]
        return env_names

    def _validate(self, environment_type, fields):
        if environment_type not in self.environment_types:
            raise ValueError(f'The environment with type {environment_type}'
                             f'does not exist.')

        if not isinstance(environment_type, str):
            raise ValueError('An environment type should be a string.')

        if not fields:
            raise ValueError('An non-empty dictionary of read-only properties'
                             'is required.')

        if not isinstance(fields, dict):
            raise ValueError('The properties should be a non-empty dictionary.')

        for values in fields.values():
            if not isinstance(values, str):
                raise ValueError('A read-only property of an'
                                 ' Environment should be a string.')


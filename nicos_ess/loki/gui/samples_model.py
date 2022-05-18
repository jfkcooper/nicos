#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""LoKI Samples Model."""
from nicos.core import ConfigurationError
from nicos.guisupport.qt import Qt

from nicos_ess.loki.gui.scriptbuilder_model import LokiScriptModel


class SamplesTableModel(LokiScriptModel):
    def __init__(self, columns):
        super().__init__(list(columns.keys()))
        self.positions = []
        self.columns = columns

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headings[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.positions[section] \
                if section < len(self.positions) else ''

    def set_positions(self, positions):
        self.positions = positions

        while len(self._table_data) < len(self.positions):
            self.insert_row(len(self._table_data))
        self._emit_update()

    def clear(self):
        self.raw_data = []

    def extract_samples(self):
        samples = []
        for index, (pos, sample) in enumerate(
                zip(self.positions, self.raw_data)):
            if sample:
                if not sample.get('Name', ''):
                    raise ConfigurationError(f'Position {pos} requires a name.')
                details = {self.columns.get(k, k): v
                           for k, v in sample.items()}
                details['position'] = pos
                samples.append((index, details))
        return samples

    def set_samples(self, samples):
        raw_data = [{} for _ in self.positions]
        for sample in samples:
            data = {k: sample[v] for k, v in self.columns.items()
                    if v in sample}
            if data and sample['position'] in self.positions:
                raw_data[self.positions.index(sample['position'])] = data
        while len(raw_data) < len(self.positions):
            raw_data.append({})
        self.raw_data = raw_data[:len(self.positions)]
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Reseda detector image based on McSTAS simulation."""

from pathlib import Path

import numpy as np

from nicos.core.constants import LIVE
from nicos.core.device import Readable
from nicos.core.params import ArrayDesc, Attach, Override, Param, Value, \
    intrange, listof, oneof, tupleof
from nicos.devices.mcstas import McStasImage as BaseImage, \
    McStasSimulation as BaseSimulation
from nicos.protocols.cache import FLAG_NO_STORE

from nicos_mlz.reseda.utils import MiezeFit
from nicos_virt_mlz.reseda.devices.sample import Sample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='reseda_fast'),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'l_ambda': Attach('Wave length', Readable),
        'd_lambda': Attach('Delta in wave length', Readable),
        'tablex': Attach('Sample position x', Readable),
        'tabley': Attach('Sample position y', Readable),
        'tablez': Attach('Sample position z', Readable),
        'table_rotx': Attach('Sample goniometer x', Readable),
        'table_roty': Attach('Sample goniometer y', Readable),
        'table_rotz': Attach('Sample goniometer z', Readable),
        'l1': Attach('Length between rf-flippers', Readable, optional=True),
        'l2': Attach('Length between second rf-flipper and detector',
                     Readable, optional=True),
        'coil_nse_len': Attach('Length of nse-coil', Readable, optional=True),
        'detectorangle': Attach('Rotation of detector around the sample',
                                Readable),
        'i_nse': Attach('Current of NSE-Coil', Readable),
        'f1': Attach('Frequency of first rf-flipper', Readable),
        'f2': Attach('Frequency of second rf-flipper', Readable),
        'psd_distance': Attach('Distance between sample and detector',
                               Readable),
    }

    def _dev(self, dev, scale=1):
        return dev.fmtstr % (dev.read(0) / scale)

    def _prepare_params(self):
        params = [
            'lam=%s' % self._dev(self._attached_l_ambda),
            'dlam=%.2f' % (self._attached_d_lambda.read(0) *
                           self._attached_l_ambda.read(0) / 100),
            'table_x=%s' % self._dev(self._attached_tablex),
            'table_y=%s' % self._dev(self._attached_tabley),
            'table_z=%s' % self._dev(self._attached_tablez),
            'table_rotx=%s' % self._dev(self._attached_table_rotx),
            'table_roty=%s' % self._dev(self._attached_table_roty),
            'table_rotz=%s' % self._dev(self._attached_table_rotz),
            # Param: Inse=0
            'Inse=%s' % self._dev(self._attached_i_nse),
            'detectorangle=%s' % self._dev(self._attached_detectorangle),
            'samplenum=%d' % self._attached_sample.sampletype,
            # Param: sourceopen=10
            # Param: foil_dist=0.0,0.00685,0.00455,-1,-1,0.0046,0.00455,0.00658
            # Param: coilrotation=0
            # Param: math_field=1
            # Param: f1=4500
            'f1=%s' % self._dev(self._attached_f1),
            # Param: f2=6200
            'f2=%s' % self._dev(self._attached_f2),
            'psd_dist=%s' % self._dev(self._attached_psd_distance),
        ]
        # Param: l1=1.87
        if self._attached_l1:
            params.append('l1=%s' % self._dev(self._attached_l1))
        # Param: l2=4.95
        if self._attached_l2:
            params.append('l2=%s' % self._dev(self._attached_l2))
        # Param: coilnselen=1
        if self._attached_coil_nse_len:
            params.append('coilnselen=%s' % self._dev(
                self._attached_coil_nse_len))
        return params

    def _getNeutronsToSimulate(self):
        n = self.neutronspersec * self.preselection
        if self._attached_sample.sampletype == 1:
            # Scaling factor for simulation runs with different sample types
            # determined by test runs
            n /= (85 / 70)
        return n


class McStasImage(BaseImage):
    """Image channel based on McStas simulation."""

    parameters = {
        'mode': Param('Data acquisition mode (tof or image)',
                      type=oneof('image', 'tof'), settable=True,
                      category='presets'),
        'roi': Param('Region of interest, given as (x1, y1, x2, y2)',
                     type=tupleof(intrange(-1, 1024), intrange(-1, 1024),
                                  intrange(-1, 1024), intrange(-1, 1024)),
                     default=(-1, -1, -1, -1), settable=True),
        'tofchannels': Param('Total number of TOF channels to use',
                             type=intrange(1, 1024), default=128,
                             settable=True, category='presets'),
        'foilsorder': Param('Usable foils, ordered by number. Must match the '
                            'number of foils configured in the server!',
                            type=listof(intrange(0, 31)), settable=False,
                            default=[0, 1, 2, 3, 4, 5, 6, 7],
                            category='instrument'),
        'foils': Param('Number of spaces for foils in the TOF data',
                       type=intrange(1, 32), default=8, category='instrument'),
        'fitfoil': Param('Foil for contrast fitting (number BEFORE resorting)',
                         type=int, default=0, settable=True),
    }

    parameter_overrides = {
        'size': Override(type=tupleof(intrange(1, 1024), intrange(1, 1024)),
                         default=(128, 128), mandatory=False),
        'mcstasfile': Override(default='cascade.bin', mandatory=False),
    }

    fitter = MiezeFit()

    _datashape = []

    def doInit(self, mode):
        self._xres, self._yres = self.size

    def doStart(self):
        self.readresult = [0, 0]
        BaseImage.doStart(self)

    def valueInfo(self):
        if self.mode == 'tof':
            return (Value(self.name + '.roi', unit='cts', type='counter',
                          errors='sqrt', fmtstr='%d'),
                    Value(self.name + '.total', unit='cts', type='counter',
                          errors='sqrt', fmtstr='%d'),
                    Value('fit.contrast', unit='', type='other',
                          errors='next', fmtstr='%.3f'),
                    Value('fit.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('fit.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('fit.avgErr', unit='', type='error',
                          errors='none', fmtstr='%.1f'),
                    Value('fit.phase', unit='', type='other', errors='next',
                          fmtstr='%.3f'),
                    Value('fit.phaseErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('roi.contrast', unit='', type='other',
                          errors='next', fmtstr='%.3f'),
                    Value('roi.contrastErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'),
                    Value('roi.avg', unit='', type='other', errors='next',
                          fmtstr='%.1f'),
                    Value('roi.avgErr', unit='', type='error',
                          errors='none', fmtstr='%.1f'),
                    Value('roi.phase', unit='', type='other', errors='next',
                          fmtstr='%.3f'),
                    Value('roi.phaseErr', unit='', type='error',
                          errors='none', fmtstr='%.3f'))
        return (Value(self.name + '.roi', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),
                Value(self.name + '.total', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'))

    @property
    def arraydesc(self):
        if self.mode == 'image':
            return ArrayDesc(self.name, self._datashape, '<u4', ['X', 'Y'])
        return ArrayDesc(self.name, self._datashape, '<u4', ['X', 'Y', 'T'])

    def _readpsd(self, quality):
        try:
            def import_cascade_bin(path_to_result_dir):
                """Return a 'self.size' numpy array."""
                p = Path(path_to_result_dir).joinpath(self.mcstasfile)
                if p.exists():
                    return np.squeeze(np.fromfile(
                        str(p), dtype=np.dtype((np.double, self.size))))
                self.log.warning('No file: %s', p)
                return np.zeros((self.tofchannels, ) + self.size)

            factor = self._attached_mcstas._getScaleFactor()
            if hasattr(self._attached_mcstas, '_mcstasdirpath'):
                buf = import_cascade_bin(self._attached_mcstas._mcstasdirpath)
                self._buf = (buf * factor).astype(np.uint32)
            else:
                self._buf = np.zeros((self.tofchannels, ) + self.size)
        except OSError:
            if quality != LIVE:
                self.log.exception('Could not read result file', exc=1)

        total = self._buf.sum()
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = self._buf[..., y1:y2, x1:x2].sum()
        else:
            x1, y1, x2, y2 = 0, 0, self._buf.shape[-1], self._buf.shape[-2]
            roi = total
        if self.mode == 'image':
            self.readresult = [roi, total]

        # demux timing into foil + timing
        nperfoil = self._datashape[0] // len(self.foilsorder)
        shaped = self._buf.reshape(
            (len(self.foilsorder), nperfoil) + self._datashape[1:])

        x = np.arange(nperfoil)
        ty = shaped[self.fitfoil].sum((1, 2))
        ry = shaped[self.fitfoil, :, y1:y2, x1:x2].sum((1, 2))

        self.log.debug('fitting %r and %r' % (ty, ry))

        tres = self.fitter.run(x, ty, None)
        if tres._failed:
            self.log.warning(tres._message)
        else:
            self.log.debug('total result is %s +/- %r for [avg, contrast, '
                           'freq, phase]', tres, tres._pars[2])

        rres = self.fitter.run(x, ry, None)
        if rres._failed:
            self.log.warning(rres._message)
        else:
            self.log.debug('ROI result is %s +/- %r for [avg, contrast, freq, '
                           'phase]', rres, rres._pars[2])

        self.readresult = [
            roi, total,
            abs(tres.contrast), tres.dcontrast, tres.avg, tres.davg,
            tres.phase, tres.dphase,  # tres.freq, tres.dfreq,
            abs(rres.contrast), rres.dcontrast,rres.avg, rres.davg,
            rres.phase, rres.dphase,  # rres.freq, rres.dfreq,
        ]

        # also fit per foil data and pack everything together to be send via
        # cache for display
        payload = []
        for foil in self.foilsorder:
            foil_tot = shaped[foil].sum((1, 2))
            foil_roi = shaped[foil, :, y1:y2, x1:x2].sum((1, 2))
            tres = self.fitter.run(x, foil_tot, None)
            rres = self.fitter.run(x, foil_roi, None)
            if not tres._failed and not rres._failed:
                payload.append([
                    tres._pars[1], tres._pars[2], foil_tot.tolist(),
                    rres._pars[1], rres._pars[2], foil_roi.tolist(),
                ])
            else:
                payload.append([[0.] * 4, [0.] * 4, foil_tot.tolist(),
                                [0.] * 4, [0.] * 4, foil_roi.tolist()])
        self.log.debug('payload: %r', payload)
        self._cache.put(self.name, '_foildata', payload, flag=FLAG_NO_STORE)

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and self.size or (
            self.size + (self.tofchannels,))
        self._tres = (value == 'image') and 1 or self.tofchannels

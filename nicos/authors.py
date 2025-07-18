# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

authors_list = '''\
NICOS is maintained by:

* Georg Brandl <g.brandl@fz-juelich.de>
* Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
* Christian Felder <c.felder@fz-juelich.de>
* Jens Krüger <jens.krueger@frm2.tum.de>
* Björn Pedersen <bjoern.pedersen@frm2.tum.de>

Contributors:

* Nikolas Arend <n.arend@fz-juelich.de>
* Josef Baudisch <josef.baudisch@frm2.tum.de>
* Nikhil Biyani <nikhil.biyani@psi.ch>
* Pierre Boillat <pierre.boillat@psi.ch>
* Matt Clarke <matt.clarke@ess.eu>
* Robert Georgii <robert.georgii@frm2.tum.de>
* Jonathan Haehne <jonathan.haehne@frm2.tum.de>
* Moritz Hannemann <m.hannemann@fz-juelich.de>
* Ümit Hardal <umit.hardal@ess.eu>
* Michael Hart <michael.hart@stfc.ac.uk>
* Klaudia Hradil <klaudia.hradil@tuwien.ac.at>
* Lea Kleesattel <lea.kleesattel@frm2.tum.de>
* Mark Könnecke <Mark.Koennecke@psi.ch>
* Jakob Lass <jakob.lass@gmail.com>
* Alexander Lenz <alexander.lenz@frm2.tum.de>
* Peter Link <peter.link@frm2.tum.de>
* Kenan Muric <kenan.muric@ess.eu>
* Pascal Neubert <pascal.neubert@frm2.tum.de>
* Tobias Neuwirth <tobias.neuwirth@frm2.tum.de>
* Konstantin Kholostov <k.kholostov@fz-juelich.de>
* George O'Neill <george.oneill@ess.eu>
* Adrian Potter <adrian.potter@tessella.com>
* Jörg Pulz <joerg.pulz@frm2.tum.de>
* Stefan Rainow <s.rainow@fz-juelich.de>
* Christian Randau <christian.randau@frm2.tum.de>
* Andreas Schulz <andreas.schulz@frm2.tum.de>
* Johannes Schwarz <johannes.schwarz@frm2.tum.de>
* Tobias Unruh <tobias.unruh@krist.uni-erlangen.de>
* Michael Wedel <michael.wedel@esss.se>
* Wolfgang Wein <wein@informatik.tu-muenchen.de>
* Alexander Zaft <a.zaft@fz-juelich.de>
* Markus Zolliker <markus.zolliker@psi.ch>

Instrument-specific code was contributed by:

* Stefanos Athanasopoul <stefanos.athanasopoulos@ess.eu>
* Fabian Beule <f.beule@fz-juelich.de>
* Alexander Book <alexander.book@frm2.tum.de>
* Michele Brambilla <michele.brambilla@psi.ch>
* Alexey Bykov <redi87@bk.ru>
* Daniel Cacabelos <daniel.cacabelos@ess.eu>
* Petr Čermák <cermak@mag.mff.cuni.cz>
* Goetz Eckold <geckold@gwdg.de>
* Artem Feoktystov <a.feoktystov@fz-juelich.de>
* Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
* Arno Frank <arno.frank@tuwien.ac.at>
* Jonathan Frank <jonathan.frank@frm2.tum.de>
* Christian Franz <christian.franz@frm2.tum.de>
* Weimin Gan <weimin.gan@hereon.de>
* Holger Gibhardt <hgibhar@gwdg.de>
* Artur Glavic <artur.glavic@psi.ch>
* Martin Haese <martin.haese@hereon.de>
* Michael Hofmann <michael.hofmann@frm2.tum.de>
* Markus Hölzel <markus.hoelzel@frm2.tum.de>
* Stefan Huber <stefan.huber@frm2.tum.de>
* Leonardo Ibanez <leoo.davinci@gmail.com>
* Johanna Jochum <johanna.jochum@frm2.tum.de>
* Stefanie Keuler <s.keuler@fz-juelich.de>
* Ebad Kamil <ebad.kamil@ess.eu>
* Sabrina Kirstein <s.kirstein@fz-juelich.de>
* Wiebke Lohstroh <wiebke.lohstroh@frm2.tum.de>
* Adrian Losko <adrian.losko@frm2.tum.de>
* Avishek Maity <Avishek.Maity@frm2.tum.de>
* Gaetano Mangiapia <gaetano.mangiapia@hereon.de>
* Rifai Muslih <rifai@batan.go.id>
* Thomas Müller <t.mueller@fz-juelich.de>
* Dominic Oram <dominic.oram@stfc.ac.uk>
* Dominik Petz <dominik.petz@frm2.tum.de>
* Ji Tae Park <jitae.park@frm2.tum.de>
* Jonas Petersson <jonas.petersson@ess.eu>
* Matthias Pomm <matthias.pomm@hereon.de>
* Kirill Pshenichnyi <pshcyrill@mail.ru>
* Andrew Sazonov <andrew.sazonov@frm2.tum.de>
* Philipp Schmakat <philipp.schmakat@frm2.tum.de>
* Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>
* Tobias Schrader <t.schrader@fz-juelich.de>
* Michael Schulz <michael.schulz@frm2.tum.de>
* Simon Sebold <simon.sebold@frm2.tum.de>
* Sandra Seger <sandra.seger@frm2.tum.de>
* Anatoliy Senyshyn <anatoliy.senyshyn@frm2.tum.de>
* Oleg Sobolev <oleg.sobolev@frm2.tum.de>
* Olaf Soltwedel <olaf.soltwedel@frm2.tum.de>
* Stefan Söllradl <stefan.soellradl@frm2.tum.de>
* Alexander Steffens <a.steffens@fz-juelich.de>
* Iwan Sumirat <sumirat@batan.go.id>
* Henrik Thoma <henrik.thoma@frm2.tum.de>
* Lukas Vogl <lukas.vogl@frm2.tum.de>
* Michael Wagener <m.wagener@fz-juelich.de>
* Alexander Weber <al.weber@fz-juelich.de>
* Tobias Weber <tobias.weber@frm2.tum.de>
* Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
* Aleks Wischolit <aleks.wischolit@frm2.tum.de>
* Marcell Wolf <marcell.wolf@frm2.tum.de>

Logos were contributed by:

* Ramona Schurek <r.schurek@fz-juelich.de>

It is free software, and can be distributed under the terms of the
GNU General Public license version 2 or later (see LICENSE).
'''

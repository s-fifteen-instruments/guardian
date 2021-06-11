#!/bin/sh
#
# Guardian is a quantum key distribution REST API and supporting software stack.
# Copyright (C) 2021  W. Cyrus Proctor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
set -ex

# Absolute filepath to this script
FILEPATH=$(readlink -f "${0}")
# Absolute dirpath to this script
DIRPATH=$(dirname "${FILEPATH}")

if [ "${KME}" = "kme2" ]; then
  # kme1 generates the simulated QKD epoch files
  # Transfer kme2's epoch files over and remove
  # the source files on kme1 once the transfer is
  # complete. This prevents reingestion of previously
  # ingested epoch files which can cause sync issues.
  # Ignore missing arguments suppresses the link_stat
  # error message that arises if there are no epoch
  # files to transfer.
  rsync --remove-source-files --ignore-missing-args -avz --timeout=5 \
    ${REMOTE_KME_DIRPATH:-SETMEINMAKEFILE}/volumes/kme1/qkd/epoch_files/kme2/* \
    ${DIRPATH}/../volumes/kme1/qkd/epoch_files/kme2/
fi

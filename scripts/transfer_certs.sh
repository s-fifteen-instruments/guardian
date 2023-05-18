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

mkdir -p ${DIRPATH}/../volumes/${LOCAL_KME_ID:-SETMEINMAKEFILE}/certificates/remote/${REMOTE_KME_ID:-SETMEINMAKEFILE}/rest
rsync -avz --timeout=3 \
  ${REMOTE_KME_DIRPATH:-SETMEINMAKEFILE}/volumes/${REMOTE_KME_ID:-SETMEINMAKEFILE}/certificates/production/rest/rest*cert.pem \
  ${DIRPATH}/../volumes/${LOCAL_KME_ID:-SETMEINMAKEFILE}/certificates/remote/${REMOTE_KME_ID:-SETMEINMAKEFILE}/rest/


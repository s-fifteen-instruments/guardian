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
set -x

# Absolute filepath to this script
FILEPATH=$(readlink -f "${0}")
# Absolute dirpath to this script
DIRPATH=$(dirname "${FILEPATH}")
# Check for docker daemon and docker-compose
. "${DIRPATH}/docker_check.sh"

export CONFIG_FILE="docker-compose.init.yml"
export UP="docker-compose -f \${CONFIG_FILE} up -d --build \${S} || { echo \"\${S} up failed\" ; exit 1; } "
export LOG="docker-compose -f \${CONFIG_FILE} logs \${F} \${S} || { echo \"\${S} logs failed\" ; exit 1; } "
export STOP="docker-compose -f \${CONFIG_FILE} stop \${S} || { echo \"\${S} stop failed\" ; exit 1; } "
export REMOVE="docker-compose -f \${CONFIG_FILE} rm -s -f \${S} || { echo \"\${S} remove failed\" ; exit 1; } "
export STALL="sleep \${WAIT}"
export STARTUP="${UP} && ${STALL} && ${LOG}"
export SHUTDOWN="${STALL} && ${STOP} && ${REMOVE}"


# SSH config needs to be setup
if ssh $REMOTE_KME_ADDRESS "test -d ~/code/guardian/volumes/${LOCAL_KME_ID}/qkd/epoch_files/${REMOTE_KME_ID}" ; then
  # NOTE: Only necessary when using rsync to remotely transfer keying material
  echo Remote files found
  /bin/sh ${DIRPATH}/transfer_keys.sh
  S="watcher notifier"     WAIT=5 F=   eval ${STARTUP}
  S="watcher notifier"     WAIT=1      eval ${SHUTDOWN}
  rm -rf ~/code/guardian/volumes/${LOCAL_KME_ID}/qkd/epoch_files/${REMOTE_KME_ID}
  ssh $REMOTE_KME_ADDRESS "rmdir ~/code/guardian/volumes/${LOCAL_KME_ID}/qkd/epoch_files/${REMOTE_KME_ID}"
else
  echo Remote files not found
  S=qkd                    WAIT=0 F=-f eval ${STARTUP}
  S="watcher notifier"     WAIT=5 F=   eval ${STARTUP}
  S="watcher notifier qkd" WAIT=1      eval ${SHUTDOWN}
fi


# NOTE: This assumes a Vault instance is up and unsealed.

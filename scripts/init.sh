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

# If this file exists, we've already gone through
# the whole initialization process...skip it.
if [ -f "${DIRPATH}/.initialized" ]; then
	echo "KME \"${KME}\" already initialized ... continuing"
  exit 0
fi

export CONFIG_FILE="docker-compose.${KME}.init.yml"
export UP="docker-compose -f \${CONFIG_FILE} up -d --build \${S} || { echo \"\${S} up failed\" ; exit 1; } "
export LOG="docker-compose -f \${CONFIG_FILE} logs \${F} \${S} || { echo \"\${S} logs failed\" ; exit 1; } "
export DOWN="docker-compose -f \${CONFIG_FILE} down || { echo \"\${S} down failed\" ; exit 1; } "
export STALL="sleep \${WAIT}"
export STARTUP="${UP} && ${STALL} && ${LOG}"
export SHUTDOWN="${STALL} && ${DOWN}"

docker network create traefik-public

if [ "${KME}" = "kme1" ]; then

  S=certauth           WAIT=0 F=-f eval ${STARTUP}
  S=vault              WAIT=1 F=   eval ${STARTUP}
  S=vault_init         WAIT=0 F=-f eval ${STARTUP}
  S=certauth_csr       WAIT=0 F=-f eval ${STARTUP}
  S=vault_init_phase_2 WAIT=0 F=-f eval ${STARTUP}
  S=vault_client_auth  WAIT=0 F=-f eval ${STARTUP}
  S=qkd                WAIT=0 F=-f eval ${STARTUP}
  S="watcher notifier" WAIT=1 F=   eval ${STARTUP}
                       WAIT=3      eval ${SHUTDOWN}

elif [ "${KME}" = "kme2" ]; then
  
  S=vault              WAIT=1 F=   eval ${STARTUP}
  S=vault_init         WAIT=0 F=-f eval ${STARTUP}
  S=certauth_csr       WAIT=0 F=-f eval ${STARTUP}
  S=vault_init_phase_2 WAIT=0 F=-f eval ${STARTUP}
  S=vault_client_auth  WAIT=0 F=-f eval ${STARTUP}
  S="watcher notifier" WAIT=1 F=   eval ${STARTUP}
                       WAIT=3      eval ${SHUTDOWN}

else
  echo "Unrecognized KME type: \"${KME}\""
  echo "Use \"kme1\" or \"kme2\"; exiting"
  exit -1
fi

touch "${DIRPATH}/.initialized"

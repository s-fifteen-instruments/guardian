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
export DOWN="docker-compose -f \${CONFIG_FILE} down || { echo \"\${S} down failed\" ; exit 1; } "
export STALL="sleep \${WAIT}"
export STARTUP="${UP} && ${STALL} && ${LOG}"
export SHUTDOWN="${STALL} && ${DOWN}"

# +--------------------+----------------------+-----------------+-----------------+
# |   Expression       |       parameter      |     parameter   |    parameter    |
# |   in script:       |   Set and Not Null   |   Set But Null  |      Unset      |
# +--------------------+----------------------+-----------------+-----------------+
# | ${parameter:=word} | substitute parameter | assign word     | assign word     |
# +--------------------+----------------------+-----------------+-----------------+
# Expecting a set, non-null response if the network is already present
NETWORK_PRESENT=`docker network ls -q --filter name=traefik-public`
if [ -z "${NETWORK_PRESENT}" ]; then
  echo "Creating the \"traefik-public\" network"
  docker network create traefik-public
else
  echo "The \"traefik-public\" network is already present"
fi

# SSH config needs to be setup
if ssh $REMOTE_KME_ADDRESS "test -d ${DIRPATH}/../volumes/${REMOTE_KME_ID}/qkd/epoch_files/${LOCAL_KME_ID}" ; then

  S=vault              WAIT=0 F=   eval ${STARTUP}
  S=unsealer           WAIT=0 F=   eval ${STARTUP}
  S=vault_init_phase_2 WAIT=2 F=-f eval ${STARTUP}
  S=vault_client_auth  WAIT=0 F=-f eval ${STARTUP}
  # NOTE: Only necessary when using rsync to remotely transfer keying material
  /bin/sh ${DIRPATH}/transfer_keys.sh
  S="watcher notifier" WAIT=5 F=   eval ${STARTUP}
                       WAIT=3      eval ${SHUTDOWN}

else
  
  S=vault              WAIT=0 F=   eval ${STARTUP}
  S=unsealer           WAIT=0 F=   eval ${STARTUP}
  S=vault_init_phase_2 WAIT=2 F=-f eval ${STARTUP}
  S=vault_client_auth  WAIT=0 F=-f eval ${STARTUP}
  S=qkd                WAIT=0 F=-f eval ${STARTUP}
  S="watcher notifier" WAIT=5 F=   eval ${STARTUP}
                       WAIT=3      eval ${SHUTDOWN}

fi

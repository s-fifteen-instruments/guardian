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
export STALL="sleep \${WAIT}"
export STARTUP="${UP} && ${STALL} && ${LOG}"

S=vault_clear WAIT=0 F=-f eval ${STARTUP}

# NOTE: This assumes a Vault instance is up.

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

test_dir=/tmp/guardian_test

# Absolute filepath to this script
FILEPATH=$(readlink -f "${0}")
# Absolute dirpath to this script
DIRPATH=$(dirname "${FILEPATH}")

mkdir -p ${test_dir}
cd ${test_dir}
rsync -avz ${LOCAL_KME_DIRPATH}/volumes/${LOCAL_KME_ID}/certificates/production/admin/${LOCAL_SAE_ID} ./ &
rsync -avz ${REMOTE_KME_DIRPATH}/volumes/${REMOTE_KME_ID}/certificates/production/admin/${REMOTE_SAE_ID} ./ &
wait

echo "1 key; 8 bits each; 4 iterations"
${DIRPATH}/key_loop.sh 1 8 4
echo "4 keys; 8 bits each; 4 iterations"
${DIRPATH}/key_loop.sh 4 8 4
echo "1 key; 256 bits each; 4 iterations"
${DIRPATH}/key_loop.sh 1 256 4
echo "4 keys; 256 bits each; 4 iterations"
${DIRPATH}/key_loop.sh 4 256 4

echo "4 simultaneous requests; 1 key; 8 bits each; 4 iterations"
${DIRPATH}/key_loop.sh 1 8 4 &
${DIRPATH}/key_loop.sh 1 8 4 &
${DIRPATH}/key_loop.sh 1 8 4 &
${DIRPATH}/key_loop.sh 1 8 4 &
wait
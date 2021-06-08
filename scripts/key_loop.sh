#!/bin/bash
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

if [ "$#" -ne 3 ]; then
    echo "Illegal number of command-line arugments"
    echo "First Argument: Number of keys to request"
    echo "Second Argument: Size of keys in bits"
    echo "Third Arugments: Number of iterations to run" 
    exit -1
fi
# Number of keys to request
N=${1}
# Size of keys in bits
S=${2}
# Number of loop iterations
NLOOP=${3}

# Absolute filepath to this script
FILEPATH=$(readlink -f "${0}")
# Absolute dirpath to this script
DIRPATH=$(dirname "${FILEPATH}")

for i in `seq 1 ${NLOOP}`; do 
  printf "$i: "
  ${DIRPATH}/key_compare.sh ${N} ${S}
  return_code=$?
  if [ "${return_code}" -ne 0 ];then
    echo "FAIL"
  else
    echo "PASS"
  fi
done

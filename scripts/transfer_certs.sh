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

if [ "${KME}" = "kme1" ]; then
  mkdir -p /home/alice/code/guardian/volumes/kme2/certificates/production/rest
  rsync -avz bob@kme2:/home/bob/code/guardian/volumes/kme2/certificates/production/rest/rest.ca-chain.cert.pem /home/alice/code/guardian/volumes/kme2/certificates/production/rest/rest.ca-chain.cert.pem
fi

if [ "${KME}" = "kme2" ]; then
  mkdir -p /home/bob/code/guardian/volumes/kme1/certificates/production/rest
  rsync -avz alice@kme1:/home/alice/code/guardian/volumes/kme1/certificates/production/rest/rest.ca-chain.cert.pem /home/bob/code/guardian/volumes/kme1/certificates/production/rest/rest.ca-chain.cert.pem
fi

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


docker-compose up -d --build certauth
sleep 1
docker-compose logs certauth
docker-compose up -d vault
sleep 1
docker-compose logs vault
docker-compose up -d --build vault_init
sleep 2
docker-compose logs vault_init
docker-compose up -d --build certauth_csr
sleep 1
docker-compose logs certauth_csr
docker-compose up -d --build vault_init_phase_2
sleep 2
docker-compose logs vault_init_phase_2
docker-compose up -d --build qkd
sleep 1
docker-compose logs -f qkd
docker-compose up -d --build  watcher
docker-compose up -d --build notifier
sleep 1
docker-compose logs -f notifier
docker-compose logs watcher

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

# Generate root CA certs/keys
certs: export KME = $(KME)
certs: export ACTION = CAGEN
certs:
	@echo Making Target $@
	date
	@sh gen_certs.sh

# Generate certs for CSR
csr: export ACTION = CSR
csr:
	@echo Making Target $@
	date
	@sh gen_certs.sh

# Copy production certs/keys to production directory
certs: export KME = $(KME)
install: export ACTION = INSTALL
install:
	@echo Making Target $@
	date
	@sh gen_certs.sh

.PHONY: clean

# Remove all certs/keys; including root/intermediate CAs
clean:
	@echo Making Target $@
	date
	@rm -rf ./root/

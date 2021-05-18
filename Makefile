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
SCRIPTS := ./scripts
SERVICES := rest
export KME ?= kme1
$(info )
$(info Using KME configuration: '$(KME)')
$(info Use the command-line syntax, e.g. 'KME=kme2' to change)
$(info )

rest: init
	$(SCRIPTS)/run.sh

init:
	$(SCRIPTS)/init.sh

log:
	$(SCRIPTS)/log.sh $(SERVICES)

down:
	$(SCRIPTS)/down.sh

keys:
	$(SCRIPTS)/keys.sh

cycle: clean rest log

.PHONY: clean allclean
allclean: export KME = both
allclean: clean
clean: down
	sudo $(SCRIPTS)/clean.sh $(KME)


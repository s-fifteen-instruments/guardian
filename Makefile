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
##########################
##### CAN CHANGE ME ######
##########################
export KME ?= kme1
##########################
##########################
##########################

##########################
##### LEAVE ME ALONE #####
##########################
SERVICES := rest
SCRIPTS := ./scripts
ifeq ($(KME), kme1)
export LOCAL_KME_ID := kme1
export REMOTE_KME_ID := kme2
else ifeq ($(KME), kme2)
export LOCAL_KME_ID := kme2
export REMOTE_KME_ID := kme1
else
$(error KME input not recognized: $(KME). Please use "kme1" or "kme2"; Exiting)
endif
$(info )
$(info Using Local KME configuration: '$(KME)')
$(info Use the command-line syntax, e.g. 'KME=kme2' to change)
$(info Environment variables used throughout Guardian:)
$(info KME: $(KME))
$(info LOCAL_KME_ID: $(LOCAL_KME_ID))
$(info REMOTE_KME_ID: $(REMOTE_KME_ID))
$(info )

# KME rest app
rest: init
	$(SCRIPTS)/run.sh

# KME initialization steps
init:
	$(SCRIPTS)/init.sh

# KME rest app docker logs
log:
	$(SCRIPTS)/log.sh $(SERVICES)

# KME rest app shutdown
down:
	$(SCRIPTS)/down.sh

# QKD simulator make more keying material
# Needs local Vault instance up and unsealed
keys: rest
	$(SCRIPTS)/keys.sh

.PHONY: clean allclean
# Clean local and remote KMEs
allclean: export KME = both
allclean: clean
# Clean local KME
clean: down
	sudo $(SCRIPTS)/clean.sh $(KME)

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
## OR SET ME IN THE ENV ##
##########################
# - Choose "kme1" or "kme2" for the local KME identity.
#   kme1 => local, kme2 => remote
export KME ?= kme1
# - Location of Local KME's guardian git repository
export LOCAL_KME_ADDRESS ?= a.qkd.internal
export LOCAL_KME_DIRPATH ?= s-fifteen@$(LOCAL_KME_ADDRESS):/home/s-fifteen/code/guardian
# - Location of Remote KME's guardian git repository
#   TODO: Verify currently only used to transfer keys (to be handled by qcrypto) and
#         transfer certs (to replace full-chain authentication with int+root ca-chain)
export REMOTE_KME_ADDRESS ?= b.qkd.internal
export REMOTE_KME_DIRPATH ?= s-fifteen@$(REMOTE_KME_ADDRESS):/home/s-fifteen/code/guardian

# NOTE:
# - Set to <username>@<hostnameORip>:<path/to/guardian/repository>
# - It is expected that passwordless SSH access is set up to this location.
# - Use a full absolute path. Do not use env variables or tilde (~) as
#   they will not necessarily expand correctly in a remote context.
##########################
##########################
##########################


##########################
##### LEAVE ME ALONE #####
##########################
SERVICES := rest
SCRIPTS := ./scripts
# Verbosity for 'compare' target
V := 0 
ifeq ($(KME), kme1)
export LOCAL_KME_ID := kme1
export REMOTE_KME_ID := kme2
export LOCAL_SAE_ID := sae1
export REMOTE_SAE_ID := sae2
else ifeq ($(KME), kme2)
export LOCAL_KME_ID := kme2
export REMOTE_KME_ID := kme1
export LOCAL_SAE_ID := sae2
export REMOTE_SAE_ID := sae1
else
$(error KME input not recognized: $(KME). Please use "kme1" or "kme2"; Exiting)
endif
$(info )
$(info Using Local KME configuration: '$(KME)')
$(info Use the command-line syntax, e.g. 'KME=kme2' to change)
$(info )
$(info Remote KME Repository Location: '$(REMOTE_KME_DIRPATH)')
$(info Use the command-line syntax, e.g. 'REMOTE_KME_DIRPATH=alice@kme1:/home/alice/code/guardian' to change)
$(info )
$(info Environment variables used throughout Guardian:)
$(info KME: $(KME))
$(info LOCAL_KME_ID: $(LOCAL_KME_ID))
$(info REMOTE_KME_ID: $(REMOTE_KME_ID))
$(info LOCAL_SAE_ID: $(LOCAL_SAE_ID))
$(info REMOTE_SAE_ID: $(REMOTE_SAE_ID))
$(info )

# Not strictly necessary but this
# Makefile is not intended to be
# run in parallel.
.NOTPARALLEL:

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

# Requires both local and remote
# REST APIs up and running.
compare:
ifneq ($(LOCAL_KME_ID), kme1)
	$(error Illegal KME configuration: $(KME) for compare target. Please run from "kme1"; Exiting)
endif
	$(SCRIPTS)/compare.sh $(V)

# Reset local Vault instance
# Needs local Vault instance up and unsealed
clear: rest
	$(SCRIPTS)/clear.sh

.PHONY: clean allclean
# Clean local and remote KMEs
allclean: export KME = both
allclean: clean
# Clean local KME
clean: down
	sudo $(SCRIPTS)/clean.sh $(KME)

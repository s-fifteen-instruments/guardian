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
#export KME ?= kme1
# - Location of Local KME's guardian git repository
export LOCAL_KME_ADDRESS ?= e.qkd.internal
export LOCAL_KME_DIRPATH ?= s-fifteen@$(LOCAL_KME_ADDRESS):/home/s-fifteen/code/guardian
# - Location of Remote KME's guardian git repository
#   TODO: Verify currently only used to transfer keys (to be handled by qcrypto) and
#         transfer certs (to replace full-chain authentication with int+root ca-chain)
export LOCAL_KME_ID ?= KME-S15-Guardian-005-Guardian.Faiz
export LOCAL_SAE_ID := SAE-S15-Test-005-sae5
export LOCAL_QKDE_ID := QKDE0005

export REMOTE_KME ?= 1# or 2
ifeq ($(REMOTE_KME), 1)
export REMOTE_KME_ADDRESS ?= c.qkd.internal
export REMOTE_KME_DIRPATH ?= root@$(REMOTE_KME_ADDRESS):/root/code/guardian
export REMOTE_KME_ID ?= KME-S15-Guardian-003-Guardian.Charlie
export REMOTE_SAE_ID := SAE-S15-Test-003-sae3
export REMOTE_QKDE_ID := QKDE0003
else ifeq ($(REMOTE_KME), 2)
export REMOTE_KME_ADDRESS ?= d.qkd.internal
export REMOTE_KME_DIRPATH ?= root@$(REMOTE_KME_ADDRESS):/root/code/guardian
export REMOTE_KME_ID ?= KME-S15-Guardian-004-Guardian.Daud
export REMOTE_SAE_ID := SAE-S15-Test-004-sae4
export REMOTE_QKDE_ID := QKDE0004
else
$(error REMOTE_KME input not recognized: $(REMOTE KME). Please use "1" or "2"; Exiting)
endif
# NOTE:
# - Set to <username>@<hostnameORip>:<path/to/guardian/repository>
# - It is expected that passwordless SSH access is set up to this location.
# - Use a full absolute path. Do not use env variables or tilde (~) as
#   they will not necessarily expand correctly in a remote context.
export LOCAL_KME_IP ?= $(shell ping -c1 $(LOCAL_KME_ADDRESS) | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p' )
export REMOTE_KME_IP ?= $(shell ping -c1 $(REMOTE_KME_ADDRESS) | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p' )
##########################
##########################
##########################


##########################
##### GET DEVICE PATHS####
##########################
#tmst_dev := $(shell ls /dev/ioboards/usbtmst0 )
#serial_devs := $(shell echo -e [ ;\
#            for dev in /dev/serial/by-id/* ;\
#            do echo -e "\'$$dev:$$dev\' " ; \
#            done ; \
#            echo -e ] ; )
#
#serial_devs := $(patsubst %comma, %] , $(serial_devs))
#devices := $(patsubst [,[ '$(tmst_dev)', $(serial_devs))
#dev_pl_holder := DEV_PLACE_HOLDER
#
#dev_inject:
#ifeq (,$(wildcard ./docker-compose.yml))
#	@echo "Creating docker-compose.yml"
#	@sed  "s!$(dev_pl_holder)!$(devices)!" < docker-compose.yml.template > docker-compose.yml
#	@sed -i "s/' '/', '/g"  docker-compose.yml
#endif
##########################
##### LEAVE ME ALONE #####
##########################
SERVICES := rest
SCRIPTS := ./scripts
# Verbosity for 'compare' target
V := 0 


$(info )
$(info Environment variables used throughout Guardian:)
$(info LOCAL_KME_ID: $(LOCAL_KME_ID))
$(info REMOTE_KME_ID: $(REMOTE_KME_ID))
$(info LOCAL_SAE_ID: $(LOCAL_SAE_ID))
$(info REMOTE_SAE_ID: $(REMOTE_SAE_ID))
$(info LOCAL_KME_HASH: $(LOCAL_KME_HASH))
$(info )

# Not strictly necessary but this
# Makefile is not intended to be
# run in parallel.
.NOTPARALLEL:

# Force usage of frozen pip requirements
frozen_requirements:
	find . -type f -name "Dockerfile" -print0 | xargs -0 sed -i "s/requirements.txt/requirements.freeze.txt/g"
	# Ignore libraries in rest with no version constraint
	sed -i '/uvicorn\[standard\]/d' rest/Dockerfile

# KME rest app
rest: init
	$(SCRIPTS)/run.sh

# KME initialization steps

init:
ifeq (,$(wildcard volumes/$(LOCAL_KME_ID)))
	cp -pr volumes/kme1 volumes/$(LOCAL_KME_ID)
	sed -i 's/{{ env "LOCAL_KME_ID" }}/$(LOCAL_KME_ID)/g' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	sed -i 's/{{ env "LOCAL_KME_ADDRESS" }}/$(LOCAL_KME_ADDRESS)/g' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	sed -i 's/{{ env "LOCAL_SAE_ID" }}/MYsaeCN/g' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
endif
	$(SCRIPTS)/init.sh

connect:
ifeq (,$(wildcard volumes/$(REMOTE_KME_ID)))
	mkdir -pv volumes/$(REMOTE_KME_ID)/certificates/production/rest
	mkdir -pv volumes/$(REMOTE_KME_ID)/qkd/epoch_files
endif
	sed -n -i 'p; s/{{ env "REMOTE_KME_ID" }}/$(REMOTE_KME_ID)/p' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	sed -i "/$(REMOTE_KME_ID)/s/^#//" ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	$(SCRIPTS)/connect.sh

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
allclean: clean
	docker volume prune -f
	sudo find volumes -maxdepth 1 -type d -not \( -name "kme1" -or -name "kme2" -or -name "volumes" \) -exec rm -rf {} +

# Clean local KME

clean: down
	$(SCRIPTS)/clean.sh


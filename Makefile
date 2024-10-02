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
# Location of local and remote KME's guardian git repository
# - For transferring REST client certificates for inter-KME communication.
# - Passwordless SSH access must be set up to the remote directory.
export LOCAL_KME_ADDRESS ?= qkde0002.public
export LOCAL_KME_ADD_SSH ?= qkde0002.internal
export REMOTE_KME_ADDRESS ?= qkde0001.public
export REMOTE_KME_ADD_SSH ?= qkde0001.internal
export REMOTE_KME_DIR_SSH ?= qitlab@$(REMOTE_KME_ADD_SSH):/home/qitlab/programs/software/s-fifteen/guardian

# Identity strings for QKDE and KME, with an initial local SAE bootstrapped, swap at remote
export LOCAL_QKDE_ID ?= QKDE0002
export LOCAL_KME_ID ?= KME-S15-Guardian-002-Guardian
export LOCAL_SAE_ID ?= SAE-S15-Test-002-sae1
export REMOTE_QKDE_ID ?= QKDE0001
export REMOTE_KME_ID ?= KME-S15-Guardian-001-Guardian

# Path used only for key comparison tests, *no need to modify* if not performing out-of-band tests
export LOCAL_KME_DIRPATH  ?= s-fifteen@$(LOCAL_KME_ADDRESS):/home/s-fifteen/code/guardian
export REMOTE_KME_DIRPATH ?= s-fifteen@$(REMOTE_KME_ADDRESS):/home/s-fifteen/code/guardian
##########################
##########################
##########################


##########################
##### GET DEVICE PATHS####
##########################
tmst_dev := $(shell ls /dev/ioboards/usbtmst0 2>/dev/null)
serial_devs := $(shell echo -e [ ;\
            for dev in /dev/serial/by-id/* ;\
            do echo -e "\'$$dev:$$dev\' " ; \
            done ; \
            echo -e ] ; )

serial_devs := $(patsubst %comma, %] , $(serial_devs))
devices := $(patsubst [,[ '$(tmst_dev)', $(serial_devs))
dev_pl_holder := DEV_PLACE_HOLDER

dev_inject:
ifeq (,$(wildcard ./docker-compose.yml))
	@echo "Creating docker-compose.yml"
	@sed  "s!$(dev_pl_holder)!$(devices)!" < docker-compose.yml.template > docker-compose.yml
	@sed -i "s/' '/', '/g"  docker-compose.yml
endif
##########################
##### LEAVE ME ALONE #####
##########################

# Map domain name to IP address for /etc/hosts injection into containers
export LOCAL_KME_IP2 ?= $(shell ping -c1 $(LOCAL_KME_ADD_SSH) | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p' )
export LOCAL_KME_IP ?= $(shell ping -c1 $(LOCAL_KME_ADDRESS) | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p' )
export REMOTE_KME_IP2 ?= $(shell ping -c1 $(REMOTE_KME_ADD_SSH) | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p' )
export REMOTE_KME_IP ?= $(shell ping -c1 $(REMOTE_KME_ADDRESS) | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p' )

LOCAL_REPO_DIRPATH := $(word 2, $(subst :, ,$(LOCAL_KME_DIRPATH)))
SERVICES := rest
SCRIPTS := ./scripts
# Verbosity for 'compare' target
V := 0 
$(info )
$(info Environment variables used throughout Guardian:)
$(info LOCAL_KME_ID: $(LOCAL_KME_ID))
$(info REMOTE_KME_ID: $(REMOTE_KME_ID))
$(info LOCAL_SAE_ID: $(LOCAL_SAE_ID))
$(info LOCAL_KME_IP: $(LOCAL_KME_IP))
$(info REMOTE_KME_IP: $(REMOTE_KME_IP))
$(info REMOTE_KME_IP2: $(REMOTE_KME_IP2))
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
rest: init dev_inject
	$(SCRIPTS)/run.sh

# KME initialization steps
init: dev_inject
ifeq (,$(wildcard volumes/$(LOCAL_KME_ID)))
	@if ! [ "$(shell id -u)" = 0 ]; then \
		echo "Operation cancelled. Please run 'make init' as 'root', in order to copy permissions correctly."; \
		exit 1; \
	fi
	cp -pr volumes/kme1 volumes/$(LOCAL_KME_ID)
	sed -i 's:{{ env "LOCAL_REPO_DIRPATH" }}:$(LOCAL_REPO_DIRPATH):g' ./volumes/$(LOCAL_KME_ID)/vault/logs/logrotate.conf
	sed -i 's/{{ env "LOCAL_KME_ID" }}/$(LOCAL_KME_ID)/g' ./volumes/$(LOCAL_KME_ID)/vault/logs/logrotate.conf
	sed -i 's:{{ env "LOCAL_REPO_DIRPATH" }}:$(LOCAL_REPO_DIRPATH):g' ./volumes/$(LOCAL_KME_ID)/vault/logs/logrotate.sh
	sed -i 's/{{ env "LOCAL_KME_ID" }}/$(LOCAL_KME_ID)/g' ./volumes/$(LOCAL_KME_ID)/vault/logs/logrotate.sh
	sed -i 's/{{ env "LOCAL_KME_ID" }}/$(LOCAL_KME_ID)/g' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	sed -i 's/{{ env "LOCAL_KME_ADDRESS" }}/$(LOCAL_KME_ADDRESS)/g' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	sed -i 's/{{ env "LOCAL_SAE_ID" }}/$(LOCAL_SAE_ID)/g' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
endif
	$(SCRIPTS)/init.sh

connect:
ifeq (,$(wildcard volumes/$(REMOTE_KME_ID)))
	mkdir -pv volumes/$(LOCAL_KME_ID)/certificates/remote/$(REMOTE_KME_ID)/certificates/rest
endif
	sed -n -i 'p; s/{{ env "REMOTE_KME_ID" }}/$(REMOTE_KME_ID)/p' ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	sed -i "/$(REMOTE_KME_ID)/s/^#//" ./volumes/$(LOCAL_KME_ID)/traefik/configuration/traefik.d/tls.yml
	$(SCRIPTS)/connect.sh

# KME rest app docker logs
log: dev_inject 
	$(SCRIPTS)/log.sh $(SERVICES)

# KME rest app shutdown
down: dev_inject
	$(SCRIPTS)/down.sh

# QKD simulator make more keying material
# Needs local Vault instance up and unsealed
keys: rest dev_inject
	$(SCRIPTS)/keys.sh

# Requires both local and remote
# REST APIs up and running.
compare: dev_inject
ifneq ($(LOCAL_KME_ID), kme1)
	$(error Illegal KME configuration: $(KME) for compare target. Please run from "kme1"; Exiting)
endif
	$(SCRIPTS)/compare.sh $(V)

# Reset local Vault instance
# Needs local Vault instance up and unsealed
clear: rest dev_inject
	$(SCRIPTS)/clear.sh

.PHONY: clean allclean
# Clean local KME of all configs and images except Makefile changes
allclean: clean
	rm -f common/CERTAUTH_SECRETS common/CERTAUTH_CONFIG docker-compose.yml
	docker volume prune -f

# Clean local KME
clean: down
	sudo $(SCRIPTS)/clean.sh
	sudo find volumes -maxdepth 1 -type d -not \( -name "kme1" -or -name "volumes" \) -exec rm -rf {} +

#Force watcher to restart
restart_watcher:
	docker stop guardian-watcher-1
	sleep 1
	docker-compose -f docker-compose.yml up -d --build watcher

#Force qkd to restart
restart_qkd:
	docker stop qkd
	sleep 7
	docker rm qkd
	docker-compose -f docker-compose.yml up -d --build qkd

generate_sample_certs: generate_config
	$(SCRIPTS)/generate_sample_certs.sh

generate_config:
	$(SCRIPTS)/generate_config.sh

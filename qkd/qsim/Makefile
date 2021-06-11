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
# Work line that preserves built binaries and removes output files:
# make clean && make ctest
#
# Typical work line that removes output files and binaries:
# make allclean && make ctest
#
# Work line that removes all output files and binaries:
# make distclean && make ctest
#
# Set compiler via CC environment variable on command-line, e.g.
# make allclean && make ctest CC=clang
# make allclean && make ctest CC=icc
# make allclean && make ctest CC=gcc
#
SHELL := /bin/bash
setup: link

link: esim
	ln -sf ./src/esim

esim:
	+$(MAKE) -C ./src

ctest: clean link
	./run_esim
	./run_chopper lec
	./run_chopper2 hec
	./run_getrate hec
	./run_getrate lec
	./run_pfind
	./run_costream
	./run_splicer
	./run_ec
	./run_copy hec
	./run_copy lec

.PHONY: clean allclean distclean
clean:
	rm -rf hec
	rm -rf lec
	rm -f *.pipe
	rm -f *.log
	rm -f *_tlog
	rm -f *.out
	rm -f *.bin
	find -type d \( -name "*.hec" -o -name "*.lec" \) -exec rm -rf {} + 
	+$(MAKE) -C ./src clean

allclean: clean
	rm -f esim
	# Only delete copied epoch files here; otherwise, can lead to removal
	# and desync between local and remote KMEs because epoch files were
	# destroyed before consumed by the other side.
	rm -rf ./epoch_files/*
	+$(MAKE) -C ./src allclean

distclean: allclean
	+$(MAKE) -C ./src distclean

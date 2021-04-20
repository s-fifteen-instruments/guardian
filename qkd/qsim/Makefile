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
	/usr/bin/time -v ./run_esim
	/usr/bin/time -v ./run_chopper lec
	/usr/bin/time -v ./run_chopper2 hec
	/usr/bin/time -v ./run_getrate hec
	/usr/bin/time -v ./run_getrate lec
	/usr/bin/time -v ./run_pfind
	/usr/bin/time -v ./run_costream
	/usr/bin/time -v ./run_splicer
	/usr/bin/time -v ./run_ec
	/usr/bin/time -v ./run_copy hec

.PHONY: clean allclean distclean
clean:
	rm -rf hec
	rm -rf lec
	rm -f *.pipe
	rm -f *.log
	rm -f *_tlog
	rm -f *.out
	rm -f *.bin
	rm -f ./epoch_files/*
	find -type d \( -name "*.hec" -o -name "*.lec" \) -exec rm -rf {} + 
	+$(MAKE) -C ./src clean

allclean: clean
	rm -f esim
	+$(MAKE) -C ./src allclean

distclean: allclean
	+$(MAKE) -C ./src distclean

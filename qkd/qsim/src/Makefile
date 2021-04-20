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
# Typical work line:
# make clean && make
#
# Set compiler via CC environment variable on command-line, e.g.
# make clean && make CC=clang
# make clean && make CC=icc
# make clean && make CC=gcc
#
# For expensive debugging statements, enable CFLAGS_DEBUG within CFLAGS
#
SHELL := /bin/bash
CC := gcc
CFLAGS_DEBUG := -g -DDEBUG
CFLAGS := -flto -mtune=native -march=native -Wall -Ofast # $(CFLAGS_DEBUG)
INCLUDES :=
LFLAGS :=
LIBS := -lm
SRCS := event_simulator.c pcg.c
OBJS := $(SRCS:.c=.o)
MAIN := esim

.PHONY: clean allclean distclean

all: $(MAIN)

$(MAIN): $(OBJS)
	$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

.c.o:
	$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
	$(RM) *.log *.out *.bin *.o *~

allclean: clean
	$(RM) $(MAIN)

depend: $(SRCS)
	makedepend $(INCLUDES) $^

distclean: allclean

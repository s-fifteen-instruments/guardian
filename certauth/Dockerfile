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
FROM alpine:3.14.0
LABEL author="Cyrus Proctor"

# Create a vault user and group plus a vault client first so the IDs get
# set the same way, even as the rest of this may change over time.
RUN addgroup vault                          && \
    adduser -S vault -G vault --uid 100     && \
    adduser -S vaultinit -G vault --uid 101 && \
    mkdir -p /certificates                  && \
    apk add --no-cache                         \
    openssl                                    \
    make

VOLUME /certificates

# Do not "make clean" unless to remove
# root CA and intermediate CA entirely
CMD ["make certs", "make install"]

ENTRYPOINT ["/bin/sh", "-c"]

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
FROM python:3-alpine
LABEL author="Cyrus Proctor"

COPY ["./vault_init_config.py", "./requirements.txt", "./"]

# Create a vault user and group plus a vault client first so the IDs get
# set the same way, even as the rest of this may change over time.
RUN addgroup vault                                       && \
    adduser --system vaultinit --ingroup vault --uid 101 && \
    mkdir -p /certificates                               && \
    pip install --no-cache-dir -r ./requirements.txt

VOLUME /certificates
VOLUME /vault/policies

# USER vaultinit

COPY ["./vault_init.py", "./vault_auth.py", "./"]

CMD ["vault_init.py"]

ENTRYPOINT ["python"]

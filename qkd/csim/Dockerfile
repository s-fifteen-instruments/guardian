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
FROM python:3.9-alpine
LABEL author="Justin Peh"

# NOTE: 0 does not imply a false value
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/root
ENV TOP_DIR=./qkd/csim

# Set a volume to the epoch file directory to process
VOLUME ["/epoch_files"]

# Install dependencies
RUN apk add git envsubst
COPY ["${TOP_DIR}/requirements.txt", "${HOME}/"]
RUN pip install --no-cache-dir -r ${HOME}/requirements.txt

COPY ["${TOP_DIR}/simulate_keygen.py", "${HOME}/"]
COPY ["${TOP_DIR}/entrypoint.sh", "${HOME}/"]

# Set a working directory into the image
WORKDIR ${HOME}/

# Set the scripts for the python entrypoint to run
ENTRYPOINT ["/root/entrypoint.sh"]


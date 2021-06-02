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
FROM alpine:latest
LABEL author="Cyrus Proctor"

# NOTE: 0 does not imply buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/root
ENV TOP_DIR=./notifier
ENV COMMON_DIR=./common

COPY ["${TOP_DIR}/requirements.txt", "${HOME}/"]

# Set a volume to the epoch file directory to process
VOLUME /epoch_files

RUN apk update --no-cache \
    && apk add --no-cache \
        python3 \
        py-pip \
#    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ${HOME}/requirements.txt \
    && mkdir -p ${HOME}/code/notifier \
    && cd ${HOME}/code/notifier

COPY ["${COMMON_DIR}/global_config.py", "${COMMON_DIR}/notifier_config.py", "${TOP_DIR}/notifier.py", "${HOME}/code/notifier/"]

# Set a working directory into the image
WORKDIR ${HOME}/code/notifier

# Set the script for the python entrypoint to run
CMD ["notifier.py"]

ENTRYPOINT ["python3", "-u"] 

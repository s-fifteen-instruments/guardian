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

ARG CC=gcc
ENV HOME=/root
ENV TOP_DIR=./qkd
ENV COMMON_DIR=./common

# Set a volume to the location of qsim output
VOLUME ${HOME}/code/qsim/epoch_files

COPY ["${COMMON_DIR}/qkd_config", "${TOP_DIR}/qsim/", "${HOME}/code/qsim/"]
COPY ["${TOP_DIR}/rnd.c.patch", "${HOME}/code/rnd.c.patch"]

# Ensure basic packages are installed for building and running qsim
# Minor sed fixes for testing
# Build qcrypto and qsim
RUN apk update --no-cache \
    && apk add --no-cache --virtual qsim-base \
        build-base \
        gcc \
        wget \
        git \
        openssh \
    && apk add --virtual qsim-run \
        fftw-dev \
        make \
        vim \
        bash \
        grep \
        coreutils \
        python3 \
    && mkdir -p -m 0700 ${HOME}/.ssh \
    && mkdir -p ${HOME}/code \
    && cd ${HOME}/code \
    && git clone https://github.com/s-fifteen-instruments/qcrypto.git qcrypto \
    && cd ${HOME}/code/qcrypto/remotecrypto \
    && sed -i "s#/\* i f (\!inbytesread) break;  end of file reached \*/#if (\!inbytesread) break; /* end of file reached */#g" chopper.c \
    && make CC=${CC} \
    && cd ../errorcorrection \
    && mv ${HOME}/code/rnd.c.patch ./ \
    && patch rnd.c < ./rnd.c.patch \
    && make CC=${CC} \
    && cd ${HOME}/code/qsim
    # Leave building qsim for docker-compose
    # && make CC=${CC} \
    # && apk del --no-cache qsim-base

# Set a working directory into the image
WORKDIR ${HOME}/code/qsim

# Set the targets for the qsim make entrypoint to run
CMD ["clean", "ctest"]

ENTRYPOINT ["make"] 

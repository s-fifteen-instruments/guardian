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

# For updates, check:
# https://github.com/tiangolo/uvicorn-gunicorn-docker/tree/master/docker-images

FROM python:3.8-alpine3.10

LABEL maintainer="Cyrus Proctor"
LABEL originalauthorr="Sebastian Ramirez <tiangolo@gmaiil.com>"

COPY ["start.sh", "gunicorn_conf.py", "start-reload.sh", "requirements.txt", "/"]
RUN apk add --no-cache --virtual .build-deps gcc libc-dev make \
    && pip install --no-cache-dir "uvicorn[standard]" gunicorn fastapi \
    && pip install --no-cache-dir -r /requirements.txt \
    && apk del .build-deps gcc libc-dev make \
    && chmod +x /start-reload.sh \
    && chmod +x /start.sh

COPY ["./app", "/app"]
# WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh
# script (e.g. for migrations) and then will start Gunicorn with Uvicorn
CMD ["/start.sh"]

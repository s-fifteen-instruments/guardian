#!/usr/bin/env python
#
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

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable
from typing import Tuple
from global_config import GlobalSettings


class WatcherSettings(BaseSettings):
    GLOBAL: GlobalSettings = GlobalSettings()
    DELETE_EPOCH_FILES: bool = True
    CLIENT_NAME: str = "watcher"
    CLIENT_CERT_FILEPATH: str = f"{GLOBAL.CERT_DIRPATH}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}"
    CLIENT_KEY_FILEPATH: str = f"{GLOBAL.CERT_DIRPATH}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.KEY_SUFFIX}"
    NOTIFY_MAX_NUM_ATTEMPTS: int = 100
    NOTIFY_SLEEP_TIME: float = 0.5  # seconds
    NOTIFY_SLEEP_TIME_DELTA: float = 30.0  # seconds

    # Make environment settings take precedence over __init__ and file
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


settings = WatcherSettings()

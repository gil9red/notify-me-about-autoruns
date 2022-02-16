#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from pathlib import Path


DIR = Path(__file__).resolve().parent

DIR_LOGS = DIR / 'logs'
DIR_LOGS.mkdir(parents=True, exist_ok=True)

DB_DIR_NAME = DIR / 'database'
DB_DIR_NAME.mkdir(parents=True, exist_ok=True)

DB_FILE_NAME = str(DB_DIR_NAME / 'database.sqlite')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import logging
import sys

from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import DIR_LOGS, DIR


def get_logger(name: str, dir_name='logs', encoding='utf-8'):
    dir_name = Path(dir_name).resolve()
    dir_name.mkdir(parents=True, exist_ok=True)

    file_name = str(dir_name / Path(name).resolve().name) + '.log'

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = RotatingFileHandler(file_name, maxBytes=10_000_000, backupCount=5, encoding=encoding)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


log = get_logger(DIR.name, DIR_LOGS)

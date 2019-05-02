#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:26
# @File    : config.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import json


def setup(path):
    config = Config({})
    config.parse_config(path)
    CONF(config)


class Config(object):
    def __init__(self, opts):
        self._opts = opts or {}

    def parse_config(self, path):
        with open(path, 'r') as f:
            config = json.load(f)
        self._opts = config

    def __getattr__(self, attr):
        try:
            value = self._opts[attr]
            if isinstance(value, dict):
                return Config(value)
            return value
        except KeyError:
            raise AssertionError("No Such Option: %s" % attr)


class Configuration(object):
    def __init__(self, config):
        self._config = config

    def __getattr__(self, attr):
        return getattr(self._config, attr)

    def __call__(self, config):
        self._config = config


CONF = Configuration(None)
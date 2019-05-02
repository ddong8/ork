#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:04
# @File    : base_middleware.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import


class MiddleWare(object):
    def process_request(self, handler):
        pass

    def process_response(self, handler):
        pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 21:53
# @File    : __init__.py.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

from ..middleware.httpauth import HTTPAuthorization


def get_middleware():
    return [HTTPAuthorization()]
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:02
# @File    : httpauth.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import base64

from ..core import exception
from ..core import utils
from ..core.i18n import _
from .base_middleware import MiddleWare


class HTTPAuthorization(MiddleWare):

    def process_request(self, handler):
        """在业务逻辑之前对每个请求进行授权处理"""
        pass

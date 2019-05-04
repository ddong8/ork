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
        req = handler.request
        basic_auth = req.headers.get('Authorization', None)
        if basic_auth:
            basic = basic_auth.split(' ', 1)[1]
            user_pass = utils.ensure_unicode(base64.b64decode(utils.ensure_bytes(basic)))
            username, password = user_pass.split(':', 1)
            if username == 'test' and password == '123456':
                pass
            else:
                raise exception.AuthError(message=_("Basic auth username or password isn't correct!"))
        else:
            raise exception.AuthError(message=_("Missing Authorization header"))

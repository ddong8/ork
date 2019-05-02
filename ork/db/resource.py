#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:10
# @File    : resource.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import logging

from ork.db import models
from ork.db.curd import ResourceBase

LOG = logging.getLogger(__name__)


class SysOperationLog(ResourceBase):
    orm_meta = models.SysOperationLog
    _default_order = ('+uuid',)
    _primary_keys = 'uuid'
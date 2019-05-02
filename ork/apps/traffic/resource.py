#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:36
# @File    : resource.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

from ...core import utils
from ...db import models
from ...db.curd import ResourceBase


class City(ResourceBase):
    orm_meta = models.City
    _primary_keys = ('uid',)


class Line(ResourceBase):
    orm_meta = models.Line
    _primary_keys = ('uuid',)

    def _before_create(self, resource):
        resource['uuid'] = utils.generate_prefix_uuid(prefix='line-')
        return resource
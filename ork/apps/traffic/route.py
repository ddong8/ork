#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:35
# @File    : route.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

from ..traffic import controller


def add_routes(api):
    api.add_route(r"/cities", controller.CollectionCity)
    api.add_route(r"/city/(.*)", controller.ItemCity)
    api.add_route(r"/lines", controller.CollectionLine)
    api.add_route(r"/line/(.*)", controller.ItemLine)
    api.add_route(r"/", controller.Index)

    # api.add_route(r"/socket/", controller.SocketHandler),
    # api.add_route(r"/subscribe", controller.SubscribeHandler)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/3 1:19
# @File    : start_up.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from .server import tornado_server as server

if __name__ == '__main__':
    server.run()

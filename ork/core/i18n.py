#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:23
# @File    : i18n.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import gettext
import logging

LOG = logging.getLogger(__name__)


class Translator():
    """
    i18n国际化翻译器
    用户可以调用setup来更改当前locale
    """

    def __init__(self):
        self.translation = None

    def __call__(self, value):
        if self.translation:
            return self.translation.gettext(value)
        else:
            return value

    def setup(self, app, locales, lang):
        try:
            self.translation = gettext.translation(app, locales, [lang])
        except IOError:
            LOG.warning('language(%s) files not found, no translation will be used', lang)


_ = Translator()
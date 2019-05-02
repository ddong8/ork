#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:26
# @File    : base.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import fnmatch
import json
import logging
import re

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from ..core import exception
from ..core import utils
from ..core.i18n import _

LOG = logging.getLogger(__name__)


class BaseHandler(RequestHandler):
    name = ''
    resource = None

    def prepare(self):
        for middleware in self.application.middleware:
            middleware.process_request(self)

    def finish(self, chunk=None):
        for middleware in self.application.middleware:
            middleware.process_response(self)
        return super(BaseHandler, self).finish(chunk)

    def data_received(self, chunk):
        pass

    @staticmethod
    def _validate_method(req, allow_methods):
        if req.method not in allow_methods:
            raise exception.NotFoundError(code=404, title=_("Resource not Found"),
                                          description=_("resource that you request not found"))

    @staticmethod
    def _validate_data(req, data):
        if not data:
            raise exception.BodyParseError(msg=_('empty request body, a valid json document is required.'))
        try:
            body = data.decode('utf-8')
            LOG.debug("request body: %s", body)
            req.json = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            raise exception.BodyParseError(
                msg=_('malformed json, body was incorrect or not encoded as UTF-8.'))

    @staticmethod
    def _build_criteria(req, supported_filters=None):
        """
        构造过滤条件，包括filters，offset，limit
        :param req: 请求对象
        :type req: Request
        :param supported_filters: 支持参数过滤，若设置，则只允许特定字段的过滤
        :type supported_filters: list
        :returns: {'filters': filters, 'offset': offset, 'limit': limit}
        :rtype: dict
        """

        def _glob_match(pattern_filters, name):
            if pattern_filters is None or name in pattern_filters:
                return True
            for pattern_filter in pattern_filters:
                if fnmatch.fnmatch(name, pattern_filter):
                    return True
            return False

        query_dict = {}
        reg = re.compile('^(.+)\[(\d+)\]$')
        for key, value in req.arguments.items():
            matches = reg.match(key)
            if matches:
                match_key, match_index = matches.groups()
                if match_key in query_dict:
                    query_dict[match_key].append(value)
                else:
                    query_dict[match_key] = [value]
            else:
                query_dict[key] = value
        # 移除[]后缀,兼容js数组形态查询
        strip_query_dict = {}
        for key, value in query_dict.items():
            if key.endswith('[]'):
                strip_query_dict[key[:-2]] = value
            else:
                strip_query_dict[key] = value
        query_dict = strip_query_dict
        filter_mapping = {'contains': 'like', 'icontains': 'ilike',  # include
                          'istartswith': 'istarts', 'startswith': 'starts',
                          'iendswith': 'iends', 'endswith': 'ends',
                          'in': 'in', 'notin': 'nin', 'notequal': 'ne', 'equal': 'eq',  # value compare
                          'less': 'lt', 'lessequal': 'lte', 'greater': 'gt', 'greaterequal': 'gte'}
        filters = {}
        offset = None
        limit = None
        orders = None

        if query_dict is None:
            return filters, offset, limit
        if '__offset' in query_dict:
            offset = int(query_dict.pop('__offset'))
        if '__limit' in query_dict:
            limit = int(query_dict.pop('__limit'))
        if '__orders' in query_dict:
            orders = query_dict.pop('__orders')
            if utils.is_list_type(orders):
                orders = [order.strip() for order in orders]
            else:
                orders = [orders.strip()]
        for key in query_dict:
            # 没有指定支持filters或者是支持的filter，并且key是简单条件
            if supported_filters is None or key in supported_filters:
                keys = key.split('__', 1)
                if len(keys) == 1:
                    filters[key] = query_dict[key]
                else:
                    base_key, comparator = keys[0], keys[1]
                    comparator = filter_mapping.get(comparator, None)
                    if comparator:
                        if base_key in filters and isinstance(filters[base_key], dict):
                            filters[base_key] = {comparator: query_dict[key]}
                        else:
                            filters[base_key] = {comparator: query_dict[key]}
                continue
            # key是一个复杂条件
            for valid_key in supported_filters:
                if not key.startswith(valid_key + '__'):
                    continue
                base_key, comparator = key.split('__', 1)
                comparator = filter_mapping.get(comparator, None)
                if comparator and _glob_match(supported_filters, base_key):
                    if base_key in filters and isinstance(filters[base_key], dict):
                        filters[base_key][comparator] = query_dict[key]
                    else:
                        filters[base_key] = {comparator: query_dict[key]}
        return {'filters': filters, 'offset': offset, 'limit': limit, 'orders': orders}

    def make_resource(self):
        """
        get current resource.
        :param req:
        :return: current resource
        """
        return self.resource()


class BaseWebSocketHandler(WebSocketHandler):
    """
    implemented abstract method on_message
    from WebSocketHandler and data_received from RequestHandler.
    """

    def on_message(self, message):
        pass

    def data_received(self, chunk):
        pass
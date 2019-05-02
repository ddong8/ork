#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:29
# @File    : logger.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import copy
import datetime
import functools
import json
import logging

from ork.common.message import PRODUCER
from ork.core import config
from ork.core import utils
from ork.core.i18n import _
from ork.db.resource import SysOperationLog

LOG = logging.getLogger(__name__)
CONF = config.CONF


def change_log():
    """
    记录数据变化到数据历史表
    """

    def _change_log(func):
        @functools.wraps(func)
        def __change_log(resource, req, *args, **kwargs):
            record = func(resource, req, *args, **kwargs)

            def _diff(name, data_before, data_after):
                fix_data_before = copy.copy(data_before)
                fix_data_after = copy.copy(data_after)
                ignore_fields = CONF.resource.ignore_fields
                for field in ignore_fields.get(name, []):
                    fix_data_before.pop(field, None)
                    fix_data_after.pop(field, None)
                if fix_data_before != fix_data_after:
                    return True
                return False

            try:
                if resource.name and CONF.resource.change_log:
                    op = func.__name__
                    op_time = datetime.datetime.now()
                    creds = req.x_auth
                    if op == 'create':
                        SysOperationLog().create({
                            'resource': resource.name,
                            'tenant_uuid': creds['tenant'],
                            'user_name': creds['user'],
                            'operation': op,
                            'operate_time': op_time,
                            'data_before': json.loads(json.dumps(req.json, cls=utils.ComplexEncoder)),
                            'data_after': json.loads(json.dumps(record, cls=utils.ComplexEncoder))
                        }, validate=False)
                        if resource.name in CONF.message.resource:
                            routing_key = op + "." + resource.name
                            body = {
                                "data_before": json.loads(json.dumps(req.json, cls=utils.ComplexEncoder)),
                                "data_after": json.loads(json.dumps(record, cls=utils.ComplexEncoder))}
                            if CONF.message.enabled:
                                try:
                                    PRODUCER.send_message(routing_key, body)
                                except Exception as e:
                                    LOG.error(e)
                                    PRODUCER.reconnection()
                                    PRODUCER.send_message(routing_key, body)
                    elif op == 'update':
                        data_before, data_after = record
                        if _diff(resource.name, data_before, data_after):
                            SysOperationLog().create({
                                'resource': resource.name,
                                'tenant_uuid': creds['tenant'],
                                'user_name': creds['user'],
                                'operation': op,
                                'operate_time': op_time,
                                'data_before': json.loads(json.dumps(data_before, cls=utils.ComplexEncoder)),
                                'data_after': json.loads(json.dumps(data_after, cls=utils.ComplexEncoder))
                            }, validate=False)
                            if resource.name in CONF.message.resource:
                                routing_key = op + "." + resource.name
                                body = {
                                    "data_before": json.loads(json.dumps(data_before, cls=utils.ComplexEncoder)),
                                    "data_after": json.loads(json.dumps(data_after, cls=utils.ComplexEncoder))}
                                if CONF.message.enabled:
                                    try:
                                        PRODUCER.send_message(routing_key, body)
                                    except Exception as e:
                                        LOG.error(e)
                                        PRODUCER.reconnection()
                                        PRODUCER.send_message(routing_key, body)
                    elif op == 'delete':
                        count, details = record
                        for x in range(count):
                            data = json.loads(json.dumps(details[x], cls=utils.ComplexEncoder))
                            SysOperationLog().create({
                                'resource': resource.name,
                                'tenant_uuid': creds['tenant'],
                                'user_name': creds['user'],
                                'operation': op,
                                'operate_time': op_time,
                                'data_before': data,
                                'data_after': data
                            }, validate=False)
                            if resource.name in CONF.message.resource:
                                routing_key = op + "." + resource.name
                                body = {
                                    "data_before": data,
                                    "data_after": data}
                                if CONF.message.enabled:
                                    try:
                                        PRODUCER.send_message(routing_key, body)
                                    except Exception as e:
                                        LOG.error(e)
                                        PRODUCER.reconnection()
                                        PRODUCER.send_message(routing_key, body)
                    elif op == 'acquire':
                        SysOperationLog().create({
                            'resource': resource.name,
                            'tenant_uuid': creds['tenant'],
                            'user_name': creds['user'],
                            'operation': op,
                            'operate_time': op_time,
                            'data_before': json.loads(json.dumps(req.json, cls=utils.ComplexEncoder)),
                            'data_after': json.loads(json.dumps(record, cls=utils.ComplexEncoder))
                        }, validate=False)
                        if resource.name in CONF.message.resource:
                            routing_key = op + "." + resource.name
                            body = {
                                "data_before": json.loads(json.dumps(req.json, cls=utils.ComplexEncoder)),
                                "data_after": json.loads(json.dumps(record, cls=utils.ComplexEncoder))}
                            if CONF.message.enabled:
                                try:
                                    PRODUCER.send_message(routing_key, body)
                                except Exception as e:
                                    LOG.error(e)
                                    PRODUCER.reconnection()
                                    PRODUCER.send_message(routing_key, body)
                    elif op == 'release':
                        count, details = record
                        data = {'count': count, 'data': details}
                        data = json.loads(json.dumps(data, cls=utils.ComplexEncoder))
                        SysOperationLog().create({
                            'resource': resource.name,
                            'tenant_uuid': creds['tenant'],
                            'user_name': creds['user'],
                            'operation': op,
                            'operate_time': op_time,
                            'data_before': data,
                            'data_after': data
                        }, validate=False)
                        if resource.name in CONF.message.resource:
                            routing_key = op + "." + resource.name
                            body = {
                                "data_before": data,
                                "data_after": data}
                            if CONF.message.enabled:
                                try:
                                    PRODUCER.send_message(routing_key, body)
                                except Exception as e:
                                    LOG.error(e)
                                    PRODUCER.reconnection()
                                    PRODUCER.send_message(routing_key, body)
            except Exception as e:
                LOG.error(_("error while writing operation log..."))
                LOG.error(e)
            return record

        return __change_log

    return _change_log
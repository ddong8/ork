#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:36
# @File    : controller.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import datetime
import json
import logging

from ...apps.traffic import resource
from ...common.consumer import MessageConsumer
from ...common.consumer import SubscribeConsumer
from ...common.handler import CollectionHandler
from ...common.handler import ItemHandler
from ...common.handler import WSHandler

LOG = logging.getLogger(__name__)


class SocketHandler(WSHandler):

    def open(self):
        routing_key = self.get_arguments('routing_key')[0]
        self.message_consumer = MessageConsumer(routing_key)
        self.message_consumer.run(self.ws_connection)
        self.write_message(
            u"[%s]-[%s]-routing_key [%s] successfully bind!" % (
                self.request.host, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), routing_key))
        self.users.add(self)

    def on_message(self, message):
        self.write_message(message)

    def on_close(self):
        routing_key = self.get_arguments('routing_key')[0]
        self.message_consumer.stop()
        self.users.remove(self)
        LOG.info(u"[%s]-[%s]-routing_key [%s] unbind succeed!" % (
            self.request.host, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), routing_key))


class SubscribeHandler(WSHandler):

    def open(self):
        routing_key = self.get_arguments('topic')[0]
        self.message_consumer = SubscribeConsumer(routing_key)
        self.message_consumer.run(self.ws_connection)
        msg_resource = "subscribe.connected"
        msg_title = u"[%s]-[%s]-topic [%s] successfully bind!" % (
            self.request.host, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), routing_key)
        data = json.dumps({"resource": msg_resource, "title": msg_title, "body": None})
        self.write_message(data)
        self.users.add(self)

    def on_message(self, message):
        self.write_message(json.dumps({"resource": "subscribe.heartbeat", "title": "heartbeat", "body": None}))

    def on_close(self):
        routing_key = self.get_arguments('topic')[0]
        self.message_consumer.stop()
        self.users.remove(self)
        msg_resource = "subscribe.disconnected"
        msg_title = u"[%s]-[%s]-routing_key [%s] unbind succeed!" % (
            self.request.host, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), routing_key)
        data = json.dumps({"resource": msg_resource, "title": msg_title, "body": None})
        LOG.info(data)


class CollectionCity(CollectionHandler):
    name = 'traffic.city'
    resource = resource.City


class ItemCity(ItemHandler):
    name = 'traffic.city'
    resource = resource.City


class CollectionLine(CollectionHandler):
    name = 'traffic.line'
    resource = resource.Line


class ItemLine(ItemHandler):
    name = 'traffic.line'
    resource = resource.Line
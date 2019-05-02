#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:31
# @File    : consumer.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import datetime
import json
import logging

import pika
from pika.adapters.tornado_connection import TornadoConnection

from ork.core.config import CONF

LOGGER = logging.getLogger(__name__)


class MessageConsumer(object):
    EXCHANGE = CONF.message.exchange_name
    EXCHANGE_TYPE = CONF.message.exchange_type
    BROKER_URL = CONF.message.broker_url

    def __init__(self, routing_key):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._queue = None
        self._routing_key = routing_key
        self._ws = None

    def connect(self):
        LOGGER.info('Connecting to %s', self.BROKER_URL)
        return TornadoConnection(pika.URLParameters(self.BROKER_URL),
                                 self.on_connection_open)

    def close_connection(self):
        LOGGER.info('Closing connection')
        self._connection.close()

    def add_on_connection_close_callback(self):
        LOGGER.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if not self._closing:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, unused_connection):
        LOGGER.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def reconnect(self):
        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

    def add_on_channel_close_callback(self):
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def setup_exchange(self, exchange_name):
        LOGGER.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        LOGGER.info('Exchange declared')
        self.setup_queue()

    def setup_queue(self):
        LOGGER.info('Declaring queue')
        self._channel.queue_declare(self.on_queue_declareok, exclusive=True)

    def on_queue_declareok(self, method_frame):
        self._queue = method_frame.method.queue
        LOGGER.info('Binding %s to %s with %s',
                    self.EXCHANGE, self._queue, self._routing_key)
        self._channel.queue_bind(self.on_bindok, self._queue,
                                 self.EXCHANGE, self._routing_key)

    def add_on_cancel_callback(self):
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        message = u'[%s]-[%s]:[%s] more detail, click me! ||| %s' % (
            self._ws.request.host, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), basic_deliver.routing_key,
            body)

        self._ws.write_message(message)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        LOGGER.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self._queue)

    def on_bindok(self, unused_frame):
        LOGGER.info('Queue bound')
        self.start_consuming()

    def close_channel(self):
        LOGGER.info('Closing the channel')
        self._channel.close()

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self, ws):
        self._ws = ws
        self._connection = self.connect()

    def stop(self):
        LOGGER.info('Stopping')
        self._closing = True
        self.stop_consuming()
        LOGGER.info('Stopped')


class SubscribeConsumer(MessageConsumer):

    def __init__(self, routing_key):
        super(SubscribeConsumer, self).__init__(routing_key)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        msg_resource = basic_deliver.routing_key
        msg_title = u'[%s]-[%s]:[%s] more detail, click me!' % (
            self._ws.request.host, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg_resource)
        data = json.dumps({"resource": msg_resource, "title": msg_title, "body": body})
        self._ws.write_message(data)
        self.acknowledge_message(basic_deliver.delivery_tag)
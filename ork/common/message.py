#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:28
# @File    : message.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

# from __future__ import absolute_import
#
# import json
#
# import pika
#
# from ..core import config
#
# CONF = config.CONF
#
#
# class Producer(object):
#     def __init__(self):
#         self.credentials = pika.PlainCredentials(username=CONF.message.username, password=CONF.message.password)
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host=CONF.message.broker, port=CONF.message.port, credentials=self.credentials))
#         self.channel = self.connection.channel()
#         self.channel.exchange_declare(exchange=CONF.message.exchange_name, exchange_type=CONF.message.exchange_type)
#
#     def send_message(self, routing_key, body):
#         self.channel.basic_publish(exchange=CONF.message.exchange_name,
#                                    routing_key=routing_key,
#                                    body=json.dumps(body))
#
#     def reconnection(self):
#         self.credentials = pika.PlainCredentials(username=CONF.message.username, password=CONF.message.password)
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host=CONF.message.broker, port=CONF.message.port, credentials=self.credentials))
#         self.channel = self.connection.channel()
#         self.channel.exchange_declare(exchange=CONF.message.exchange_name, exchange_type=CONF.message.exchange_type)
#
#     def close(self):
#         self.connection.close()
#
#
# PRODUCER = Producer()
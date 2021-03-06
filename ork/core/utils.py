#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:21
# @File    : utils.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

import calendar
import datetime
import fnmatch
import hashlib
import inspect
import json
import os
import random
import socket
import uuid

import six


class ComplexEncoder(json.JSONEncoder):
    """加强版的JSON Encoder，支持日期、日期+时间类型的转换"""

    def default(self, obj):
        # fix, 不要使用strftime，当超过1900年时会报错
        if isinstance(obj, datetime.datetime):
            return obj.isoformat(' ').split('.')[0]
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def get_hostname():
    """
    获取主机名
    :returns: 主机名
    :rtype: string
    """
    return socket.gethostname()


def encrypt_password(password, salt):
    """
    对原始密码和盐进行加密码，返回加密密文
    :param password: 原始密码
    :type password: string
    :param salt: 盐，对加密进行干扰
    :type salt: string
    :returns: 加密密文
    :rtype: string
    """
    return hashlib.sha224(ensure_bytes(password + salt)).hexdigest()


def check_password(encrypted, password, salt):
    """
    检查密文是否由原始密码和盐加密而来，返回bool
    :param encrypted: 加密密码
    :type encrypted: string
    :param password: 原始密码
    :type password: string
    :param salt: 盐，对加密进行干扰
    :type salt: string
    :returns: 是否一致
    :rtype: bool
    """
    return encrypted == encrypt_password(password, salt)


def generate_salt(length=32):
    """
    生成随机的固定长度盐
    :param length: 盐的长度
    :type length: int
    :returns: 盐
    :rtype: string
    """
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_ []{}<>~`+=,.;:/?|'
    salt = ''
    for idx in range(length):
        salt += random.choice(chars)
    return salt


def get_function_name():
    """
    获取当前函数名
    :returns: 当前函数名
    :rtype: string
    """
    return inspect.stack()[1][3]


def walk_dir(dir_path, pattern):
    """
    递归遍历文件夹，列出所有符合pattern模式的文件
    :param dir_path: 文件夹路径
    :type dir_path: str
    :param pattern: 过滤模式
    :type pattern: str
    :returns: 文件列表
    :rtype: list
    """
    result = []
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            filename = os.path.join(root, name)
            if fnmatch.fnmatch(filename, pattern):
                result.append(filename)
    return result


def generate_uuid(dashed=True, version=1, lower=True):
    """
    创建一个随机的UUID
    :param dashed: 是否包含 - 字符
    :type dashed: bool
    :param version: UUID生成算法
    :type version: int
    :param lower: 是否小写(默认)
    :type lower: bool
    :returns: UUID
    :rtype: string
    """
    func = getattr(uuid, 'uuid' + str(version))
    if dashed:
        guid = str(func())
    else:
        guid = func().hex
    if lower:
        return guid
    return guid.upper()


def generate_prefix_uuid(prefix, length=8):
    """
    创建一个带指定前缀的类uuid标识
    :param prefix: 前缀
    :type prefix: string
    :param length: 随机串长度
    :type length: int
    :returns: UUID
    :rtype: string
    """
    uid = prefix + uuid.uuid1().hex[:length]
    return uid


def unixtime(dt_obj):
    """
    将DataTime对象转换为unix时间
    :param dt_obj: datetime.datetime 对象
    :type dt_obj: datetime.datetime
    :returns: unix时间
    :rtype: float
    """
    return calendar.timegm(dt_obj.utctimetuple())


def bool_from_string(subject, strict=False, default=False):
    """
    将字符串转换为bool值
    :param subject: 待转换对象
    :type subject: str
    :param strict: 是否只转换指定列表中的值
    :type strict: bool
    :param default: 转换失败时的默认返回值
    :type default: bool
    :returns: 转换结果
    :rtype: bool
    """
    TRUE_STRINGS = ('1', 't', 'true', 'on', 'y', 'yes')
    FALSE_STRINGS = ('0', 'f', 'false', 'off', 'n', 'no')
    if isinstance(subject, bool):
        return subject
    if not isinstance(subject, six.string_types):
        subject = six.text_type(subject)

    lowered = subject.strip().lower()

    if lowered in TRUE_STRINGS:
        return True
    elif lowered in FALSE_STRINGS:
        return False
    elif strict:
        acceptable = ', '.join(
            "'%s'" % s for s in sorted(TRUE_STRINGS + FALSE_STRINGS))
        msg = "Unrecognized value '%(val)s', acceptable values are: %(acceptable)s" % {'val': subject,
                                                                                       'acceptable': acceptable}
        raise ValueError(msg)
    else:
        return default


def is_string_type(value):
    """
    判断value是否字符类型，兼容python2、python3
    :param value: 输入值
    :type value: any
    :returns: 判断结果
    :rtype: bool
    """
    if six.PY3:
        return isinstance(value, (str, bytes))
    return isinstance(value, basestring)


def is_list_type(value):
    """
    判断value是否列表类型，兼容python2、python3
    :param value: 输入值
    :type value: any
    :returns: 判断结果
    :rtype: bool
    """
    return isinstance(value, (list, set, tuple))


def format_kwstring(templ, **kwargs):
    """
    格式化字符串
    :param templ: 待格式化的字符串
    :type templ: string
    :returns: 格式化后的字符串
    :rtype: string
    """
    return templ % kwargs


def ensure_unicode(value):
    """
    确保将输入值转换为unicode字符，兼容python2、python3
    :param value: 输入值
    :type value: string
    :returns: unicode字符串
    :rtype: `unicode`
    """
    if not is_string_type(value):
        raise ValueError('not string type')
    if six.PY2:
        return value.decode()
    elif six.PY3:
        if isinstance(value, bytes):
            return value.decode()
        else:
            return value
    raise ValueError('can not convert to unicode')


def ensure_bytes(value):
    """
    确保将输入值转换为bytes/str字符，兼容python2中返回str、python3返回bytes
    :param value: 输入值
    :type value: string
    :returns: bytes/str字符串
    :rtype: `bytes`/`str`
    """
    if not is_string_type(value):
        raise ValueError('not string type')
    if six.PY2:
        return value.encode()
    elif six.PY3:
        if isinstance(value, str):
            return value.encode()
        else:
            return value
    raise ValueError('can not convert to bytes')
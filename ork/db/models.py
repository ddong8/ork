#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:14
# @File    : models.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import absolute_import

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.declarative import declarative_base

from ..db.dictbase import DictBase
from ..db.validator import Validate
from ..db.validator import declarative_constructor

Base = declarative_base(constructor=declarative_constructor)
Validate(Base)
metadata = Base.metadata


def get_names():
    """
    获取所有Model类名
    """
    return Base._decl_class_registry.keys()


def get_class_by_name(name):
    """
    根据Model类名获取类
    :param name: Model类名
    :type name: str
    :returns: Model类
    :rtype: class
    """
    return Base._decl_class_registry.get(name, None)


def get_class_by_tablename(tablename):
    """
    根据表名获取类
    :param tablename: 表名
    :type tablename: str
    :returns: Model类
    :rtype: class
    """
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


def get_tablename_by_name(name):
    """
    根据Model类名获取表名
    :param name: Model类名
    :type name: str
    :returns: 表名
    :rtype: str
    """
    return Base._decl_class_registry.get(name, None).__tablename__


def get_name_by_class(modelclass):
    """
    根据Model类获取类名
    :param modelclass: Model类
    :type modelclass: class
    :returns: 类名
    :rtype: str
    """
    for n, c in Base._decl_class_registry.items():
        if c == modelclass:
            return n


class City(Base, DictBase):
    __tablename__ = 'city'

    attributes = ['uuid', 'id', 'name']

    uuid = Column(String(63), primary_key=True)
    id = Column(String(63), nullable=False)
    name = Column(String(255), nullable=False)


class Line(Base, DictBase):
    __tablename__ = 'line'

    attributes = ['uuid', 'id', 'name', 'city_id']

    uuid = Column(String(63), primary_key=True)
    id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    city_id = Column(String(63), nullable=False)


class SysRelationship(Base, DictBase):
    """动态关系模型"""
    __tablename__ = 'sys_relationship'

    attributes = ['id', 'name', 'display_name', 'src_resource', 'src_field', 'dst_resource', 'dst_field',
                  'index', 'one_to_many']
    detail_attributes = attributes
    summary_attributes = ['id', 'name', 'display_name']

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('relationship_id_seq'::regclass)"))
    name = Column(String(127), nullable=False)
    display_name = Column(String(127), nullable=False)
    src_resource = Column(String(255), nullable=False)
    src_field = Column(String(255), nullable=False)
    dst_resource = Column(String(255), nullable=False)
    dst_field = Column(String(255), nullable=False)
    index = Column(String(31), nullable=False, server_default=text("'btree'::character varying"))
    one_to_many = Column(Boolean, nullable=False)


class SysOperationLog(Base, DictBase):
    __tablename__ = 'sys_operation_log'
    attributes = ['resource', 'tenant_uuid', 'user_name', 'operation', 'operate_time', 'data_before', 'data_after']

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sys_operation_log_id_seq'::regclass)"))
    resource = Column(String(127), index=True, nullable=False)
    tenant_uuid = Column(String(36), index=True, nullable=False)
    user_name = Column(String(63), nullable=False)
    operation = Column(String(31), nullable=False)
    operate_time = Column(DateTime, index=True, nullable=False)
    data_before = Column(JSONB)
    data_after = Column(JSONB)
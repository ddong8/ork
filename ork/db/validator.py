#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:09
# @File    : validator.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.
"""
    sqlalchemy data type validator
"""
from __future__ import absolute_import

import datetime

import six
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.dialects.postgresql.base import CIDR
from sqlalchemy.dialects.postgresql.base import INET
from sqlalchemy.dialects.postgresql.base import MACADDR
from sqlalchemy.dialects.postgresql.json import JSON
from sqlalchemy.dialects.postgresql.json import JSONB

from ork.core.exception import ValidationError

if six.PY3:
    string_type = str
    int_type = int
else:
    string_type = basestring
    int_type = (int, long)


class DataTypeValidator(object):
    """
    supported following data type:
    1.int
    2.smallinteger
    3.biginteger
    4.float
    5.text
    6.string -->> length validate
    7.date
    8.datetime
    9.boolean
    10.cidr
    11.inet
    12.macaddr
    13.json
    14.jsonb
    """

    def __init__(self, field_info):
        self.field_column = field_info['field_column']
        self.field_name = field_info['field_name']
        self.field_value = field_info['field_value']
        self.validators = {
            Integer: self.validate_int,
            SmallInteger: self.validate_smallinteger,
            BigInteger: self.validate_biginteger,
            Float: self.validate_float,
            String: self.validate_string,
            text: self.validate_text,
            Date: self.validate_date,
            DateTime: self.validate_datetime,
            Boolean: self.validate_boolean,
            INET: self.validate_inet,
            CIDR: self.validate_cidr,
            JSONB: self.validate_jsonb,
            JSON: self.validate_json,
            MACADDR: self.validate_macaddr
        }

    def __call__(self, data_class):
        return self.validators.get(data_class)()

    def validate_int(self):
        if isinstance(self.field_value, string_type):
            try:
                self.field_value = int(self.field_value)
            except Exception as e:
                raise ValidationError(message='[%s] must be int type!' % self.field_name)
        else:
            if not isinstance(self.field_value, int_type):
                raise ValidationError(message='[%s] must be int type!' % self.field_name)

    def validate_smallinteger(self):
        if not isinstance(self.field_value, int):
            ValidationError(message='[%s] must be int type!' % self.field_name)

    def validate_biginteger(self):
        if not isinstance(self.field_value, int):
            ValidationError(message='[%s] must be int type!' % self.field_name)

    def validate_float(self):
        if not isinstance(self.field_value, float):
            ValidationError(message='[%s] must be float!' % self.field_name)

    def validate_string(self):
        if isinstance(self.field_value, string_type):
            max_length = self.field_column.type.length
            min_length = 0
            if not min_length <= len(self.field_value) <= max_length:
                raise ValidationError(message='[%s] length must be at %s <= %s <= %s!' % (
                    self.field_name, min_length, len(self.field_value), max_length))
        else:
            raise ValidationError(message='[%s] must be string type!' % self.field_name)

    def validate_text(self):
        if not isinstance(self.field_value, string_type):
            ValidationError(message='[%s] must be string type!')

    def validate_date(self):
        if not isinstance(self.field_value, datetime.date):
            ValidationError(message='[%s] must be date type!' % self.field_name)

    def validate_datetime(self):
        if not isinstance(self.field_value, datetime.datetime):
            ValidationError(message='[%s] must be datatime type!' % self.field_name)

    def validate_boolean(self):
        if not isinstance(self.field_value, bool):
            ValidationError(message='[%s] must be boolean type!' % self.field_name)

    def validate_inet(self):
        if not isinstance(self.field_value, string_type):
            ValidationError(message='[%s] must be string type!' % self.field_name)

    def validate_cidr(self):
        if not isinstance(self.field_value, string_type):
            ValidationError(message='[%s] must be string type!' % self.field_name)

    def validate_jsonb(self):
        if not isinstance(self.field_value, (dict, list)):
            ValidationError(message='[%s] must be dict or list!' % self.field_name)

    def validate_json(self):
        if not isinstance(self.field_value, (dict, list)):
            ValidationError(message='[%s] must be dict or list!' % self.field_name)

    def validate_macaddr(self):
        if not isinstance(self.field_value, string_type):
            ValidationError(message='[%s] must be string!' % self.field_name)


class Validate(object):
    def __init__(self, base):
        @event.listens_for(base, 'attribute_instrument')
        def configure_listener(class_, key, inst):
            table = class_.metadata.tables[class_.__tablename__]
            if not hasattr(inst.property, 'columns'):
                return

            @event.listens_for(inst, "set", retval=True)
            def set_(instance, value, oldvalue, initiator):
                field_column = inst.property.columns[0]
                field_name = field_column.name
                cols = []
                for col in table.columns._all_columns:
                    cols.append(col.name)
                if field_name in cols:
                    field_info = {"field_column": field_column, "field_name": field_name, "field_value": value}
                    # check field column nullable, if nullable and value is None return None, no need extra validate.
                    if field_column.nullable and value is None:
                        return value
                    # others validate by data type
                    validator = DataTypeValidator(field_info)
                    validator(field_column.type.__class__)
                    return value


def declarative_constructor(self, **kwargs):
    """A simple constructor that allows initialization from kwargs.
    Sets attributes on the constructed instance using the names and
    values in ``kwargs``.
    Only keys that are present as
    attributes of the instance's class are allowed. These could be,
    for example, any mapped columns or relationships.
    """
    cls_ = type(self)
    for k in kwargs:
        if hasattr(cls_, k):
            setattr(self, k, kwargs[k])


declarative_constructor.__name__ = '__init__'
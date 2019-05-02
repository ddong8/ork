#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/2 22:19
# @File    : curd.py
# @Author  : donghaixing
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import copy
import datetime
import logging
from contextlib import contextmanager

import sqlalchemy.exc

from ork.core import config
from ork.core import exception
from ork.core import utils
from ork.core.i18n import _
from ork.db import filter_wrapper
from ork.db import pool

CONF = config.CONF
LOG = logging.getLogger(__name__)


class ResourceBase(object):
    """
    资源操作基础类
    """
    orm_meta = None

    _primary_keys = 'id'

    _default_filter = {}

    _default_order = []

    def __init__(self, session=None, transaction=None):
        self._pool = None
        self._session = session
        self._transaction = transaction
        if session is None and transaction is None:
            self._pool = pool.POOL

    @property
    def default_filter(self):
        """
        获取默认过滤条件，只读
        :return: 默认过滤条件
        :rtype: dict
        """
        return copy.deepcopy(self._default_filter)

    @property
    def default_order(self):
        """
        获取默认排序规则，只读
        :return: 默认排序规则
        :rtype: list
        """

        return copy.copy(self._default_order)

    @property
    def primary_keys(self):
        """
        获取默认主键列，只读
        :return: 默认主键列
        :rtype: list
        """
        return copy.copy(self._primary_keys)

    @contextmanager
    def get_session(self):
        """
        会话管理上下文， 如果资源初始化时指定使用外部会话，则返回的也是外部会话对象
        """
        session = None
        if self._session is None and self._transaction is None:
            try:
                old_session = self._session
                session = self._pool.get_session()
                self._session = session
                yield session
            finally:
                self._session = old_session
                if session:
                    session.remove()
        elif self._session:
            yield self._session
        else:
            yield self._transaction

    @contextmanager
    def transaction(self):
        """
        事务管理上下文，如果资源初始化时指定使用外部事物，则返回的也是外部事物对象，
        保证事物统一性
        eg.
        with self.transaction() as session:
            resource(transaction=session).add()
            resource(transaction=session).update()
            resource(transaction=session).delete()
        """
        session = None
        if self._transaction is None:
            try:
                old_transaction = self._transaction
                session = self._pool.transaction()
                # 设置默认的数据库会话，所有函数都使用此会话
                self._transaction = session
                yield session
                session.commit()
            except Exception as e:
                LOG.exception(e)
                if session:
                    session.rollback()
                raise e
            finally:
                # 恢复原先设置
                self._transaction = old_transaction
                if session:
                    session.remove()
        else:
            yield self._transaction

    def _filter_hander_mapping(self):
        handlers = {
            'INET': filter_wrapper.FilterNetwork(),
            'CIDR': filter_wrapper.FilterNetwork(),
            'small_integer': filter_wrapper.FilterNumber(),
            'integer': filter_wrapper.FilterNumber(),
            'big_integer': filter_wrapper.FilterNumber(),
            'numeric': filter_wrapper.FilterNumber(),
            'float': filter_wrapper.FilterNumber(),
            'date': filter_wrapper.FilterDateTime(),
            'datetime': filter_wrapper.FilterDateTime(),
        }
        return handlers

    def _get_filter_handler(self, name):
        handlers = self._filter_hander_mapping()
        return handlers.get(name, filter_wrapper.Filter())

    def _apply_filters(self, query, orm_meta, filters=None, orders=None):
        def _extract_column_visit_name(column):
            col_type = getattr(column, 'type', None)
            if col_type:
                return getattr(col_type, '__visit_name__', None)
            return None

        def _handle_filter(handler, op, query, column, value):
            if op:
                func = getattr(handler, 'op_%s' % op, None)
                if func:
                    return func(query, column, value)
            else:
                func = getattr(handler, 'op', None)
                if func:
                    return func(query, column, value)
            return query

        filters = filters or {}
        orders = orders or []
        for name, value in filters.items():
            column = filter_wrapper.column_from_expression(orm_meta, name)
            if column is not None:
                handler = self._get_filter_handler(_extract_column_visit_name(column))
                if not isinstance(value, dict):
                    # op is None
                    query = _handle_filter(handler, None, query, column, value)
                else:
                    for operator, value in value.items():
                        query = _handle_filter(handler, operator, query, column, value)
        for field in orders:
            order = '+'
            if field.startswith('+'):
                order = '+'
                field = field[1:]
            elif field.startswith('-'):
                order = '-'
                field = field[1:]
            column = filter_wrapper.column_from_expression(orm_meta, field)
            if column:
                if order == '+':
                    query = query.order_by(column)
                else:
                    query = query.order_by(column.desc())
        return query

    def _get_query(self, session, orm_meta=None, filters=None, orders=None, tables=None, ignore_default=False):
        """获取一个query对象，这个对象已经应用了filter，可以确保查询的数据只包含我们感兴趣的数据，常用于过滤已被删除的数据
        :param session: session对象
        :type session: session
        :param orm_meta: ORM Model, 如果None, 则默认使用self.orm_meta
        :type orm_meta: ORM Model
        :param filters: 简单的等于过滤条件, eg.{'column1': value, 'column2':
        value}，如果None，则默认使用default filter
        :type filters: dict
        :param orders: 排序['+field', '-field', 'field']，+表示递增，-表示递减，不设置默认递增
        :type orders: list
        :returns: query对象
        :rtype: query
        :raises: ValueError
        """
        orm_meta = orm_meta or self.orm_meta
        filters = filters or {}
        filters = copy.copy(filters)
        if not ignore_default:
            filter_wrapper.merge(filters, self.default_filter)
        if not ignore_default:
            orders = self.default_order if orders is None else orders
        else:
            orders = orders or []
        orders = copy.copy(orders)
        tables = tables or []
        tables = copy.copy(tables)
        tables.insert(0, orm_meta)
        if orm_meta is None:
            raise exception.CriticalError(msg=utils.format_kwstring(
                _('%(name)s.orm_meta can not be None'), name=self.__class__.__name__))
        query = session.query(*tables)
        query = self._apply_filters(query, orm_meta, filters, orders)
        return query

    def list(self, filters=None, orders=None, offset=None, limit=None):
        offset = offset or 0
        with self.get_session() as session:
            query = self._get_query(session, filters=filters, orders=orders)
            if offset:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            records = query
            results = [rec.to_dict() for rec in records]
        return results

    def count(self, filters=None, offset=None, limit=None):
        offset = offset or 0
        with self.get_session() as session:
            query = self._get_query(session, filters=filters, orders=[])
            if offset:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            return query.count()

    def _apply_primary_key_filter(self, query, rid):
        keys = self.primary_keys
        if utils.is_list_type(keys) and utils.is_list_type(rid):
            if len(rid) != len(keys):
                raise exception.CriticalError(msg=utils.format_kwstring(
                    _('primary key length not match! require: %(length_require)d, input: %(length_input)d'),
                    length_require=len(keys), length_input=len(rid)))
            for idx, val in enumerate(rid):
                query = query.filter(getattr(self.orm_meta, keys[idx]) == val)
        elif utils.is_string_type(keys) and utils.is_list_type(rid) and len(rid) == 1:
            query = query.filter(getattr(self.orm_meta, keys) == rid[0])
        elif utils.is_list_type(keys) and len(keys) == 1:
            query = query.filter(getattr(self.orm_meta, keys[0]) == rid)
        elif utils.is_string_type(keys) and not utils.is_list_type(rid):
            query = query.filter(getattr(self.orm_meta, keys) == rid)
        else:
            raise exception.CriticalError(msg=utils.format_kwstring(
                _('primary key not match! require: %(keys)s'), keys=keys))
        return query

    def get(self, rid):
        """
        :param rid:
        :return:
        """
        result = None
        with self.get_session() as session:
            query = self._get_query(session)
            query = self._apply_primary_key_filter(query, rid)
            rec_tuples = query.one_or_none()
            if rec_tuples:
                result = rec_tuples.to_detail_dict()
            else:
                raise exception.NotFoundError('%s not found!' % rid)
        return result

    def _before_create(self, resource):
        pass

    def create(self, resource):
        with self.get_session() as session:
            self._before_create(resource)
            orm_fields = resource
            try:
                item = self.orm_meta(**orm_fields)
                session.add(item)
                session.flush()
                return item.to_dict()
            except sqlalchemy.exc.IntegrityError as e:
                print(e)
            except sqlalchemy.exc.SQLAlchemyError as e:
                LOG.exception(e)
                raise exception.DBError(msg=_('unknown db error'))

    def update(self, rid, resource):
        with self.transaction() as session:
            try:
                query = self._get_query(session)
                query = self._apply_primary_key_filter(query, rid)
                record = query.one_or_none()
                orm_fields = resource
                if record is None:
                    raise exception.NotFoundError(rid=str(rid))
                else:
                    before_update = record.to_dict()
                    if orm_fields:
                        record.update(orm_fields)
                    session.flush()
                    after_update = record.to_dict()
                return before_update, after_update
            except sqlalchemy.exc.IntegrityError as e:
                print(e)
            except sqlalchemy.exc.SQLAlchemyError as e:
                LOG.exception(e)
                raise exception.DBError(msg=_('unknown db error'))

    def delete(self, rid):
        with self.transaction() as session:
            try:
                query = self._get_query(session, orders=[])
                query = self._apply_primary_key_filter(query, rid)
                record = query.one_or_none()
                resource = None
                count = 0
                if record is not None:
                    resource = record.to_dict()
                if getattr(self.orm_meta, 'removed', None) is not None:
                    if record is not None:
                        count = query.update({'removed': datetime.datetime.now()})
                else:
                    count = query.delete()
                session.flush()
                return count, [resource]
            except sqlalchemy.exc.IntegrityError as e:
                print(e)
            except sqlalchemy.exc.SQLAlchemyError as e:
                LOG.exception(e)
                raise exception.DBError(msg=_('unknown db error'))
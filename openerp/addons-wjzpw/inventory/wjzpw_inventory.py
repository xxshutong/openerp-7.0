# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import calendar

import logging
import datetime
from openerp import tools

from openerp.osv import fields, osv, orm

_logger = logging.getLogger(__name__)


class utils():
    @classmethod
    def get_default_value(cls, cr, uid, column):
        """
        获取最近输入数据的column值
        """
        query_sql = """
            SELECT %s
            FROM wjzpw_inventory_input
            WHERE write_uid = %d ORDER BY id DESC LIMIT 1
        """ % (column, uid)
        cr.execute(query_sql)
        result = cr.dictfetchone()
        if result:
            return result[column]
        return None


class wjzpw_inventory_input(osv.osv):
    """
    坯布入库
    """
    _name = "wjzpw.inventory.input"
    _description = "wjzpw.inventory.ruKuGuanLi"

    def _get_default_machine_no(self, cr, uid, context=None):
        return utils.get_default_value(cr, uid, 'machine_no')

    def _get_default_input_date(self, cr, uid, context=None):
        return utils.get_default_value(cr, uid, 'input_date')

    def _get_default_product_id(self, cr, uid, context=None):
        return utils.get_default_value(cr, uid, 'product_id')

    def _get_default_batch_no(self, cr, uid, context=None):
        return utils.get_default_value(cr, uid, 'batch_no')

    def _input_date_str(self, cr, uid, ids, field_name, arg, context):
        """
        字符串入库日期
        """
        res = {}
        for id in ids:
            res.setdefault(id, '')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.input_date:
                res[rec.id] = rec.input_date
        return res

    def _total_number(self, cr, uid, ids, field_name, arg, context):
        """
        合计
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.superior_number and rec.grade_a_number and rec.grade_b_number:
                res[rec.id] = rec.superior_number + rec.grade_a_number + rec.grade_b_number
        return res

    def _a_rate(self, cr, uid, ids, field_name, arg, context):
        """
        一等次品率
        """
        res = {}
        for id in ids:
            res.setdefault(id, '')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.grade_a_number:
                rate = rec.grade_a_number * 1.0 / (rec.superior_number + rec.grade_a_number + rec.grade_b_number)
                res[rec.id] = '0' if rate == 0.0 else ("%.2f%s" % (rate, '%'))
        return res

    def _b_rate(self, cr, uid, ids, field_name, arg, context):
        """
        二等次品率
        """
        res = {}
        for id in ids:
            res.setdefault(id, '')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.grade_b_number:
                rate = rec.grade_b_number * 1.0 / (rec.superior_number + rec.grade_a_number + rec.grade_b_number)
                res[rec.id] = '0' if rate == 0.0 else ("%.2f%s" % (rate, '%'))
        return res

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        return super(wjzpw_inventory_input, self).search(cr, user, args, offset, limit, 'input_date desc', context, count)

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        """
        Get the list of records in list view grouped by the given ``groupby`` fields

        :param cr: database cursor
        :param uid: current user id
        :param domain: list specifying search criteria [['field_name', 'operator', 'value'], ...]
        :param list fields: list of fields present in the list view specified on the object
        :param list groupby: fields by which the records will be grouped
        :param int offset: optional number of records to skip
        :param int limit: optional max number of records to return
        :param dict context: context arguments, like lang, time zone
        :param list orderby: optional ``order by`` specification, for
                             overriding the natural sort ordering of the
                             groups, see also :py:meth:`~osv.osv.osv.search`
                             (supported only for many2one fields currently)
        :return: list of dictionaries(one dictionary for each record) containing:

                    * the values of fields grouped by the fields in ``groupby`` argument
                    * __domain: list of tuples specifying the search criteria
                    * __context: dictionary with argument like ``groupby``
        :rtype: [{'field_name_1': value, ...]
        :raise AccessError: * if user has no read rights on the requested object
                            * if user tries to bypass access rules for read on the requested object

        """
        context = context or {}
        self.check_access_rights(cr, uid, 'read')
        if not fields:
            fields = self._columns.keys()

        query = self._where_calc(cr, uid, domain, context=context)
        self._apply_ir_rules(cr, uid, query, 'read', context=context)

        # Take care of adding join(s) if groupby is an '_inherits'ed field
        groupby_list = groupby
        qualified_groupby_field = groupby
        if groupby:
            if isinstance(groupby, list):
                groupby = groupby[0]
            qualified_groupby_field = self._inherits_join_calc(groupby, query)

        if groupby:
            assert not groupby or groupby in fields, "Fields in 'groupby' must appear in the list of fields to read (perhaps it's missing in the list view?)"
            groupby_def = self._columns.get(groupby) or (self._inherit_fields.get(groupby) and self._inherit_fields.get(groupby)[2])
            assert groupby_def and groupby_def._classic_write, "Fields in 'groupby' must be regular database-persisted fields (no function or related fields), or function fields with store=True"

        # TODO it seems fields_get can be replaced by _all_columns (no need for translation)
        fget = self.fields_get(cr, uid, fields)
        flist = ''
        group_count = group_by = groupby
        if groupby:
            if fget.get(groupby):
                groupby_type = fget[groupby]['type']
                if groupby_type in ('date', 'datetime'):
                    qualified_groupby_field = "to_char(%s,'yyyy-mm')" % qualified_groupby_field
                    flist = "%s as %s " % (qualified_groupby_field, groupby)
                elif groupby_type == 'boolean':
                    qualified_groupby_field = "coalesce(%s,false)" % qualified_groupby_field
                    flist = "%s as %s " % (qualified_groupby_field, groupby)
                else:
                    flist = qualified_groupby_field
            else:
                # Don't allow arbitrary values, as this would be a SQL injection vector!
                raise orm.except_orm('Invalid group_by',
                                 'Invalid group_by specification: "%s".\nA group_by specification must be a list of valid fields.'%(groupby,))

        #TODO custom appregated fields - From WJZPW
        aggregated_fields = ['superior_number', 'grade_a_number', 'grade_b_number']
        for f in aggregated_fields:
            if flist:
                flist += ', '
            if f == 'superior_number' or f == 'grade_a_number' or f == 'grade_b_number':
                qualified_field = '"%s"."%s"' % (self._table, f)
                flist += "sum(%s) AS %s" % (qualified_field, f)
        # total number calculate
        total_number = '(sum("%s".superior_number) + sum("%s".grade_a_number) + sum("%s".grade_b_number))' % (self._table, self._table, self._table)
        if flist:
            flist += ', '
        flist += "%s AS total_number" % total_number

        # a_rate and b_rate calculate
        aggregated_fields = ['a_rate', 'b_rate']
        aggregated_fields_cols = {"a_rate": "grade_a_number", "b_rate": "grade_b_number"}
        for f in aggregated_fields:
            if flist:
                flist += ', '
            qualified_field = '"%s"."%s"' % (self._table, aggregated_fields_cols[f])
            flist += "round((CASE WHEN sum(%s) > 0 THEN sum(%s)*1.0/%s ELSE 0 END ), 2) AS %s " % (qualified_field, qualified_field, total_number, f)

        gb = groupby and (' GROUP BY ' + qualified_groupby_field) or ''

        from_clause, where_clause, where_clause_params = query.get_sql()
        where_clause = where_clause and ' WHERE ' + where_clause
        limit_str = limit and ' limit %d' % limit or ''
        offset_str = offset and ' offset %d' % offset or ''
        if len(groupby_list) < 2 and context.get('group_by_no_leaf'):
            group_count = '_'
        cr.execute('SELECT min(%s.id) AS id, count(%s.id) AS %s_count' % (self._table, self._table, group_count) + (flist and ',') + flist + ' FROM ' + from_clause + where_clause + gb + limit_str + offset_str, where_clause_params)
        alldata = {}
        groupby = group_by
        for r in cr.dictfetchall():
            for fld, val in r.items():
                if val is None: r[fld] = False
            alldata[r['id']] = r
            del r['id']

        order = orderby or groupby
        data_ids = self.search(cr, uid, [('id', 'in', alldata.keys())], order=order, context=context)

        # the IDs of records that have groupby field value = False or '' should be included too
        data_ids += set(alldata.keys()).difference(data_ids)

        if groupby:
            data = self.read(cr, uid, data_ids, [groupby], context=context)
            # restore order of the search as read() uses the default _order (this is only for groups, so the footprint of data should be small):
            data_dict = dict((d['id'], d[groupby] ) for d in data)
            result = [{'id': i, groupby: data_dict[i]} for i in data_ids]
        else:
            result = [{'id': i} for i in data_ids]

        for d in result:
            if groupby:
                d['__domain'] = [(groupby, '=', alldata[d['id']][groupby] or False)] + domain
                if not isinstance(groupby_list, (str, unicode)):
                    if groupby or not context.get('group_by_no_leaf', False):
                        d['__context'] = {'group_by': groupby_list[1:]}
            if groupby and groupby in fget:
                if d[groupby] and fget[groupby]['type'] in ('date', 'datetime'):
                    dt = datetime.datetime.strptime(alldata[d['id']][groupby][:7], '%Y-%m')
                    days = calendar.monthrange(dt.year, dt.month)[1]

                    date_value = datetime.datetime.strptime(d[groupby][:10], '%Y-%m-%d')
                    d[groupby] = babel.dates.format_date(
                        date_value, format='MMMM yyyy', locale=context.get('lang', 'en_US'))
                    d['__domain'] = [(groupby, '>=', alldata[d['id']][groupby] and datetime.datetime.strptime(alldata[d['id']][groupby][:7] + '-01', '%Y-%m-%d').strftime('%Y-%m-%d') or False), \
                                     (groupby, '<=', alldata[d['id']][groupby] and datetime.datetime.strptime(alldata[d['id']][groupby][:7] + '-' + str(days), '%Y-%m-%d').strftime('%Y-%m-%d') or False)] + domain
                del alldata[d['id']][groupby]
            d.update(alldata[d['id']])
            del d['id']

        if groupby and groupby in self._group_by_full:
            result = self._read_group_fill_results(cr, uid, domain, groupby, groupby_list,
                                                   aggregated_fields, result, read_group_order=order,
                                                   context=context)

        return result

    _columns = {
        'machine_no': fields.integer('wjzpw.inventory.jiHao', required=True),
        'input_date': fields.date('wjzpw.inventory.luRuRiQi', required=True),
        'superior_number': fields.integer('wjzpw.inventory.youDengPin', required=True),
        'grade_a_number': fields.integer('wjzpw.inventory.yiDengPin', required=True),
        'grade_b_number': fields.integer('wjzpw.inventory.erDengPin', required=True),
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing', required=True),
        'batch_no': fields.many2one('wjzpw.batch.no', 'wjzpw.piHao', required=True),
        'machine_output_id': fields.many2one('wjzpw.inventory.machine.output', 'wjzpw.inventory.jiTaiChanChu',
                                             required=False),

        # functions
        'input_date_str': fields.function(_input_date_str, string='wjzpw.inventory.luRuRiQi', type='char', method=True, store=True),  # 字符串入库日期
        'total_number': fields.function(_total_number, string='wjzpw.inventory.heJi', type='integer', method=True),  # 产量合计
        'a_rate': fields.function(_a_rate, string='wjzpw.inventory.yiDengCiPinLv', type='char', method=True),  # 一等次品率
        'b_rate': fields.function(_b_rate, string='wjzpw.inventory.erDengCiPinLv', type='char', method=True),  # 二等次品率
    }

    _defaults = {
        "superior_number": 0,
        "grade_a_number": 0,
        "grade_b_number": 0,
        "machine_no": _get_default_machine_no,
        "input_date": _get_default_input_date,
        "product_id": _get_default_product_id,
        "batch_no": _get_default_batch_no
    }

    _order = "input_date desc, product_id, batch_no, machine_no"


class wjzpw_inventory_output(osv.osv):
    """
    坯布出库
    """
    _name = "wjzpw.inventory.output"
    _description = "wjzpw.inventory.chuKuGuanLi"

    _columns = {
        'input_date': fields.date('wjzpw.inventory.luRuRiQi', required=True),
        'code': fields.char('wjzpw.inventory.maDan', size=60, required=False),
        'superior_number': fields.integer('wjzpw.inventory.youDengPin', required=True),
        'grade_a_number': fields.integer('wjzpw.inventory.yiDengPin', required=True),
        'grade_b_number': fields.integer('wjzpw.inventory.erDengPin', required=True),
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing', required=True),
        'batch_no': fields.many2one('wjzpw.batch.no', 'wjzpw.piHao', required=True),
        'customer': fields.many2one('res.partner', 'wjzpw.inventory.keHu', domain=[('customer', '=', True)],
                                    required=True)
    }

    _defaults = {
        "superior_number": 0,
        "grade_a_number": 0,
        "grade_b_number": 0
    }

    _order = "input_date desc, customer, product_id"


class wjzpw_organzine_input(osv.osv):
    """
    经丝入库
    """
    _name = "wjzpw.organzine.input"
    _description = "wjzpw.inventory.jingSiRuKuGuanLi"

    def onchange_fields(self, cr, uid, ids, quantity, quantity_avg, weight_avg, count):
        quantity_count = 0
        weight = 0.0
        count_weight = 0.0
        if quantity and quantity_avg:
            quantity_count = quantity * quantity_avg
        if quantity and quantity_avg and weight_avg:
            weight = quantity * quantity_avg * weight_avg
        if weight_avg and count:
            count_weight = weight_avg * count
        return {
            'value': {
                'quantity_count': quantity_count,
                'weight': weight,
                'count_weight': count_weight
            }
        }

    def _total_count(self, cr, uid, ids, field_name, arg, context):
        """
        计算总只数
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            total_count = 0
            if rec.quantity_avg and rec.quantity:
                total_count += rec.quantity_avg * rec.quantity
            if rec.count:
                total_count += rec.count
            res[rec.id] = total_count
        return res

    def _total_weight(self, cr, uid, ids, field_name, arg, context):
        """
        计算总重量
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0.0)
        for rec in self.browse(cr, uid, ids, context=context):
            total_weight = 0
            if rec.weight:
                total_weight += rec.weight
            if rec.count_weight:
                total_weight += rec.count_weight
            res[rec.id] = total_weight
        return res

    _columns = {
        'input_date': fields.date('wjzpw.inventory.ruKuRiQi', required=True),
        'process_unit': fields.char('wjzpw.inventory.jiaGongDanWei'),  # 加工单位
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'weight_avg': fields.float('wjzpw.inventory.tongZiJingZhong'),  # 筒子净重
        'quantity_avg': fields.integer('wjzpw.inventory.meiBaoXiangZhiShu'),  # 每包箱只数
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'quantity_count': fields.integer('wjzpw.inventory.baoXiangZhiShu'), # 包/箱只数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 箱数重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 只数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang'),  # 只数重量

        # Function fields
        'total_count': fields.function(_total_count, string='wjzpw.inventory.zongZhiShu', type='integer', method=True),  # 总只数
        'total_weight': fields.function(_total_weight, string='wjzpw.inventory.zongZhongLiang', type='float', method=True)  #总重量
    }

    _default = {
        'quantity': 0,
        'count': 0,
    }

    _order = "input_date desc"


class wjzpw_flow_no(osv.osv):
    """
    牵经流程编号
    """
    _name = "wjzpw.flow.no"
    _description = "wjzpw.liuChengBianHao"
    _flow_prefix = "LC"

    def _default_flow_no(self, cr, uid, context=None):
        default_no = self._default_no(cr, uid, context=context)
        return  '%s%05d' % (self._flow_prefix, default_no)

    def _default_no(self, cr, uid, context=None):
        query_sql = """
            SELECT max(no)
            FROM wjzpw_flow_no
            """
        cr.execute(query_sql)
        order = cr.dictfetchone()['max']
        if not order:
            return 1
        else:
            return order + 1

    _columns = {
        'name': fields.char('wjzpw.inventory.liuChengBianHao', size=64, required=True),
        'no': fields.integer('wjzpw.inventory.liuChengBianHao', required=True, readonly=True),
    }

    _defaults = {
        'name': _default_flow_no,
        'no': _default_no,
    }

    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该流程编号已经存在'),
        ('no_unique', 'unique(no)', u'该流程编号已经存在'),
        ]

    _order = "no desc"


class wjzpw_organzine_output(osv.osv):
    """
    经丝出库
    """
    _name = "wjzpw.organzine.output"
    _description = "wjzpw.inventory.chuKuGuanLi"

    def onchange_fields(self, cr, uid, ids, quantity, quantity_avg, weight_avg, count):
        quantity_count = 0
        weight = 0.0
        count_weight = 0.0
        if quantity and quantity_avg:
            quantity_count = quantity * quantity_avg
        if quantity and quantity_avg and weight_avg:
            weight = quantity * quantity_avg * weight_avg
        if weight_avg and count:
            count_weight = weight_avg * count
        return {
            'value': {
                'quantity_count': quantity_count,
                'weight': weight,
                'count_weight': count_weight
            }
        }

    def _get_process_unit_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT process_unit
            FROM wjzpw_organzine_input
            """
        cr.execute(query_sql)
        keyValues = []
        for process_unit in cr.fetchall():
            keyValues.append((process_unit[0], process_unit[0]))
        return tuple(keyValues)

    def onchange_process_unit(self, cr, uid, ids, process_unit):
        query_sql = """
            SELECT DISTINCT material_specification
            FROM wjzpw_organzine_input
            WHERE process_unit = '%s' ORDER BY material_specification
            """ % process_unit
        cr.execute(query_sql)
        specification_ids = []
        for specification_id in cr.fetchall():
            specification_ids.append(specification_id[0])

        return {
            'domain': {
                'material_specification': [('id', 'in', specification_ids)]
            }
        }

    def onchange_material_specification(self, cr, uid, ids, process_unit=None, material_specification=None):
        query_sql = """
            SELECT DISTINCT material_area
            FROM wjzpw_organzine_input
            WHERE process_unit = '%s' AND material_specification = %d ORDER BY material_area
            """ % (process_unit, material_specification)
        cr.execute(query_sql)
        area_ids = []
        for material_area_id in cr.fetchall():
            area_ids.append(material_area_id[0])

        return {
            'domain': {
                'material_area': [('id', 'in', area_ids)]
            }
        }

    def onchange_material_area(self, cr, uid, ids, process_unit=None, material_specification=None, material_area=None):
        query_sql = """
            SELECT DISTINCT batch_no
            FROM wjzpw_organzine_input
            WHERE process_unit = '%s' AND material_specification = %d AND material_area = %d ORDER BY batch_no
            """ % (process_unit, material_specification, material_area)
        cr.execute(query_sql)
        batch_no_ids = []
        for batch_no in cr.fetchall():
            batch_no_ids.append(batch_no[0])

        return {
            'domain': {
                'batch_no': [('id', 'in', batch_no_ids)]
            }
        }

    def _total_count(self, cr, uid, ids, field_name, arg, context):
        """
        计算总只数
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            total_count = 0
            if rec.quantity_avg and rec.quantity:
                total_count += rec.quantity_avg * rec.quantity
            if rec.count:
                total_count += rec.count
            res[rec.id] = total_count
        return res

    def _total_weight(self, cr, uid, ids, field_name, arg, context):
        """
        计算总重量
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0.0)
        for rec in self.browse(cr, uid, ids, context=context):
            total_weight = 0
            if rec.weight:
                total_weight += rec.weight
            if rec.count_weight:
                total_weight += rec.count_weight
            res[rec.id] = total_weight
        return res

    _columns = {
        'output_date': fields.date('wjzpw.inventory.chuKuRiQi', required=True),
        'process_unit': fields.selection(_get_process_unit_options, 'wjzpw.inventory.jiaGongDanWei', required=True),  # 加工单位
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'weight_avg': fields.float('wjzpw.inventory.yuanLiaoTongZiJingZhongKG'),  # 筒子净重
        'quantity_avg': fields.integer('wjzpw.inventory.meiBaoXiangZhiShu'),  # 每包箱只数
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'quantity_count': fields.integer('wjzpw.inventory.baoXiangZhiShu'),  # 包/箱只数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 箱数重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 只数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang'),  # 只数重量
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing'),  # 品名
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.liuChengBianHao'),  # 流程编号

        # Function fields
        'total_count': fields.function(_total_count,
                                       string='wjzpw.inventory.zongZhiShu',
                                       type='integer',
                                       method=True),  # 总只数
        'total_weight': fields.function(_total_weight, string='wjzpw.inventory.zongZhongLiang', type='float', method=True),  #总重量
        # 'department': fields.many2one('hr.department', 'wjzpw.inventory.shiYongBuMen', required=True)  # 使用部门
        'department': fields.selection((('zjb', 'wjzpw.inventory.zhengJiangBing'), ('bn', 'wjzpw.inventory.beiNian'), ('msb', 'wjzpw.inventory.menShiBu')), 'wjzpw.inventory.shiYongBuMen', required=True)  # 使用部门
    }

    _defaults = {
        "quantity": 0,
        "count": 0,
    }

    _order = "output_date desc"


class wjzpw_inventory_machine_output(osv.osv):
    _name = "wjzpw.inventory.machine.output"
    _description = "wjzpw.inventory.jiTaiChanLiang"

    def _complete_date(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res.setdefault(id, '未完成')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.complete_date:
                res[rec.id] = rec.complete_date
            else:
                res[rec.id] = '未完成'
        return res

    def _woven_shrinkage(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res.setdefault(id, '未知')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.woven_shrinkage:
                res[rec.id] = rec.woven_shrinkage
        return res

    def _output_amount(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            machine_output = self.get_machine_output_by_id(cr, id)
            if machine_output and machine_output['output_amount']:
                res[id] = machine_output['output_amount']
                continue
            res[id] = self.get_total_output_amount(cr, machine_output)
        return res

    @classmethod
    def get_machine_output_by_id(cls, cr, id):
        # Get current machine output instance
        get_sql = """
            SELECT *
            FROM wjzpw_inventory_machine_output
            WHERE id = %d
            """ % id
        cr.execute(get_sql)
        return cr.dictfetchone()

    @classmethod
    def get_total_output_amount(cls, cr, machine_output):
        # Get total output by now
        sum_sql = """
            SELECT sum(superior_number) AS total_superior, sum(grade_a_number) AS total_a, sum(grade_b_number) AS total_b
            FROM wjzpw_inventory_input
            WHERE machine_output_id IS NULL AND machine_no = %d AND product_id = %d AND batch_no = %d
            """ % (machine_output['machine_no'], machine_output['product_id'], machine_output['batch_no'])
        cr.execute(sum_sql)
        sum_res = cr.dictfetchone()
        total = 0.0
        if sum_res:
            total += sum_res['total_superior'] if sum_res['total_superior'] else 0.0
            total += sum_res['total_a'] if sum_res['total_a'] else 0.0
            total += sum_res['total_b'] if sum_res['total_b'] else 0.0
        return total

    @classmethod
    def get_input_ids_by_machine_output(cls, cr, machine_output):
        # Get total output by now
        sum_sql = """
            SELECT id
            FROM wjzpw_inventory_input
            WHERE machine_output_id IS NULL AND machine_no = %d AND product_id = %d AND batch_no = %d
            """ % (machine_output['machine_no'], machine_output['product_id'], machine_output['batch_no'])
        cr.execute(sum_sql)
        ids = []
        for inventory_input in cr.fetchall():
            ids.append(inventory_input[0])
        return ids

    # Button to complete machine output
    def action_button_complete_machine_output(self, cr, uid, ids, context=None):
        for id in ids:
            # Get current machine output instance
            machine_output = self.get_machine_output_by_id(cr, id)
            if machine_output:
                total = self.get_total_output_amount(cr, machine_output)
                # Update Machine output record
                self.pool.get('wjzpw.inventory.machine.output') \
                    .write(cr, uid, [id],
                           {'output_amount': total, 'is_completed': 'Y', 'complete_date': datetime.datetime.now(),
                            'woven_shrinkage':
                                (0.0 if machine_output['beam_amount'] <= 0.0
                                 else (machine_output['beam_amount'] - total) / machine_output['beam_amount'])})
                # Update all input records which have the same batch No and product type
                input_ids = self.get_input_ids_by_machine_output(cr, machine_output)
                self.pool.get('wjzpw.inventory.input').write(cr, uid, input_ids, {'machine_output_id': machine_output['id']})

    _columns = {
        'machine_no': fields.integer('wjzpw.inventory.jiHao', required=True),
        'beam_amount': fields.float('wjzpw.inventory.jingZhouChangDu', required=True),
        'output_amount': fields.float('wjzpw.inventory.leiJiChanLiang'),
        'is_completed': fields.boolean('wjzpw.inventory.yiWanCheng', required=True),
        'complete_date': fields.datetime('wjzpw.inventory.wanChengShiJian'),
        'woven_shrinkage': fields.float('wjzpw.inventory.zhiSuoLv'),
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing', required=True),
        'batch_no': fields.many2one('wjzpw.batch.no', 'wjzpw.piHao', required=True),

        # Function fields
        'complete_date_fun': fields.function(_complete_date, string='wjzpw.inventory.wanChengShiJian', type='char',
                                             method=True),
        'output_amount_fun': fields.function(_output_amount, string='wjzpw.inventory.leiJiChanLiang', type='float',
                                             method=True),
        'woven_shrinkage_fun': fields.function(_woven_shrinkage, string="wjzpw.inventory.zhiSuoLv", type='char',
                                               method=True)

    }

    _default = {
        'output_amount': 0,
        'is_completed': False
    }

    _order = "machine_no,product_id,batch_no"


class wjzpw_weft_input(osv.osv):
    """
    纬丝入库
    """
    _name = "wjzpw.weft.input"
    _description = "wjzpw.inventory.weiSiRuKuGuanLi"

    def _calculate_weight_avg(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res.setdefault(id, '未知')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.weight and rec.quantity:
                res[rec.id] = '%0.2f' % (rec.weight / rec.quantity)
        return res

    _columns = {
        'input_date': fields.date('wjzpw.inventory.ruKuRiQi', required=True),
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.weft.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'level': fields.selection((('A', 'A'), ('AA', 'AA')), 'wjzpw.inventory.dengJi'),  # 等级
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 箱数重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 二次入库零散个数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang'),  # 只数重量
        'weight_avg': fields.function(_calculate_weight_avg, string='wjzpw.inventory.meiXiangZhongLiang', type='char', method=True)  # 计算得出每箱重量
    }

    _default = {
        'quantity': 0,
        'count': 0,
        'weight': 0,
    }

    _order = "input_date desc"


class wjzpw_weft_output(osv.osv):
    """
    纬丝出库
    """
    _name = "wjzpw.weft.output"
    _description = "wjzpw.inventory.chuKuGuanLi"

    # def _get_material_specification_options(self, cr, uid, context=None):
    #     query_sql = """
    #         SELECT DISTINCT material_specification
    #         FROM wjzpw_weft_input
    #         """
    #     cr.execute(query_sql)
    #     material_specification_ids = []
    #     for material_specification in cr.fetchall():
    #         material_specification_ids.append((material_specification[0]))
    #     return material_specification_ids

    def onchange_material_specification(self, cr, uid, ids, material_specification=None):
        query_sql = """
            SELECT DISTINCT material_area
            FROM wjzpw_weft_input
            WHERE material_specification = %d ORDER BY material_area
            """ % material_specification
        cr.execute(query_sql)
        area_ids = []
        for material_area_id in cr.fetchall():
            area_ids.append(material_area_id[0])

        return {
            'domain': {
                'material_area': [('id', 'in', area_ids)]
            }
        }

    def onchange_material_area(self, cr, uid, ids, material_specification=None, material_area=None):
        query_sql = """
            SELECT DISTINCT batch_no
            FROM wjzpw_weft_input
            WHERE material_specification = %d AND material_area = %d ORDER BY batch_no
            """ % (material_specification, material_area)
        cr.execute(query_sql)
        batch_no_ids = []
        for batch_no in cr.fetchall():
            batch_no_ids.append(batch_no[0])

        return {
            'domain': {
                'batch_no': [('id', 'in', batch_no_ids)]
            }
        }

    def onchange_quantity(self, cr, uid, ids, material_specification=None, material_area=None, batch_no=None, level=None, quantity=None):
        if not material_specification or not material_area or not batch_no or not level or not quantity:
            return {}
        query_sql = """
            SELECT quantity, weight
            FROM wjzpw_weft_inventory
            WHERE material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s'
        """ % (material_specification, material_area, batch_no, level)
        cr.execute(query_sql)
        weft_inventory = cr.dictfetchone()
        if weft_inventory:
            value = weft_inventory['weight'] / weft_inventory['quantity'] * quantity
            return {
                'value': {
                    'weight': value
                }
            }
        else:
            return {}

    def create(self, cr, uid, vals, *args, **kwargs):
        if vals['weight'] == 0.0:
            query_sql = """
                SELECT weight/quantity as unit
                FROM wjzpw_weft_inventory
                WHERE material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s'
            """ % (vals['material_specification'], vals['material_area'], vals['batch_no'], vals['level'])
            cr.execute(query_sql)
            weft_inventory = cr.dictfetchone()
            if weft_inventory and vals['quantity']:
                vals['weight'] = weft_inventory['unit'] * vals['quantity']
        left_output = super(wjzpw_weft_output, self).create(cr, uid, vals, *args, **kwargs)
        if vals['department'] != 'hdcj':
            return left_output
        new_vals = {}
        new_vals['material_specification'] = vals['material_specification']
        new_vals['material_area'] = vals['material_area']
        new_vals['batch_no'] = vals['batch_no']
        new_vals['level'] = vals['level']
        # Get latest weft workshop left
        # 每次仓库出库都需要在车间剩余里添加记录
        cr.execute(
            '''
            SELECT input_date, quantity, weight, count, count_weight
            FROM wjzpw_weft_workshop_left
            WHERE material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s' ORDER BY input_date desc, quantity desc, count desc limit 1
            ''' % (vals['material_specification'], vals['material_area'], vals['batch_no'], vals['level'])
        )
        workshop_left = cr.dictfetchone()
        # Calculate weft workshop left
        if workshop_left:
            new_vals['input_date'] = workshop_left['input_date']
            new_vals['quantity'] = workshop_left['quantity'] + vals['quantity']
            new_vals['weight'] = workshop_left['weight'] + vals['weight']
            new_vals['count'] = workshop_left['count'] + vals['count']
            new_vals['count_weight'] = workshop_left['count_weight'] + vals['count_weight']
        else:
            new_vals['input_date'] = vals['output_date']
            new_vals['quantity'] = vals['quantity']
            new_vals['weight'] = vals['weight']
            new_vals['count'] = vals['count']
            new_vals['count_weight'] = vals['count_weight']

        weft_workshop_left_obj = self.pool.get('wjzpw.weft.workshop.left')
        weft_workshop_left_obj.create(cr, uid, new_vals, context=None)
        return left_output

    def unlink(self, cr, uid, ids, context=None):
        """
        删除纬丝出库的时候需要把之前加入到车间剩余里的量重新回退出来
        """
        for rec in self.browse(cr, uid, ids, context=context):
            cr.execute(
                '''
                SELECT id, input_date, quantity, weight, count, count_weight
                FROM wjzpw_weft_workshop_left
                WHERE material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s' ORDER BY input_date desc, quantity desc, count desc limit 1
                ''' % (rec.material_specification, rec.material_area, rec.batch_no, rec.level)
            )
            workshop_left = cr.dictfetchone()
            if workshop_left:
                self.pool.get('wjzpw.weft.workshop.left') \
                    .write(cr, uid, [workshop_left['id']],
                           {'quantity': workshop_left['quantity'] - rec.quantity, 'weight': workshop_left['weight'] - rec.weight
                               , 'count': workshop_left['count'] - rec.count, 'count_weight': workshop_left['count_weight'] - rec.count_weight})
        return super(wjzpw_weft_output, self).unlink(cr, uid, ids, context=context)

    _columns = {
        'create_date': fields.datetime('wjzpw.order.anPaiRiQi', readonly=True),  # 数据创建日期
        'output_date': fields.date('wjzpw.inventory.chuKuRiQi', required=True),
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.weft.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'level': fields.selection((('A', 'A'), ('AA', 'AA')), 'wjzpw.inventory.dengJi'),  # 等级
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 零散个数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang', required=True),  # 重量（KG）
        # 'department': fields.many2one('hr.department', 'wjzpw.inventory.shiYongBuMen', required=True)  # 使用部门
        'department': fields.selection((('qdcj', u'前道车间'), ('hdcj', u'后道车间'), ('msb', u'门市部')), 'wjzpw.inventory.shiYongBuMen', required=True)  # 使用部门
    }

    _defaults = {
        'quantity': 0,
        'count': 0,
        'weight': 0
    }

    _order = "create_date desc"


class wjzpw_weft_workshop_left(osv.osv):
    """
    车间剩余
    """
    _name = "wjzpw.weft.workshop.left"
    _description = "wjzpw.inventory.cheJianShengYu"

    def onchange_quantity(self, cr, uid, ids, quantity=None, material_specification=None, material_area=None, batch_no=None, level=None):
        if not quantity or not material_specification or not material_area or not batch_no or not level:
            return {}
        query_sql = """
            SELECT weight, quantity
            FROM wjzpw_weft_input
            WHERE material_specification = %d and material_area = %d and batch_no = %d and level = '%s' order by input_date desc limit 1
            """ % (material_specification, material_area, batch_no, level)
        cr.execute(query_sql)
        weft_input = cr.dictfetchone()
        if weft_input:
            weight = weft_input['weight'] / weft_input['quantity'] * quantity
            return {
                'value': {
                    'weight': weight
                }
            }
        else:
            return {}

    def onchange_material_specification(self, cr, uid, ids, material_specification=None):
        query_sql = """
            SELECT DISTINCT material_area
            FROM wjzpw_weft_input
            WHERE material_specification = %d ORDER BY material_area
            """ % material_specification
        cr.execute(query_sql)
        area_ids = []
        for material_area_id in cr.fetchall():
            area_ids.append(material_area_id[0])

        return {
            'domain': {
                'material_area': [('id', 'in', area_ids)]
            }
        }

    def onchange_material_area(self, cr, uid, ids, material_specification=None, material_area=None):
        query_sql = """
            SELECT DISTINCT batch_no
            FROM wjzpw_weft_input
            WHERE material_specification = %d AND material_area = %d ORDER BY batch_no
            """ % (material_specification, material_area)
        cr.execute(query_sql)
        batch_no_ids = []
        for batch_no in cr.fetchall():
            batch_no_ids.append(batch_no[0])

        return {
            'domain': {
                'batch_no': [('id', 'in', batch_no_ids)]
            }
        }

    def create(self, cr, uid, vals, *args, **kwargs):
        left_obj = super(wjzpw_weft_workshop_left, self).create(cr, uid, vals, *args, **kwargs)
        # Get total input
        cr.execute(
            '''
            SELECT sum(quantity) as quantity, sum(weight) as weight, sum(count) as count, sum(count_weight) as count_weight
            FROM wjzpw_weft_output
            WHERE department = 'hdcj' AND material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s'
            ''' %
            (vals['material_specification'], vals['material_area'], vals['batch_no'], vals['level'])
        )
        input = cr.dictfetchone()
        # Get total output
        cr.execute(
            '''
            SELECT sum(quantity) as quantity, sum(weight) as weight, sum(count) as count, sum(count_weight) as count_weight
            FROM wjzpw_weft_workshop_output
            WHERE material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s'
            ''' %
            (vals['material_specification'], vals['material_area'], vals['batch_no'], vals['level'])
        )
        output = cr.dictfetchone()
        # Calculate
        if not input['quantity'] and not input['weight'] and not input['count'] and not input['count_weight']:
            return left_obj
        new_vals = vals.copy()
        if output['quantity'] or output['weight'] or output['count'] or output['count_weight']:
            new_vals['quantity'] = input['quantity'] - output['quantity'] - vals['quantity']
            new_vals['weight'] = input['weight'] - output['weight'] - vals['weight']
            new_vals['count'] = input['count'] - output['count'] - vals['count']
            new_vals['count_weight'] = input['count_weight'] - output['count_weight'] - vals['count_weight']
        else:
            new_vals['quantity'] = input['quantity'] - vals['quantity']
            new_vals['weight'] = input['weight'] - vals['weight']
            new_vals['count'] = input['count'] - vals['count']
            new_vals['count_weight'] = input['count_weight'] - vals['count_weight']
        output_date = datetime.datetime.strptime(new_vals['input_date'], "%Y-%m-%d") - datetime.timedelta(1)
        new_vals['output_date'] = output_date.strftime('%Y-%m-%d')
        del new_vals['input_date']
        weft_workshop_output_obj = self.pool.get('wjzpw.weft.workshop.output')
        weft_workshop_output_obj.create(cr, uid, new_vals, context=None)
        return left_obj

    _columns = {
        'input_date': fields.date('wjzpw.inventory.ruKuRiQi', required=True),
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.weft.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'level': fields.selection((('A', 'A'), ('AA', 'AA')), 'wjzpw.inventory.dengJi'),  # 等级
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 箱数重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 二次入库零散个数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang'),  # 只数重量
    }

    _default = {
        'quantity': 0,
        'count': 0,
        'weight': 0,
        }

    _order = "input_date desc, quantity desc, count desc"


class wjzpw_weft_workshop_output(osv.osv):
    """
    纬丝的日消耗
    """
    _name = "wjzpw.weft.workshop.output"
    _description = "wjzpw.inventory.riXiaoHao"

    _columns = {
        'output_date': fields.date('wjzpw.inventory.riQi', required=True),
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.weft.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'level': fields.char('wjzpw.inventory.dengJi'),  # 等级
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 箱数重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 二次入库零散个数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang'),  # 只数重量
    }

    _default = {
        'quantity': 0,
        'count': 0,
        'weight': 0,
        }

    _order = "output_date desc"


class wjzpw_reed_input(osv.osv):
    """
    钢筘入库
    """
    _name = "wjzpw.reed.input"
    _description = "wjzpw.inventory.ruKuGuanLi"

    def onchange_calculate_price(self, cr, uid, ids, count=None, price=None):
        if not count or not price:
            return {}
        total_price = count * price
        return {
            'value': {
                'total_price': total_price
            }
        }

    _columns = {
        'input_date': fields.date('wjzpw.inventory.ruKuRiQi', required=True),  # 入库日期
        'reed_no': fields.char('wjzpw.inventory.kouHao', required=True),  # 扣号
        'reed_width': fields.char('wjzpw.inventory.kouFu', required=True),  # 扣辐
        'count': fields.integer('wjzpw.inventory.shuLiang', required=True),  # 数量
        'price': fields.float('wjzpw.inventory.danJia', required=True),  # 单价
        'total_price': fields.float('wjzpw.inventory.jinEr', required=True),  # 金额
        'reed_area': fields.many2one('wjzpw.reed.area', 'wjzpw.inventory.gangKouChanDi'),  # 钢筘产地
        'remark': fields.text('wjzpw.inventory.beiZhu')  # 备注
    }

    _order = "input_date desc"


class wjzpw_reed_output(osv.osv):
    """
    钢筘出库
    """
    _name = "wjzpw.reed.output"
    _description = "wjzpw.inventory.ruKuGuanLi"

    def _get_reed_no_options(self, cr, uid, context=None):
        cr.execute('SELECT DISTINCT reed_no FROM wjzpw_reed_input')
        return [(wri[0], wri[0]) for wri in cr.fetchall()]

    def _get_reed_width_options(self, cr, uid, context=None):
        cr.execute('SELECT DISTINCT reed_width FROM wjzpw_reed_input')
        return [(wri[0], wri[0]) for wri in cr.fetchall()]

    _columns = {
        'output_date': fields.date('wjzpw.inventory.chuKuRiQi', required=True),  # 出库日期
        'reed_no': fields.selection(_get_reed_no_options, 'wjzpw.inventory.kouHao', required=True),  # 扣号
        'reed_width': fields.selection(_get_reed_width_options, 'wjzpw.inventory.kouFu', required=True),  # 扣辐
        'count': fields.integer('wjzpw.inventory.shuLiang', required=True),  # 数量
        'reed_area_to': fields.many2one('wjzpw.reed.area.to', 'wjzpw.inventory.faWangDi'),  # 钢筘发往地
        'status': fields.selection((('wx', u'维修'), ('bf', u'报废')), 'wjzpw.inventory.baoFeiHuoWeiXiu', required=True),  # 报废或维修
        'remark': fields.text('wjzpw.inventory.beiZhu')  # 备注
    }

    _order = "output_date desc"


class wjzpw_inventory(osv.osv):
    """
    培布库存，数据库视图，非是体表
    """
    _name = "wjzpw.inventory"
    _auto = False
    _description = "wjzpw.inventory.kuCun"
    _rec_name = 'product_id'

    _columns = {
        'superior_amount': fields.integer('wjzpw.inventory.youDengPin', readonly=True),  # 优等品数量
        'a_amount': fields.integer('wjzpw.inventory.yiDengPin', readonly=True),  # 一等品数量
        'b_amount': fields.integer('wjzpw.inventory.erDengPin', readonly=True),  # 二等品数量
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing', readonly=True),  # 品名
        'batch_no': fields.many2one('wjzpw.batch.no', 'wjzpw.piHao', readonly=True)  # 批号
    }

    def init(self, cr):
        """
            培布库存
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_inventory')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_inventory AS (
                SELECT row_number() over (order by product_id, batch_no) AS id,product_id, batch_no,
                CASE
                    WHEN ((SELECT count(wio.id) AS count
                        FROM wjzpw_inventory_output wio
                        WHERE wio.product_id = wii.product_id AND wio.batch_no = wii.batch_no)) <> 0
                        THEN
                            (sum(wii.superior_number) -
                            (SELECT sum(superior_number) FROM wjzpw_inventory_output wio WHERE wio.product_id = wii.product_id and wio.batch_no = wii.batch_no))
                        ELSE
                           sum(wii.superior_number)
                END AS superior_amount
                ,CASE
                    WHEN ((SELECT count(wio.id) AS count
                        FROM wjzpw_inventory_output wio
                        WHERE wio.product_id = wii.product_id AND wio.batch_no = wii.batch_no)) <> 0
                        THEN
                            (sum(wii.grade_a_number) -
                            (SELECT sum(grade_a_number) FROM wjzpw_inventory_output wio WHERE wio.product_id = wii.product_id and wio.batch_no = wii.batch_no))
                        ELSE
                           sum(wii.grade_a_number)
                END AS a_amount
                ,CASE
                    WHEN ((SELECT count(wio.id) AS count
                        FROM wjzpw_inventory_output wio
                        WHERE wio.product_id = wii.product_id AND wio.batch_no = wii.batch_no)) <> 0
                        THEN
                            (sum(wii.grade_b_number) -
                            (SELECT sum(grade_b_number) FROM wjzpw_inventory_output wio WHERE wio.product_id = wii.product_id and wio.batch_no = wii.batch_no))
                        ELSE
                           sum(wii.grade_b_number)
                END AS b_amount
                FROM wjzpw_inventory_input wii GROUP BY wii.product_id, wii.batch_no
            )""")

    _order = "product_id, batch_no"


class wjzpw_organzine_inventory(osv.osv):
    """
    经丝库存，数据库视图，非实体表
    """
    _name = "wjzpw.organzine.inventory"
    _auto = False
    _description = "wjzpw.inventory.kuCun"

    _columns = {
        'process_unit': fields.char('wjzpw.inventory.jiaGongDanWei', readonly=True),  # 加工单位
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', readonly=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', readonly=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.piHao', readonly=True),  # 批号
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'count': fields.integer('wjzpw.inventory.geShu'),  # 二次入库零散个数
        'weight': fields.float('wjzpw.inventory.zhongLiang', required=True),  # 重量（KG）
    }

    def init(self, cr):
        """
            经丝库存
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_organzine_inventory')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_organzine_inventory AS (
                SELECT row_number() over (order by process_unit, material_specification, material_area, batch_no) AS id,process_unit, material_specification,material_area,batch_no,
                CASE
                    WHEN ((SELECT count(woo.id) AS count
                        FROM wjzpw_organzine_output woo
                        WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area AND woo.batch_no = woi.batch_no)) <> 0
                        THEN
                            (sum(woi.quantity) -
                            (SELECT sum(quantity) FROM wjzpw_organzine_output woo WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area and woo.batch_no = woi.batch_no))
                        ELSE
                           sum(woi.quantity)
                END AS quantity
                ,CASE
                    WHEN ((SELECT count(woo.id) AS count
                        FROM wjzpw_organzine_output woo
                        WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area AND woo.batch_no = woi.batch_no)) <> 0
                        THEN
                            (sum(woi.count) + sum(woi.quantity_count) -
                            (SELECT sum(count) + sum(quantity_count) FROM wjzpw_organzine_output woo WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area and woo.batch_no = woi.batch_no))
                        ELSE
                           sum(woi.count) + sum(woi.quantity_count)
                END AS count
                ,CASE
                    WHEN ((SELECT count(woo.id) AS count
                        FROM wjzpw_organzine_output woo
                        WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area AND woo.batch_no = woi.batch_no)) <> 0
                        THEN
                            (sum(woi.weight) + sum(woi.count_weight) -
                            (SELECT sum(weight) + sum(count_weight) FROM wjzpw_organzine_output woo WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area and woo.batch_no = woi.batch_no))
                        ELSE
                           sum(woi.weight) + sum(woi.count_weight)
                END AS weight
                FROM wjzpw_organzine_input woi GROUP BY woi.process_unit, woi.material_specification, woi.material_area, woi.batch_no
            )""")

    _order = "process_unit, material_specification, material_area, batch_no"


class wjzpw_weft_inventory(osv.osv):
    """
    纬丝库存，数据库视图，非实体表
    """
    _name = "wjzpw.weft.inventory"
    _auto = False
    _description = "wjzpw.inventory.kuCun"

    _columns = {
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', readonly=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', readonly=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.weft.batch.no', 'wjzpw.piHao', readonly=True),  # 批号
        'level': fields.char('wjzpw.inventory.dengJi', readonly=True),  # 等级
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu', readonly=True),  # 包（或箱）数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu', readonly=True),  # 二次入库零散个数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang', readonly=True),  # 只数重量
        'week_count': fields.float('wjzpw.inventory.shiYongLv', readonly=True),  # 周使用次数
        'month_count': fields.float('wjzpw.inventory.shiYongLv', readonly=True)  # 月使用次数
    }

    def init(self, cr):
        """
            纬丝库存
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_weft_inventory')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_weft_inventory AS (
                SELECT row_number() over (order by material_specification, material_area, batch_no, level) AS id, material_specification,material_area,batch_no,level,
                CASE
                    WHEN ((SELECT count(wwo.id) AS count
                        FROM wjzpw_weft_output wwo
                        WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area AND wwo.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (sum(wwi.quantity) -
                            (SELECT sum(quantity) FROM wjzpw_weft_output wwo WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area and wwo.batch_no = wwi.batch_no))
                        ELSE
                           sum(wwi.quantity)
                END AS quantity
                ,CASE
                    WHEN ((SELECT count(wwo.id) AS count
                        FROM wjzpw_weft_output wwo
                        WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area AND wwo.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (sum(wwi.count) -
                            (SELECT sum(count) FROM wjzpw_weft_output wwo WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area and wwo.batch_no = wwi.batch_no))
                        ELSE
                           sum(wwi.count)
                END AS count
                ,CASE
                    WHEN ((SELECT count(wwo.id) AS count
                        FROM wjzpw_weft_output wwo
                        WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area AND wwo.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (sum(wwi.weight) -
                            (SELECT sum(weight) FROM wjzpw_weft_output wwo WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area and wwo.batch_no = wwi.batch_no))
                        ELSE
                           sum(wwi.weight)
                END AS weight
                ,CASE
                    WHEN ((SELECT count(wwo.id) AS count
                        FROM wjzpw_weft_output wwo
                        WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area AND wwo.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (sum(wwi.count_weight) -
                            (SELECT sum(count_weight) FROM wjzpw_weft_output wwo WHERE wwo.level = wwi.level AND wwo.material_specification = wwi.material_specification AND wwo.material_area = wwi.material_area and wwo.batch_no = wwi.batch_no))
                        ELSE
                           sum(wwi.count_weight)
                END AS count_weight
                , ((SELECT COUNT(id) FROM wjzpw_weft_output weo WHERE weo.level = wwi.level AND weo.material_specification = wwi.material_specification AND weo.material_area = wwi.material_area and weo.batch_no = wwi.batch_no AND weo.create_date > (now() - INTERVAL '7 day'))
                  + (SELECT COUNT(id) FROM wjzpw_weft_workshop_output wwwo WHERE wwwo.level = wwi.level AND wwwo.material_specification = wwi.material_specification AND wwwo.material_area = wwi.material_area and wwwo.batch_no = wwi.batch_no AND wwwo.create_date > (now() - INTERVAL '7 day')))
                  AS week_count
                , ((SELECT COUNT(id) FROM wjzpw_weft_output weo WHERE weo.level = wwi.level AND weo.material_specification = wwi.material_specification AND weo.material_area = wwi.material_area and weo.batch_no = wwi.batch_no AND weo.create_date > (now() - INTERVAL '30 day'))
                  + (SELECT COUNT(id) FROM wjzpw_weft_workshop_output wwwo WHERE wwwo.level = wwi.level AND wwwo.material_specification = wwi.material_specification AND wwwo.material_area = wwi.material_area and wwwo.batch_no = wwi.batch_no AND wwwo.create_date > (now() - INTERVAL '30 day')))
                  AS month_count
                FROM wjzpw_weft_input wwi GROUP BY wwi.material_specification, wwi.material_area, wwi.batch_no, wwi.level
            )""")

    _order = "week_count desc, month_count desc, material_specification, material_area, batch_no, level"


class wjzpw_weft_total_inventory(osv.osv):
    """
    纬丝总库存，包括仓库库存和车间库存，数据库视图，非实体表
    """
    _name = "wjzpw.weft.total.inventory"
    _auto = False
    _description = "wjzpw.inventory.zongKuCun"

    _columns = {
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', readonly=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', readonly=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.weft.batch.no', 'wjzpw.piHao', readonly=True),  # 批号
        'level': fields.char('wjzpw.inventory.dengJi', readonly=True),  # 等级
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu', readonly=True),  # 包（或箱）数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu', readonly=True),  # 二次入库零散个数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang', readonly=True),
        'week_count': fields.float('wjzpw.inventory.shiYongLv', readonly=True),  # 周使用次数
        'month_count': fields.float('wjzpw.inventory.shiYongLv', readonly=True)  # 月使用次数
    }

    def init(self, cr):
        """
            纬丝总库存
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_weft_total_inventory')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_weft_total_inventory AS (
                SELECT row_number() over (order by material_specification, material_area, batch_no, level) AS id, material_specification,material_area,batch_no,level,
                CASE
                    WHEN ((SELECT count(wwwl.id) AS count
                        FROM wjzpw_weft_workshop_left wwwl
                        WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area AND wwwl.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (wwi.quantity +
                            (SELECT quantity FROM wjzpw_weft_workshop_left wwwl WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area and wwwl.batch_no = wwi.batch_no order by input_date desc, quantity desc, count desc limit 1))
                        ELSE
                            wwi.quantity
                END AS quantity
                ,CASE
                    WHEN ((SELECT count(wwwl.id) AS count
                        FROM wjzpw_weft_workshop_left wwwl
                        WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area AND wwwl.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (wwi.count +
                            (SELECT count FROM wjzpw_weft_workshop_left wwwl WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area and wwwl.batch_no = wwi.batch_no order by input_date desc, quantity desc, count desc limit 1))
                        ELSE
                           wwi.count
                END AS count
                ,CASE
                    WHEN ((SELECT count(wwwl.id) AS count
                        FROM wjzpw_weft_workshop_left wwwl
                        WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area AND wwwl.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (wwi.weight +
                            (SELECT weight FROM wjzpw_weft_workshop_left wwwl WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area and wwwl.batch_no = wwi.batch_no order by input_date desc, quantity desc, count desc limit 1))
                        ELSE
                           wwi.weight
                END AS weight
                ,CASE
                    WHEN ((SELECT count(wwwl.id) AS count
                        FROM wjzpw_weft_workshop_left wwwl
                        WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area AND wwwl.batch_no = wwi.batch_no)) <> 0
                        THEN
                            (wwi.count_weight +
                            (SELECT count_weight FROM wjzpw_weft_workshop_left wwwl WHERE wwwl.level = wwi.level AND wwwl.material_specification = wwi.material_specification AND wwwl.material_area = wwi.material_area and wwwl.batch_no = wwi.batch_no order by input_date desc, quantity desc, count desc limit 1))
                        ELSE
                           wwi.count_weight
                END AS count_weight
                , ((SELECT COUNT(id) FROM wjzpw_weft_output weo WHERE weo.level = wwi.level AND weo.material_specification = wwi.material_specification AND weo.material_area = wwi.material_area and weo.batch_no = wwi.batch_no AND weo.create_date > (now() - INTERVAL '7 day'))
                  + (SELECT COUNT(id) FROM wjzpw_weft_workshop_output wwwo WHERE wwwo.level = wwi.level AND wwwo.material_specification = wwi.material_specification AND wwwo.material_area = wwi.material_area and wwwo.batch_no = wwi.batch_no AND wwwo.create_date > (now() - INTERVAL '7 day')))
                  AS week_count
                , ((SELECT COUNT(id) FROM wjzpw_weft_output weo WHERE weo.level = wwi.level AND weo.material_specification = wwi.material_specification AND weo.material_area = wwi.material_area and weo.batch_no = wwi.batch_no AND weo.create_date > (now() - INTERVAL '30 day'))
                  + (SELECT COUNT(id) FROM wjzpw_weft_workshop_output wwwo WHERE wwwo.level = wwi.level AND wwwo.material_specification = wwi.material_specification AND wwwo.material_area = wwi.material_area and wwwo.batch_no = wwi.batch_no AND wwwo.create_date > (now() - INTERVAL '30 day')))
                  AS month_count
                FROM wjzpw_weft_inventory wwi
            )""")

    _order = "week_count desc, month_count desc, material_specification, material_area, batch_no, level"


class wjzpw_reed_inventory(osv.osv):
    """
    钢筘库存，数据库视图，非实体表
    """
    _name = "wjzpw.reed.inventory"
    _auto = False
    _description = "wjzpw.inventory.kuCun"

    _columns = {
        'reed_no': fields.char('wjzpw.inventory.kouHao', readonly=True),  # 筘号
        'reed_width': fields.char('wjzpw.inventory.kouFu', readonly=True),  # 筘幅
        'count': fields.integer('wjzpw.inventory.shuLiang'),  # 数量
    }

    def init(self, cr):
        """
            钢筘库存
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_reed_inventory')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_reed_inventory AS (
                SELECT row_number() over (order by reed_no, reed_width) AS id,reed_no, reed_width,
                CASE
                    WHEN ((SELECT count(wro.id) AS count
                        FROM wjzpw_reed_output wro
                        WHERE wro.reed_no = wri.reed_no AND wro.reed_width = wri.reed_width)) <> 0
                        THEN
                            (sum(wri.count) -
                            (SELECT sum(count) FROM wjzpw_reed_output wro WHERE wro.reed_no = wri.reed_no AND wro.reed_width = wri.reed_width))
                        ELSE
                           sum(wri.count)
                END AS count
                FROM wjzpw_reed_input wri GROUP BY wri.reed_no, wri.reed_width
            )""")

    _order = "reed_no, reed_width"


wjzpw_inventory_input()
wjzpw_inventory_output()
wjzpw_inventory_machine_output()
wjzpw_inventory()
wjzpw_organzine_input()
wjzpw_flow_no()
wjzpw_organzine_output()
wjzpw_organzine_inventory()
wjzpw_weft_input()
wjzpw_weft_output()
wjzpw_weft_inventory()
wjzpw_reed_input()
wjzpw_reed_output()
wjzpw_reed_inventory()
wjzpw_weft_total_inventory()
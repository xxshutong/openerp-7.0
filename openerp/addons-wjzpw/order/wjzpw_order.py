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

import logging
from openerp.osv import fields, osv


_logger = logging.getLogger(__name__)


class wjzpw_order_product(osv.osv):
    """
    客户品名
    """
    _name = "wjzpw.order.product"
    _description = "wjzpw.order.keHuPinMingGuanLi"

    _columns = {
        'name': fields.char('wjzpw.order.keHuPinMing', size=64, required=True),
        'customer': fields.many2one('res.partner', 'wjzpw.order.keHu', domain=[('customer', '=', True)],
                                    required=True, readonly=True),
    }
    _sql_constraints = [
        ('name_customer_unique', 'unique(name, customer)', u'该客户品名已经存在'),
        ]

    _order = "name"

class wjzpw_order(osv.osv):
    """
    订单入库
    """
    _name = "wjzpw.order"
    _description = "wjzpw.order.dingDanGuanLi"
    _order_prefix = "SWS"

    def _default_order_no(self, cr, uid, context=None):
        default_no = self._default_no(cr, uid, context=context)
        return  '%s%04d' % (self._order_prefix, default_no)

    def _default_no(self, cr, uid, context=None):
        query_sql = """
            SELECT max(no)
            FROM wjzpw_order
            """
        cr.execute(query_sql)
        order = cr.dictfetchone()['max']
        if not order:
            return 1
        else:
            return order + 1

    def onchange_customer(self, cr, uid, ids, customer=None, context={}):
        if not customer:
            return {}
        # Get existing company no
        query_sql = """
            SELECT count(company_no) AS num, company_no
            FROM wjzpw_order
            WHERE customer = %d GROUP BY company_no order by num desc limit 1
        """ % customer
        cr.execute(query_sql)
        company_no_result = cr.dictfetchone()
        company_no_value = ''
        if company_no_result:
            company_no_value = company_no_result['company_no']
        return {
            'domain': {
                'customer_product': [('customer', '=', customer)]
            },
            'value': {
                'company_no': company_no_value
            }
        }

    def _company_no_product(self, cr, uid, ids, field_name, arg, context):
        """
        公司编号及品名
        """
        res = {}
        for id in ids:
            res.setdefault(id, u'无')
        for rec in self.browse(cr, uid, ids, context=context):
            company_no_product = ''
            if rec.company_no:
                company_no_product += rec.company_no
            if rec.product_id:
                company_no_product += rec.product_id['name']
            res[rec.id] = company_no_product
        return res

    def _dead_line_str(self, cr, uid, ids, field_name, arg, context):
        """
        交货期
        """
        res = {}
        for id in ids:
            res.setdefault(id, u'无')
        for rec in self.browse(cr, uid, ids, context=context):
            dead_line = ''
            if rec.dead_line and rec.dead_line_unit:
                dead_line = str(rec.dead_line) + ' ' + rec.dead_line_unit
            res[rec.id] = dead_line
        return res

    def _order_type(self, cr, uid, ids, field_name, arg, context):
        """
        订单类型，新品或者翻单
        """
        res = {}
        for id in ids:
            res.setdefault(id, u'新品')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_id and rec.input_date:
                query_sql = """
                    SELECT id
                    FROM wjzpw_order
                    WHERE product_id = %d AND input_date < '%s'
                    """ % (rec.product_id, rec.input_date)
                cr.execute(query_sql)
                existing_order = cr.dictfetchone()
                if existing_order:
                    res[rec.id] = u'翻单'
                else:
                    res[rec.id] = u'新品'
        return res

    _columns = {
        'order_no': fields.char('wjzpw.order.dingDanHao', required=True, readonly=True),
        'no': fields.integer('wjzpw.order.dingDanZhengShuHaoMa', required=True, readonly=True),
        'input_date': fields.date('wjzpw.order.xiaDanRiQi', required=True),
        'customer': fields.many2one('res.partner', 'wjzpw.order.keHu', domain=[('customer', '=', True)],
                                    required=True),
        'customer_product': fields.many2one('wjzpw.order.product', 'wjzpw.order.keHuPinMing'),
        'company_no': fields.char('wjzpw.order.gongSiBianHao'),
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.order.gongSiPinMing', required=True),
        'amount': fields.float('wjzpw.order.shuLiangMi', required=True),
        'dead_line': fields.float('wjzpw.order.jiaoHuoQi'),
        'dead_line_unit': fields.selection(((u'天', u'天'), (u'周', u'周'), (u'月', u'月')), 'wjzpw.order.danWei', required=True),
        # 'order_type': fields.selection((('new', u'新品'), ('old', u'翻单')), 'wjzpw.order.xinPinHuoFanDan'),
        'product_type': fields.selection((('order', u'订单'), ('inventory', u'库存')), 'wjzpw.order.dingDanHuoKuCun'),
        'customer_requirement': fields.text('wjzpw.order.keHuYaoQiu'),
        'remark': fields.text('wjzpw.order.beiZhu'),
        'status': fields.selection((('unfinished', u'未完成'), ('finished', u'完成')), 'wjzpw.order.shiFouWanCheng'),

        # Function fields
        'company_no_product': fields.function(_company_no_product, string='wjzpw.order.gongSiBianHaoJiPinMing', type='char', method=True),  # 公司编号及品名
        'dead_line_str': fields.function(_dead_line_str, string='wjzpw.order.jiaoHuoQi', type='char', method=True),  # 交货期
        'order_type': fields.function(_order_type, string='wjzpw.order.xinPinHuoFanDan', type='char', method=True)  # 新品或翻单
    }

    _defaults = {
        'order_no': _default_order_no,
        'no': _default_no,
        'dead_line_unit': u'天',
        'status': 'unfinished'
    }

    _sql_constraints = [
        ('no_unique', 'unique(no)', u'该订单号已经存在'),
        ('order_no_unique', 'unique(order_no)', u'该订单号已经存在'),
    ]

    _order = "order_no desc"

wjzpw_order()

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
        context['customer'] = customer
        return {
            'domain': {
                'customer_product': [('customer', '=', customer)]
            }
        }

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
        'dead_line_unit': fields.selection((('d', u'天'), ('w', u'周'), ('m', u'月')), 'wjzpw.order.danWei', required=True),
        'order_type': fields.selection((('new', u'新品'), ('old', u'翻单')), 'wjzpw.order.xinPinHuoFanDan'),
        'product_type': fields.selection((('order', u'订单'), ('inventory', u'库存')), 'wjzpw.order.dingDanHuoKuCun'),
        'customer_requirement': fields.text('wjzpw.order.keHuYaoQiu'),
        'remark': fields.text('wjzpw.order.beiZhu'),
        'status': fields.selection((('unfinished', u'未完成'), ('finished', u'完成')), 'wjzpw.order.shiFouWanCheng')
    }

    _defaults = {
        'order_no': _default_order_no,
        'no': _default_no,
        'dead_line_unit': 'd',
        'status': 'unfinished'
    }

    _sql_constraints = [
        ('no_unique', 'unique(no)', u'该订单号已经存在'),
        ('order_no_unique', 'unique(order_no)', u'该订单号已经存在'),
    ]

    _order = "order_no desc"

wjzpw_order()

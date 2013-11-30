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


class wjzpw_inventory_input(osv.osv):
    _name = "wjzpw.inventory.input"
    _description = "wjzpw.inventory.ruKuGuanLi"

    _columns = {
        'machine_no': fields.integer('wjzpw.inventory.jiHao', required=True),
        'input_date': fields.datetime('wjzpw.inventory.luRuRiQi', required=True),
        'superior_number': fields.float('wjzpw.inventory.youDengPin', required=True),
        'grade_a_number': fields.float('wjzpw.inventory.yiDengPin', required=True),
        'grade_b_number': fields.float('wjzpw.inventory.erDengPin', required=True),
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing', required=True),
        'batch_no': fields.many2one('wjzpw.batch.no', 'wjzpw.piHao', required=True),
        # 'machineOutputId': fields.many2one('wjzpw.inventory', 'wjzpw.inventory.jiTaiChanChu', required=False)
    }

    _defaults = {
        "superior_number": 0,
        "grade_a_number": 0,
        "grade_b_number": 0
    }

    _order = "product_id"


class wjzpw_inventory_output(osv.osv):
    _name = "wjzpw.inventory.output"
    _description = "wjzpw.inventory.chuKuGuanLi"

    _columns = {
        'input_date': fields.datetime('wjzpw.inventory.luRuRiQi', required=True),
        'code': fields.char('wjzpw.inventory.maDan', size=60, required=False),
        'superior_number': fields.float('wjzpw.inventory.youDengPin', required=True),
        'grade_a_number': fields.float('wjzpw.inventory.yiDengPin', required=True),
        'grade_b_number': fields.float('wjzpw.inventory.erDengPin', required=True),
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

    _order = "product_id"


wjzpw_inventory_input()
wjzpw_inventory_output()
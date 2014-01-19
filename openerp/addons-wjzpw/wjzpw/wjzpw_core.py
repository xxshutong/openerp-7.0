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
from reportlab.pdfbase._fontdata import _Name2StandardEncodingMap

_logger = logging.getLogger(__name__)


class wjzpw_product(osv.osv):
    """
    品名管理
    """

    _name = "wjzpw.product"
    _description = "Product Management"

    _columns = {
        'name': fields.char('Product Name', size=64, required=True),
        'description': fields.text('Description')
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该品名已经存在'),
    ]

    _defaults = {
    }
    _order = "name"


class wjzpw_batch_no(osv.osv):
    """
    批号管理
    """
    _name = "wjzpw.batch.no"
    _description = "Batch No Management"

    _columns = {
        'name': fields.char('Batch No', size=64, required=True),
        'description': fields.text('Description')
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该批号已经存在'),
    ]
    _defaults = {
    }
    _order = "name"


class wjzpw_material_specifications(osv.osv):
    """
    原料规格管理
    """
    _name = "wjzpw.material.specification"
    _description = "wjzpw.yuanLiaoGuiGeGuanLi"

    def _name_get(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] = rec.specification
        return res

    _columns = {
        'specification': fields.char('wjzpw.guiGe', size=64, required=True),
        'description': fields.text('Description'),
        'name': fields.function(_name_get, string="wjzpw.inventory.yuanLiaoGuiGe", type='char',
                                method=True)
    }
    _sql_constraints = [
        ('specification_unique', 'unique(specification)', u'该原料规格已经存在'),
    ]

    _order = "specification"


class wjzpw_organzine_batch_no(osv.osv):
    """
    经丝批号管理
    """
    _name = "wjzpw.organzine.batch.no"
    _description = "wjzpw.jingSiPiHaoGuanLi"

    _columns = {
        'name': fields.char('wjzpw.jingSiPiHao', size=64, required=True),
        'description': fields.text('Description')
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该经丝批号已经存在'),
    ]
    _defaults = {
    }
    _order = "name"


class wjzpw_weft_batch_no(osv.osv):
    """
    纬丝批号管理
    """
    _name = "wjzpw.weft.batch.no"
    _description = "wjzpw.weiSiPiHaoGuanLi"

    _columns = {
        'name': fields.char('wjzpw.weiSiPiHao', size=64, required=True),
        'description': fields.text('Description')
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该纬丝批号已经存在'),
    ]
    _defaults = {
    }
    _order = "name"


class wjzpw_material_area(osv.osv):
    """
    原料产地管理
    """
    _name = "wjzpw.material.area"
    _description = "wjzpw.chanDiGuanLi"

    _columns = {
        'name': fields.char('wjzpw.chanDi', size=64, required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该原料产地已经存在'),
    ]

    _order = "name"


class wjzpw_reed_area(osv.osv):
    """
    钢筘产地管理
    """
    _name = "wjzpw.reed.area"
    _description = "wjzpw.chanDiGuanLi"

    _columns = {
        'name': fields.char('wjzpw.chanDi', size=64, required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该产地已经存在'),
    ]

    _order = "name"


class wjzpw_reed_area_to(osv.osv):
    """
    钢筘发往地管理
    """
    _name = "wjzpw.reed.area.to"
    _description = "wjzpw.faWangDiGuanLi"

    _columns = {
        'name': fields.char('wjzpw.faWangDi', size=64, required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该发往地已经存在'),
    ]

    _order = "name"


class wjzpw_cloth_requirement(osv.osv):
    """
    坯布要求
    """
    _name = "wjzpw.cloth.requirement"
    _description = "wjzpw.piBuYaoQiu"

    _columns = {
        'name': fields.char('wjzpw.piBuYaoQiu', size=164, required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该坯布要求已经存在'),
        ]

    _order = "name"


class wjzpw_basic_organization(osv.osv):
    """
    基本组织
    """
    _name = "wjzpw.basic.organization"
    _description = "wjzpw.jiBenZuZhi"

    _columns = {
        'name': fields.char('wjzpw.jiBenZuZhi', size=64, required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique(name)', u'该基本组织已经存在'),
        ]

    _order = "name"


# class wjzpw_order_plan_remark(osv.osv):
#     """
#     生产计划备注
#     """
#     _name = "wjzpw.order.plan.remark"
#     _description = "wjzpw.shengChanJiHuaBeiZhu"
#
#     _columns = {
#         'name': fields.char('wjzpw.shengChanJiHuaBeiZhu', size=164, required=True)
#     }
#     _sql_constraints = [
#         ('name_unique', 'unique(name)', u'该生产计划备注已存在'),
#         ]
#
#     _order = "name"

wjzpw_product()
wjzpw_batch_no()
wjzpw_material_specifications()
wjzpw_organzine_batch_no()
wjzpw_weft_batch_no()
wjzpw_material_area()
wjzpw_reed_area()
wjzpw_reed_area_to()
wjzpw_cloth_requirement()
wjzpw_basic_organization()
# wjzpw_order_plan_remark()
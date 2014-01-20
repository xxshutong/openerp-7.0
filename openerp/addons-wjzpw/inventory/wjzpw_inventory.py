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
import datetime
from openerp import tools

from openerp.osv import fields, osv

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

    _columns = {
        'machine_no': fields.integer('wjzpw.inventory.jiHao', required=True),
        'input_date': fields.date('wjzpw.inventory.luRuRiQi', required=True),
        'superior_number': fields.float('wjzpw.inventory.youDengPin', required=True),
        'grade_a_number': fields.float('wjzpw.inventory.yiDengPin', required=True),
        'grade_b_number': fields.float('wjzpw.inventory.erDengPin', required=True),
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.pinMing', required=True),
        'batch_no': fields.many2one('wjzpw.batch.no', 'wjzpw.piHao', required=True),
        'machine_output_id': fields.many2one('wjzpw.inventory.machine.output', 'wjzpw.inventory.jiTaiChanChu',
                                             required=False)
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

    _order = "product_id"


class wjzpw_inventory_output(osv.osv):
    """
    坯布出库
    """
    _name = "wjzpw.inventory.output"
    _description = "wjzpw.inventory.chuKuGuanLi"

    _columns = {
        'input_date': fields.date('wjzpw.inventory.luRuRiQi', required=True),
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
        'weight_avg': fields.float('wjzpw.inventory.tongZiJingZhong'),  # 筒子净重
        'quantity_avg': fields.integer('wjzpw.inventory.meiBaoXiangZhiShu'),  # 每包箱只数
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'quantity_count': fields.integer('wjzpw.inventory.baoXiangZhiShu'),  # 包/箱只数
        'weight': fields.float('wjzpw.inventory.xiangShuZhongLiang', required=True),  # 箱数重量（KG）
        'count': fields.integer('wjzpw.inventory.zhiShu'),  # 只数
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang'),  # 只数重量

        # Function fields
        'total_count': fields.function(_total_count,
                                       string='wjzpw.inventory.zongZhiShu',
                                       type='integer',
                                       method=True),  # 总只数
        'total_weight': fields.function(_total_weight, string='wjzpw.inventory.zongZhongLiang', type='float', method=True),  #总重量
        'department': fields.many2one('hr.department', 'wjzpw.inventory.shiYongBuMen', required=True)  # 使用部门
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
        left_output = super(wjzpw_weft_output, self).create(cr, uid, vals, *args, **kwargs)
        if vals['department'] != 'hdcj':
            return left_output
        new_vals = {}
        new_vals['material_specification'] = vals['material_specification']
        new_vals['material_area'] = vals['material_area']
        new_vals['batch_no'] = vals['batch_no']
        new_vals['level'] = vals['level']
        # Get latest weft workshop left
        cr.execute(
            '''
            SELECT input_date, quantity, weight, count, count_weight
            FROM wjzpw_weft_workshop_left
            WHERE material_specification = %d AND material_area = %d AND batch_no = %d AND level = '%s' ORDER BY input_date desc limit 1
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

    _columns = {
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

    _order = "output_date desc"


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
        'superior_amount': fields.float('wjzpw.inventory.youDengPin', readonly=True),  # 优等品数量
        'a_amount': fields.float('wjzpw.inventory.yiDengPin', readonly=True),  # 一等品数量
        'b_amount': fields.float('wjzpw.inventory.erDengPin', readonly=True),  # 二等品数量
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
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang', readonly=True)
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
                FROM wjzpw_weft_input wwi GROUP BY wwi.material_specification, wwi.material_area, wwi.batch_no, wwi.level
            )""")

    _order = "material_specification, material_area, batch_no, level"


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
        'count_weight': fields.float('wjzpw.inventory.zhiShuZhongLiang', readonly=True)
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
                FROM wjzpw_weft_inventory wwi
            )""")

    _order = "material_specification, material_area, batch_no, level"


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
wjzpw_organzine_output()
wjzpw_organzine_inventory()
wjzpw_weft_input()
wjzpw_weft_output()
wjzpw_weft_inventory()
wjzpw_reed_input()
wjzpw_reed_output()
wjzpw_reed_inventory()
wjzpw_weft_total_inventory()
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


class wjzpw_inventory_input(osv.osv):
    """
    坯布入库
    """
    _name = "wjzpw.inventory.input"
    _description = "wjzpw.inventory.ruKuGuanLi"

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
        "grade_b_number": 0
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

    _columns = {
        'input_date': fields.date('wjzpw.inventory.ruKuRiQi', required=True),
        'process_unit': fields.char('wjzpw.inventory.jiaGongDanWei'),  # 加工单位
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'height': fields.float('wjzpw.inventory.zhongLiang', required=True),  # 重量（KG）
        'count': fields.integer('wjzpw.inventory.geShu'),  # 二次入库零散个数
        'is_second': fields.boolean('wjzpw.inventory.shiFouErCiRuKu')  # 是否为二次入库
    }

    _default = {
        'quantity': 0,
        'count': 0,
        'is_second': False
    }

    _order = "input_date desc"


class wjzpw_organzine_output(osv.osv):
    """
    经丝出库
    """
    _name = "wjzpw.organzine.output"
    _description = "wjzpw.inventory.chuKuGuanLi"

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

    _columns = {
        'output_date': fields.date('wjzpw.inventory.chuKuRiQi', required=True),
        'process_unit': fields.selection(_get_process_unit_options, 'wjzpw.inventory.jiaGongDanWei', required=True),  # 加工单位
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.piHao', required=True),  # 批号
        'quantity': fields.integer('wjzpw.inventory.baoHuoXiangShu'),  # 包（或箱）数
        'count': fields.integer('wjzpw.inventory.geShu'),  # 零散个数
        'height': fields.float('wjzpw.inventory.zhongLiang', required=True),  # 重量（KG）
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
        'height': fields.float('wjzpw.inventory.zhongLiang', required=True),  # 重量（KG）
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
                            (sum(woi.count) -
                            (SELECT sum(count) FROM wjzpw_organzine_output woo WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area and woo.batch_no = woi.batch_no))
                        ELSE
                           sum(woi.count)
                END AS count
                ,CASE
                    WHEN ((SELECT count(woo.id) AS count
                        FROM wjzpw_organzine_output woo
                        WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area AND woo.batch_no = woi.batch_no)) <> 0
                        THEN
                            (sum(woi.height) -
                            (SELECT sum(height) FROM wjzpw_organzine_output woo WHERE woo.process_unit = woi.process_unit AND woo.material_specification = woi.material_specification AND woo.material_area = woi.material_area and woo.batch_no = woi.batch_no))
                        ELSE
                           sum(woi.height)
                END AS height
                FROM wjzpw_organzine_input woi GROUP BY woi.process_unit, woi.material_specification, woi.material_area, woi.batch_no
            )""")

    _order = "process_unit, material_specification, material_area, batch_no"


wjzpw_inventory_input()
wjzpw_inventory_output()
wjzpw_organzine_input()
wjzpw_organzine_output()
wjzpw_inventory_machine_output()
wjzpw_inventory()
wjzpw_organzine_inventory()
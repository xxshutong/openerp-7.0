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
from datetime import datetime
from openerp import tools
from openerp.osv import fields, osv


class wjzpw_outside_warp_axes_input(osv.osv):
    """
    外加工经轴入库记录
    """
    _name = "wjzpw.outside.warp.axes.input"
    _auto = False
    _description = "wjzpw.inventory.waiJiaGongJingZhouRuKu"

    _columns = {
        'create_date': fields.datetime('wjzpw.produce.chuangJianRiQi', readonly=True),  # 数据创建日期
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.produce.liuChengBianHao', required=True),  # 流程编号
        'process_unit': fields.char('wjzpw.produce.jiaGongDanWei'),  # 加工单位
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.produce.pinMing', required=True),  # 品名
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'door_width': fields.char('wjzpw.produce.menFu'),  # 门幅
        'total_swing_number': fields.integer('wjzpw.produce.touWen'),  # 总经数/头纹
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.produce.yuanLiaoChanDi'),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.produce.piHao', required=True),  # 批号
        'remark': fields.char('wjzpw.produce.beiZhu'),  # 备注
        'axes_no': fields.char('wjzpw.produce.zhouHao'),  # 轴号
        'texture_axis_meter': fields.integer('wjzpw.produce.zhiZhouMiShu'),  # 织轴米数
    }

    def init(self, cr):
        """
            获取外加工经轴入库
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_outside_warp_axes_input')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_outside_warp_axes_input AS (
                SELECT row_number() over (order by wpbzor.create_date DESC) AS id, wpbzor.create_date, wpbzo.machine_no, wpqj.flow_no, wpqj.process_unit, wpqj.product_id, wpqj.material_area, wpqj.batch_no
                , wpqj.material_specification, wpbzo.door_width, wpqj.swing_number * wpqj.axes_number as total_swing_number, wpbzor.remark, wpbzor.axes_no, wpbzor.texture_axis_meter
                FROM wjzpw_produce_qian_jing wpqj, wjzpw_produce_bing_zhou_output wpbzo, wjzpw_produce_bing_zhou_output_record wpbzor
                WHERE wpqj.flow_no = wpbzo.flow_no AND wpbzo.id = wpbzor.wjzpw_produce_bing_zhou_output and wpqj.process_unit <> '%s'
                ORDER BY wpbzor.create_date DESC
            )""" % u'本厂')

    _order = "create_date desc"


class wjzpw_self_warp_axes_input(osv.osv):
    """
    本厂经轴入库记录
    """
    _name = "wjzpw.self.warp.axes.input"
    _auto = False
    _description = "wjzpw.inventory.benChangJingZhouRuKu"

    _columns = {
        'create_date': fields.datetime('wjzpw.produce.chuangJianRiQi', readonly=True),  # 数据创建日期
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.produce.liuChengBianHao', required=True),  # 流程编号
        'process_unit': fields.char('wjzpw.produce.jiaGongDanWei'),  # 加工单位
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.produce.pinMing', required=True),  # 品名
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'door_width': fields.char('wjzpw.produce.menFu'),  # 门幅
        'total_swing_number': fields.integer('wjzpw.produce.touWen'),  # 总经数/头纹
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.produce.yuanLiaoChanDi'),  # 原料产地
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.produce.piHao', required=True),  # 批号
        'remark': fields.char('wjzpw.produce.beiZhu'),  # 备注
        'axes_no': fields.char('wjzpw.produce.zhouHao'),  # 轴号
        'texture_axis_meter': fields.integer('wjzpw.produce.zhiZhouMiShu'),  # 织轴米数
    }

    def init(self, cr):
        """
            获取本厂经轴入库
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'wjzpw_self_warp_axes_input')
        cr.execute("""
            CREATE OR REPLACE VIEW wjzpw_self_warp_axes_input AS (
                SELECT row_number() over (order by wpbzor.create_date DESC) AS id, wpbzor.create_date, wpbzo.machine_no, wpqj.flow_no, wpqj.process_unit, wpqj.product_id, wpqj.material_area, wpqj.batch_no
                , wpqj.material_specification, wpbzo.door_width, wpqj.swing_number * wpqj.axes_number as total_swing_number, wpbzor.remark, wpbzor.axes_no, wpbzor.texture_axis_meter
                FROM wjzpw_produce_qian_jing wpqj, wjzpw_produce_bing_zhou_output wpbzo, wjzpw_produce_bing_zhou_output_record wpbzor
                WHERE wpqj.flow_no = wpbzo.flow_no AND wpbzo.id = wpbzor.wjzpw_produce_bing_zhou_output and wpqj.process_unit = '%s'
                ORDER BY wpbzor.create_date DESC
            )""" % u'本厂')

    _order = "create_date desc"


class wjzpw_outside_warp_axes_output(osv.osv):
    """
    外加工经轴出库
    """
    _name = "wjzpw.outside.warp.axes.output"
    _description = "wjzpw.inventory.waiJiaGongJingZhouChuKu"

    def onchange_flow_no(self, cr, uid, ids, flow_no=None, context={}):
        """
        根据flow_no自动获取其他信息
        """
        if flow_no:
            query_sql = """
                SELECT *
                FROM wjzpw_produce_qian_jing wpqj, wjzpw_produce_bing_zhou_output wpbzo, wjzpw_produce_bing_zhou_output_record wpbzor
                WHERE wpqj.flow_no = wpbzo.flow_no AND wpbzo.id = wpbzor.wjzpw_produce_bing_zhou_output AND wpqj.flow_no = %d
            """ % flow_no
            cr.execute(query_sql)
            result_list = cr.dictfetchall()
            if result_list and len(result_list) >= 1:
                return {
                    'value': {
                        'process_unit': result_list[0]['process_unit'],
                        'material_area': result_list[0]['material_area'],
                        'material_specification': result_list[0]['material_specification'],
                        'batch_no': result_list[0]['batch_no'],
                        'product_id': result_list[0]['product_id'],
                        'door_width': result_list[0]['door_width'],
                        'total_swing_number': result_list[0]['swing_number'] * result_list[0]['axes_number'],
                        # 'axes_no': result_list[0]['axes_no'],
                        # 'texture_axis_meter': result_list[0]['texture_axis_meter'],
                        # 'axes_number': result_list[0]['axes_number']
                    }
                }
        return {}

    def onchange_axes_unit_price(self, cr, uid, ids, texture_axis_meter=None, axes_number=None, price_unit=None):
        """
        计算总金额
        """
        if texture_axis_meter and axes_number and price_unit:
            return {
                'value': {
                    'price': float(texture_axis_meter) * float(axes_number) * price_unit
                }
            }
        return {}

    def _get_process_unit_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT process_unit, create_date
            FROM wjzpw_produce_bing_zhou_output
            ORDER BY create_date DESC
            """
        cr.execute(query_sql)
        keyValues = []
        for process_unit in cr.fetchall():
            keyValues.append((process_unit[0], process_unit[0]))
        return tuple(keyValues)

    def _get_door_width_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT door_width, create_date
            FROM wjzpw_produce_bing_zhou_output
            ORDER BY create_date DESC
            """
        cr.execute(query_sql)
        keyValues = []
        for door_width in cr.fetchall():
            keyValues.append((door_width[0], door_width[0]))
        return tuple(keyValues)

    def _get_total_swing_number_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT swing_number * axes_number as total_swing_number, create_date
            FROM wjzpw_produce_qian_jing
            ORDER BY create_date DESC
            """
        cr.execute(query_sql)
        keyValues = []
        for total_swing_number in cr.fetchall():
            keyValues.append((str(total_swing_number[0]), str(total_swing_number[0])))
        return tuple(keyValues)

    def _get_axes_no_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT axes_no, create_date
            FROM wjzpw_produce_bing_zhou_output_record
            ORDER BY create_date DESC
            """
        cr.execute(query_sql)
        keyValues = []
        for axes_no in cr.fetchall():
            keyValues.append((axes_no[0], axes_no[0]))
        return tuple(keyValues)

    def _get_texture_axis_meter_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT texture_axis_meter, create_date
            FROM wjzpw_produce_bing_zhou_output_record
            ORDER BY create_date DESC
            """
        cr.execute(query_sql)
        keyValues = []
        for texture_axis_meter in cr.fetchall():
            keyValues.append((str(texture_axis_meter[0]), str(texture_axis_meter[0])))
        return tuple(keyValues)

    def _get_axes_number_options(self, cr, uid, context=None):
        query_sql = """
            SELECT DISTINCT axes_number, create_date
            FROM wjzpw_produce_qian_jing
            ORDER BY create_date DESC
            """
        cr.execute(query_sql)
        keyValues = []
        for axes_number in cr.fetchall():
            keyValues.append((str(axes_number[0]), str(axes_number[0])))
        return tuple(keyValues)

    _columns = {
        'input_date': fields.date('wjzpw.inventory.riQi', required=True),  # 录入日期
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.inventory.liuChengBianHao', required=True),  # 流程编号
        'process_unit': fields.selection(_get_process_unit_options, 'wjzpw.inventory.jiaGongDanWei', required=True),  # 加工单位
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.inventory.yuanLiaoChanDi', required=True),  # 原料产地
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.inventory.piHao', required=True),  # 批号
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.inventory.pinMing', required=True),  # 品名
        'door_width': fields.selection(_get_door_width_options, 'wjzpw.inventory.menFu'),  # 门幅
        'total_swing_number': fields.selection(_get_total_swing_number_options, 'wjzpw.inventory.touWen'),  # 总经数/头纹
        'axes_no': fields.selection(_get_axes_no_options, 'wjzpw.inventory.zhouHao'),  # 轴号
        'texture_axis_meter': fields.selection(_get_texture_axis_meter_options, 'wjzpw.inventory.changDu'),  # 长度
        'axes_number': fields.selection(_get_axes_number_options, 'wjzpw.inventory.bingZhouShu'),  # 并轴数
        'price_unit': fields.float('wjzpw.inventory.danJiaYuanMeiBing'),  # 单价元/并
        'price': fields.float('wjzpw.inventory.jinEr'),  # 金额
        'remark': fields.char('wjzpw.inventory.beiZhu')  # 备注
    }

    _defaults = {
        'input_date': datetime.today().strftime('%Y-%m-%d'),
    }

    _order = "input_date desc"

wjzpw_outside_warp_axes_input()
wjzpw_self_warp_axes_input()
wjzpw_outside_warp_axes_output()
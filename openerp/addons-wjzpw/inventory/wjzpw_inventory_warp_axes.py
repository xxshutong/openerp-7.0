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

wjzpw_outside_warp_axes_input()
wjzpw_self_warp_axes_input()
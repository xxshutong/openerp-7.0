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
from datetime import timedelta, datetime

import logging
from openerp.osv import fields, osv


_logger = logging.getLogger(__name__)


class wjzpw_produce_qian_jing(osv.osv):
    """
    牵经
    """
    _name = "wjzpw.produce.qian.jing"
    _description = "wjzpw.produce.qianJing"

    def onchange_flow_no(self, cr, uid, ids, flow_no=None, context={}):
        if not flow_no:
            return {}
        # Get existing company no
        query_sql = """
            SELECT *
            FROM wjzpw_organzine_output
            WHERE flow_no = %d
        """ % flow_no
        cr.execute(query_sql)
        organize_output_list = cr.dictfetchall()
        if organize_output_list:
            if len(organize_output_list) == 1:
                return {
                    'value': {
                        'process_unit': organize_output_list[0]['process_unit'],
                        'product_id': organize_output_list[0]['product_id'],
                        'material_specification': organize_output_list[0]['material_specification'],
                        'batch_no': organize_output_list[0]['batch_no'],
                        'material_area': organize_output_list[0]['material_area'],
                        'weight_avg': organize_output_list[0]['weight_avg'],
                    }
                }
            if len(organize_output_list) > 1:
                # TODO
                pass
        return {}

    def onchange_swing_number_or_axes_number(self, cr, uid, ids, wing_number=None, axes_number=None, context={}):
        """
        计算总经数
        """
        if wing_number and axes_number:
            return {
                'value': {
                    'total_swing_number': wing_number * axes_number
                }
            }
        return {}

    def onchange_material_specification(self, cr, uid, ids, material_specification=None, context={}):
        """
        计算原料分特
        """
        if material_specification:
            material_specification_obj = self.pool.get('wjzpw.material.specification').browse(cr, uid, material_specification, context=context)
            return {
                'value': {
                    'material_ft': self.convert_material_specification_to_ft(material_specification_obj.name)
                }
            }
        return {}

    def convert_material_specification_to_ft(self, material_specification):
        """
        由原料规格中提取出分特
        """
        material_specification_upper = material_specification.upper()
        if 'DT/' in material_specification_upper:
            material_specification_upper_temp = material_specification_upper[:material_specification_upper.index('DT/')]
            if material_specification_upper_temp.index(' ') >= 0:
                return int(material_specification_upper_temp[material_specification_upper_temp.rfind(' ') + 1:])
            else:
                return int(material_specification_upper_temp)
        return 0

    def _get_material_ft(self, cr, uid, ids, field_name, arg, context):
        """
        计算获得原料分特
        """
        res = {}
        for id in ids:
            res.setdefault(id, None)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.material_specification:
                ft = self.convert_material_specification_to_ft(rec.material_specification.name)
                if ft:
                    res[rec.id] = ft
        return res

    def _get_already_off_axis_number(self, cr, uid, ids, field_name, arg, context):
        """
        计算牵经已落轴数
        """
        res = {}
        for id in ids:
            res[id] = 0
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.flow_no:
                output_ids = self.pool.get('wjzpw.produce.qian.jing.output').search(cr, uid, [('flow_no', '=', rec.flow_no.id)])
                value = 0
                for output in self.pool.get('wjzpw.produce.qian.jing.output').browse(cr, uid, output_ids):
                    if output.off_axis_total_number:
                        value += output.off_axis_total_number
                res[rec.id] = value
        return res

    def _get_already_meter(self, cr, uid, ids, field_name, arg, context):
        """
        计算已签米数
        """
        res = {}
        for id in ids:
            res[id] = 0
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.flow_no:
                output_ids = self.pool.get('wjzpw.produce.qian.jing.output').search(cr, uid, [('flow_no', '=', rec.flow_no.id)])
                value = 0
                for output in self.pool.get('wjzpw.produce.qian.jing.output').browse(cr, uid, output_ids):
                    if output.off_axis_total_meter:
                        value += output.off_axis_total_meter
                res[rec.id] = value
        return res

    def _get_plan_end_time(self, cr, uid, ids, field_name, arg, context):
        """
        计算预计尽机时间
        """
        res = {}
        for id in ids:
            res.setdefault(id, None)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.start_time and rec.plan_meter and rec.speed and rec.efficiency:
                hours = int(rec.plan_meter / (rec.speed * 60 * rec.efficiency))
                if hours:
                    # 获取datetime format配置
                    pool_lang = self.pool.get('res.lang')
                    lang_ids = pool_lang.search(cr, uid, [('code', '=', context['lang'])])[0]
                    lang_obj = pool_lang.browse(cr,uid,lang_ids)
                    datetime_format = lang_obj.date_format + " " + lang_obj.time_format
                    res[rec.id] = (datetime.strptime(rec.start_time, datetime_format) + timedelta(hours=hours)).strftime(datetime_format)
        return res

    def _get_plan_meter(self, cr, uid, ids, field_name, arg, context):
        """
        计算预牵米数
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.weight_avg and rec.material_specification and rec.material_ft:
                res[rec.id] = rec.weight_avg / rec.material_ft * 1000 * 10000
        return res

    def _get_single_silk_length(self, cr, uid, ids, field_name, arg, context):
        """
        计算单丝长度
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.weight_avg and rec.material_specification and rec.material_ft:
                res[rec.id] = rec.weight_avg / rec.material_ft * 1000
        return res

    def _get_total_swing_number(self, cr, uid, ids, field_name, arg, context):
        """
        计算总经数
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.swing_number and rec.axes_number:
                res[rec.id] = rec.swing_number * rec.axes_number
        return res

    _columns = {
        'create_date': fields.datetime('wjzpw.produce.chuangJianRiQi', readonly=True),  # 数据创建日期
        'machine_no': fields.selection((('1', '1'), ('2', '2')), 'wjzpw.produce.jiHao'),  # 机号
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.produce.liuChengBianHao', required=True),  # 流程编号
        'process_unit': fields.char('wjzpw.produce.jiaGongDanWei'),  # 加工单位
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.produce.pinMing', required=True),  # 品名
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.produce.piHao', required=True),  # 批号
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.produce.yuanLiaoChanDi', required=True),  # 原料产地
        'weight_avg': fields.float('wjzpw.produce.tongZiJingZhong'),  # 筒子净重
        # 'material_ft': fields.char('wjzpw.produce.yuanLiaoFenTe'),  # 原料分特
        # 'plan_meter': fields.integer('wjzpw.produce.yuQianMiShu'),  # 预牵米数
        'swing_number': fields.integer('wjzpw.produce.baiJingShu'),  # 摆经数
        'axes_number': fields.integer('wjzpw.produce.bingZhouShu'),  # 并轴数
        'total_length': fields.float('wjzpw.produce.sheDingZongChang'),  # 设定总长
        'speed': fields.integer('wjzpw.produce.cheSu'),  # 车速
        'off_axis_number': fields.integer('wjzpw.produce.qianJingLuoZhouShu'),  # 牵经落轴数
        'start_time': fields.datetime('wjzpw.produce.qiJiShiJian'),  # 起机时间
        'efficiency': fields.float('wjzpw.produce.xiaoLv'),  # 效率
        'status': fields.selection((('unfinished', 'wjzpw.produce.shengChanZhong'), ('finished', 'wjzpw.produce.yiWanCheng')), 'wjzpw.produce.zhuangTai'),  # 状态，是否完成

        # Function fields
        'material_ft': fields.function(_get_material_ft, string='wjzpw.produce.yuanLiaoFenTe', type='integer', method=True),  # 原料分特
        'already_off_axis_number': fields.function(_get_already_off_axis_number, string='wjzpw.produce.qianJingYiLuoZhou', type='integer', method=True),  # 牵经已落轴
        'plan_meter': fields.function(_get_plan_meter, string='wjzpw.produce.yuQianMiShu', type='float', method=True),  # 预牵米数
        'already_meter': fields.function(_get_already_meter, string='wjzpw.produce.yiQianMiShu', type='integer', method=True),  # 已牵米数
        'plan_end_date': fields.function(_get_plan_end_time, string='wjzpw.produce.yuJiJinJiShiJian', type='char', method=True),  # 预计尽机时间
        'total_swing_number': fields.function(_get_total_swing_number, string='wjzpw.produce.zongJingShu', type='integer', method=True),  # 计算总经数
        'single_silk_length': fields.function(_get_single_silk_length, string='wjzpw.produce.dangSiChangDuWanMi', type='float', method=True),  # 计算单丝长度
    }

    _defaults = {
        # 'order_no': _default_order_no,
        # 'no': _default_no,
        # 'dead_line_unit': u'天',
        'status': 'unfinished'
    }

    _order = "create_date desc"


class wjzpw_produce_qian_jing_output(osv.osv):
    """
    牵经工人产量
    """
    _name = "wjzpw.produce.qian.jing.output"
    _description = "wjzpw.produce.qianJingGongRenChanLiang"

    def onchange_flow_no(self, cr, uid, ids, flow_no=None, context={}):
        if not flow_no:
            return {}
        # Get existing company no
        query_sql = """
            SELECT process_unit, product_id
            FROM wjzpw_produce_qian_jing
            WHERE flow_no = %d
        """ % flow_no
        cr.execute(query_sql)
        wjzpw_produce_qian_jing = cr.dictfetchall()
        if wjzpw_produce_qian_jing and len(wjzpw_produce_qian_jing) >= 1:
            return {
                'value': {
                    'process_unit': wjzpw_produce_qian_jing[0]['process_unit'],
                    'product_id': wjzpw_produce_qian_jing[0]['product_id'],
                }
            }
        return {}

    def _get_speed(self, cr, uid, ids, field_name, arg, context):
        """
        获取车速
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.flow_no:
                query_sql = """
                    SELECT speed
                    FROM wjzpw_produce_qian_jing
                    WHERE flow_no = %d
                """ % rec.flow_no
                cr.execute(query_sql)
                wjzpw_produce_qian_jing = cr.dictfetchall()
                if wjzpw_produce_qian_jing and len(wjzpw_produce_qian_jing) >= 1:
                    res[rec.id] = wjzpw_produce_qian_jing[0]['speed']
        return res

    def _get_total_meter(self, cr, uid, ids, field_name, arg, context):
        """
        计算牵经落轴米数
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for id in ids:
            query_sql = """
                SELECT sum(off_axis_meter) as sum
                FROM wjzpw_produce_qian_jing_output_record
                WHERE wjzpw_produce_qian_jing_output = %d
            """ % id
            cr.execute(query_sql)
            result = cr.dictfetchone()
            if result and result['sum']:
                res[id] = result['sum']
        return res

    def _get_total_number(self, cr, uid, ids, field_name, arg, context):
        """
        计算牵经落轴数
        """
        res = {}
        for id in ids:
            res.setdefault(id, 0)
        for id in ids:
            query_sql = """
                SELECT sum(off_axis_number) as sum
                FROM wjzpw_produce_qian_jing_output_record
                WHERE wjzpw_produce_qian_jing_output = %d
            """ % id
            cr.execute(query_sql)
            result = cr.dictfetchone()
            if result and result['sum']:
                res[id] = result['sum']
        return res

    _columns = {
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.produce.liuChengBianHao', required=True),  # 流程编号
        'process_unit': fields.char('wjzpw.produce.jiaGongDanWei', required=True),  # 加工单位
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.produce.pinMing', required=True),  # 品名
        'input_date': fields.date('wjzpw.produce.riQi', required=True),  # 日期
        'class_type': fields.selection((('A', 'wjzpw.produce.jiaBan'), ('B', 'wjzpw.produce.yiBan'), ('C', 'wjzpw.produce.bingBan')), 'wjzpw.produce.banBie'),  # 班别
        'employee': fields.char('wjzpw.produce.xingMing'),  # 姓名
        'machine_no': fields.selection((('1', '1'), ('2', '2')), 'wjzpw.produce.jiHao'),  # 机号
        'records': fields.one2many('wjzpw.produce.qian.jing.output.record', 'wjzpw_produce_qian_jing_output', 'wjzpw.produce.chanLiangJiLu', readonly=False),
        'remark': fields.char('wjzpw.produce.beiZhu'),  # 备注

        # functions
        'speed': fields.function(_get_speed, string='wjzpw.produce.cheSuZhuanMeiFen', type='integer', method=True),  # 总只数
        'off_axis_total_meter': fields.function(_get_total_meter, string='wjzpw.produce.luoZhouMiShu', type='integer', method=True),  # 落轴米数
        'off_axis_total_number': fields.function(_get_total_number, string='wjzpw.produce.luoZhouGeShu', type='integer', method=True)  # 落轴个数
    }

    _defaults = {
        'input_date': datetime.today().strftime('%Y-%m-%d')
    }

    _order = "input_date desc"


class wjzpw_produce_qian_jing_output_record(osv.osv):
    """
    牵经工人产量记录
    """
    _name = "wjzpw.produce.qian.jing.output.record"
    _description = "wjzpw.produce.qianJingGongRenChanLiangJiLu"

    _columns = {
        'create_date': fields.datetime('wjzpw.produce.chuangJianRiQi', readonly=True),  # 数据创建日期
        'wjzpw_produce_qian_jing_output': fields.many2one('wjzpw.produce.qian.jing.output', 'wjzpw.produce.qianJingGongRenChanLiang', required=True),  # 流程编号
        'off_axis_number': fields.integer('wjzpw.produce.qianJingLuoZhouGeShu', required=True),  # 牵经落轴个数
        'off_axis_meter': fields.integer('wjzpw.produce.qianJingLuoZhouMiShu', required=True),  # 牵经落轴米数
        'remark': fields.char('wjzpw.produce.beiZhu')  # 备注
    }

    _defaults = {
        'off_axis_number': 0
    }

    _order = "create_date"


wjzpw_produce_qian_jing()
wjzpw_produce_qian_jing_output()
wjzpw_produce_qian_jing_output_record()

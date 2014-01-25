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



class wjzpw_produce_qian_jing(osv.osv):
    """
    牵经
    """
    _name = "wjzpw.produce.qian.jing"
    _description = "wjzpw.produce.qianJing"

    # def _default_order_no(self, cr, uid, context=None):
    #     default_no = self._default_no(cr, uid, context=context)
    #     return  '%s%04d' % (self._order_prefix, default_no)
    #
    # def _default_no(self, cr, uid, context=None):
    #     query_sql = """
    #         SELECT max(no)
    #         FROM wjzpw_order
    #         """
    #     cr.execute(query_sql)
    #     order = cr.dictfetchone()['max']
    #     if not order:
    #         return 1
    #     else:
    #         return order + 1
    #
    # def onchange_customer(self, cr, uid, ids, customer=None, context={}):
    #     if not customer:
    #         return {}
    #     # Get existing company no
    #     query_sql = """
    #         SELECT count(company_no) AS num, company_no
    #         FROM wjzpw_order
    #         WHERE customer = %d GROUP BY company_no order by num desc limit 1
    #     """ % customer
    #     cr.execute(query_sql)
    #     company_no_result = cr.dictfetchone()
    #     company_no_value = ''
    #     if company_no_result:
    #         company_no_value = company_no_result['company_no']
    #     return {
    #         'domain': {
    #             'customer_product': [('customer', '=', customer)]
    #         },
    #         'value': {
    #             'company_no': company_no_value
    #         }
    #     }
    #
    # def _company_no_product(self, cr, uid, ids, field_name, arg, context):
    #     """
    #     公司编号及品名
    #     """
    #     res = {}
    #     for id in ids:
    #         res.setdefault(id, u'无')
    #     for rec in self.browse(cr, uid, ids, context=context):
    #         company_no_product = ''
    #         if rec.company_no:
    #             company_no_product += rec.company_no
    #         if rec.product_id:
    #             company_no_product += rec.product_id['name']
    #         res[rec.id] = company_no_product
    #     return res
    #
    def _get_already_off_axis_number(self, cr, uid, ids, field_name, arg, context):
        """
        计算牵经已落轴数
        """
        # TODO 需要等获取人工数据后计算得到
        res = {}
        for id in ids:
            res['id'] = 0
        return res

    def _get_already_meter(self, cr, uid, ids, field_name, arg, context):
        """
        计算已签米数
        """
        # TODO 需要等获取人工数据后计算得到
        res = {}
        for id in ids:
            res['id'] = 0
        return res

    def _get_plan_end_date(self, cr, uid, ids, field_name, arg, context):
        """
        计算预计尽机时间
        """
        # TODO 计算获得预计尽机时间
        res = {}
        for id in ids:
            res['id'] = 'TODO'
        return res

    def _get_plan_meter(self, cr, uid, ids, field_name, arg, context):
        """
        计算预牵米数
        """
        # TODO 计算预牵米数
        res = {}
        for id in ids:
            res['id'] = 'TODO'
        return res

    def _get_total_swing_number(self, cr, uid, ids, field_name, arg, context):
        """
        计算总经数
        """
        # TODO 计算总经数
        res = {}
        for id in ids:
            res['id'] = 0
        return res

    #
    # def _order_type(self, cr, uid, ids, field_name, arg, context):
    #     """
    #     订单类型，新品或者翻单
    #     """
    #     res = {}
    #     for id in ids:
    #         res.setdefault(id, u'新品')
    #     for rec in self.browse(cr, uid, ids, context=context):
    #         if rec.product_id and rec.input_date:
    #             query_sql = """
    #                 SELECT id
    #                 FROM wjzpw_order
    #                 WHERE product_id = %d AND input_date < '%s'
    #                 """ % (rec.product_id, rec.input_date)
    #             cr.execute(query_sql)
    #             existing_order = cr.dictfetchone()
    #             if existing_order:
    #                 res[rec.id] = u'翻单'
    #             else:
    #                 res[rec.id] = u'新品'
    #     return res
    #
    # def write(self, cr, user, ids, vals, context=None):
    #     result = super(wjzpw_order, self).write(cr, user, ids, vals, context=context)
    #     # TODO
    #     # Generate order plan if new status is 'processing'
    #     for id in ids:
    #         if vals.get('status') and vals.get('status') == 'processing':
    #             new_vals = {}
    #             new_vals['order_id'] = id
    #             # 检查是否已经有做过这个品名,有则把数据复制过来
    #             updated_order = self.browse(cr, user, id, context=None)
    #             query_sql = """
    #                 SELECT *
    #                 FROM wjzpw_order_plan
    #                 WHERE order_id in (SELECT id FROM wjzpw_order WHERE product_id = %d) ORDER BY create_date desc LIMIT 1
    #             """ % updated_order.product_id.id
    #             cr.execute(query_sql)
    #             existing_order_plan = cr.dictfetchone()
    #             if existing_order_plan:
    #                 new_vals = existing_order_plan.copy()
    #                 new_vals['create_date'] = None
    #                 new_vals['create_uid'] = None
    #                 new_vals['write_date'] = None
    #                 new_vals['write_uid'] = None
    #                 new_vals['order_id'] = id
    #                 new_vals['dead_line'] = None
    #                 new_vals['machine_assign'] = None
    #                 new_vals['texture_axis'] = None
    #                 new_vals['texture_axis_number'] = None
    #             # 创建一个新的生产工艺及计划安排
    #             wjzpw_order_plan_obj = self.pool.get('wjzpw.order.plan')
    #             wjzpw_order_plan_obj.create(cr, user, new_vals, context=None)
    #     return result
    #
    # def _name_get(self, cr, uid, ids, field_name, arg, context):
    #     res = {}
    #     for rec in self.browse(cr, uid, ids, context=context):
    #         res[rec.id] = rec.order_no
    #     return res

    _columns = {
        'create_date': fields.datetime('wjzpw.produce.chuangJianRiQi', readonly=True),  # 数据创建日期
        'machine_no': fields.char('wjzpw.produce.jiHao'),  # 机号
        'flow_no': fields.many2one('wjzpw.flow.no', 'wjzpw.produce.liuChengBianHao', required=True),  # 流程编号
        'process_unit': fields.char('wjzpw.produce.jiaGongDanWei'),  # 加工单位
        'product_id': fields.many2one('wjzpw.product', 'wjzpw.produce.pinMing', required=True),  # 品名
        'material_specification': fields.many2one('wjzpw.material.specification', 'wjzpw.inventory.yuanLiaoGuiGe', required=True),  # 原料规格
        'batch_no': fields.many2one('wjzpw.organzine.batch.no', 'wjzpw.produce.piHao', required=True),  # 批号
        'material_area': fields.many2one('wjzpw.material.area', 'wjzpw.produce.yuanLiaoChanDi', required=True),  # 原料产地
        'weight_avg': fields.float('wjzpw.produce.tongZiJingZhong'),  # 筒子净重
        'material_ft': fields.char('wjzpw.produce.yuanLiaoFenTe'),  # 原料分特
        # 'plan_meter': fields.integer('wjzpw.produce.yuQianMiShu'),  # 预牵米数
        'swing_number': fields.integer('wjzpw.produce.baiJingShu'),  # 摆经数
        'axes_number': fields.integer('wjzpw.produce.bingZhouShu'),  # 并轴数
        'total_length': fields.float('wjzpw.produce.sheDingZongChang'),  # 设定总长
        'speed': fields.integer('wjzpw.produce.cheSu'),  # 车速
        'off_axis_number': fields.integer('wjzpw.produce.qianJingLuoZhouShu'),  # 牵经落轴数
        'start_date': fields.date('wjzpw.produce.qiJiShiJian'),  # 起机时间
        'efficiency': fields.float('wjzpw.produce.xiaoLv'),  # 效率
        'status': fields.selection((('unfinished', 'wjzpw.produce.shengChanZhong'), ('finished', 'wjzpw.produce.yiWanCheng')), 'wjzpw.produce.zhuangTai'),  # 状态，是否完成

        # Function fields
        'already_off_axis_number': fields.function(_get_already_off_axis_number, string='wjzpw.produce.qianJingYiLuoZhou', type='integer', method=True),  # 牵经已落轴
        'plan_meter': fields.function(_get_plan_meter, string='wjzpw.produce.yuQianMiShu', type='integer', method=True),  # 预牵米数
        'already_meter': fields.function(_get_already_meter, string='wjzpw.produce.yiQianMiShu', type='integer', method=True),  # 已牵米数
        'plan_end_date': fields.function(_get_plan_end_date, string='wjzpw.produce.yuJiJinJiShiJian', type='char', method=True),  # 预计尽机时间
        'total_swing_number': fields.function(_get_total_swing_number, string='wjzpw.produce.zongJingShu', type='integer', method=True)  # 计算总经数

        # 'dead_line_str': fields.function(_dead_line_str, string='wjzpw.order.jiaoHuoQi', type='char', method=True),  # 交货期
        # 'order_type': fields.function(_order_type, string='wjzpw.order.xinPinHuoFanDan', type='char', method=True),  # 新品或翻单
        # 'name': fields.function(_name_get, string="wjzpw.inventory.dingDanMing", type='char', method=True)
    }

    _defaults = {
        # 'order_no': _default_order_no,
        # 'no': _default_no,
        # 'dead_line_unit': u'天',
        'status': 'unfinished'
    }

    _order = "create_date desc"


wjzpw_produce_qian_jing()

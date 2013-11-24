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


class wjzpw_product(osv.osv):
    _name = "wjzpw.product"
    _description = "Product Management"

    _columns = {
        'name': fields.char('Product Name', size=64, required=True),
        'description': fields.text('Description')
    }
    _defaults = {
    }
    _order = "name"

class wjzpw_batch_no(osv.osv):
    _name = "wjzpw.batch.no"
    _description = "Batch No Management"

    _columns = {
        'name': fields.char('Batch No', size=64, required=True),
        'description': fields.text('Description')
    }
    _defaults = {
    }
    _order = "name"

wjzpw_product()
wjzpw_batch_no()

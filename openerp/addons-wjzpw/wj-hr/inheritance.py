from openerp.osv import osv, fields


class sale_order_test(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    _columns = {'test': fields.date('Test'),
                'testing': fields.text('Testing'),
    }
{
    'name': "Wj-zpw.com 纺织织造订单管理",
    'description': "对订单进行入库、执行等管理",
    'version': "1.0",
    'author': "xxshutong@gmail.com",
    'website': "http://www.wj-zpw.com",
    'category': "Textile",
    'sequence': 3,
    'depends': ['wjzpw', 'hr'],
    'css': [
        'static/src/css/show.css'
    ],
    'data': [
        'wjzpw_order_view.xml',
        # 'wjzpw_data.xml',
        # 'report/module_report.xml',
        # 'wizard/module_wizard.xml',
    ],
    'test': [

    ],
    'demo': [
        # 'wjzpw_demo.xml'
    ],
    'installable': True,
    'auto_install': False

}
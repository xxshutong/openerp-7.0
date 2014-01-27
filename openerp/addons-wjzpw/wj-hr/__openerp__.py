{
    'name': "Wj-zpw.com 人力资源管理",
    'description': "人力资源管理",
    'version': "1.1",
    'author': "xxshutong@gmail.com",
    'website': "http://www.wj-zpw.com",
    'category': "Human Resource",
    'sequence': 5,
    'depends': ['hr'],
    'init_xml': [],
    'update_xml' : ['hr_inherit_view.xml'],
    'css': [
        'static/src/css/show.css'
    ],
    'data': [
        # 'wjzpw_order_view.xml',
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
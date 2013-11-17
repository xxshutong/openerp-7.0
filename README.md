## 初始化安装
### 依赖：
* Postgresql

### 步骤
* 创建数据库用户openerp，密码openerp
* 安装依赖包
> sudo apt-get install graphviz ghostscript postgresql-client python-dateutil python-feedparser python-gdata python-ldap python-libxslt1 python-lxml python-mako python-openid python-psycopg2 python-pybabel python-pychart python-pydot python-pyparsing python-reportlab python-simplejson python-tz python-vatnumber python-vobject python-webdav python-werkzeug python-xlwt python-yaml python-imaging python-matplotlib
* [可选] 更新服务器端配置信息
> vi ~/.openerp_serverrc
* 通过命令运行服务器
> ./openerp-server
* 访问注册页面下方的Manage Databases进行数据库管理
> **注:** 1. master password是管理数据库的主密码,在(~/.openerp_serverrc)中进行配置，默认为admin.
>  2. 默认创建的管理员账号为admin,密码为admin








**Reference:** http://www.theopensourcerer.com/2012/12/how-to-install-openerp-7-0-on-ubuntu-12-04-lts/

## 升级系统需要注意的点：

### 1. 文件
* README.md
* .gitignore

### 2. 目录



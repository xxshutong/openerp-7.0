## 初始化安装
### 依赖：
* Postgresql

### 步骤
* 创建数据库用户openerp，密码openerp

* 创建虚拟环境
> pip install virtualenv
>

* 安装依赖包
> sudo pip install python-dateutil docutils feedparser mock unittest2 gdata python-ldap lxml mako python-openid psycopg2 Babel reportlab simplejson pytz vatnumber vobject python_webdav Werkzeug pyparsing==1.5.7 pydot PyYAML xlwt ZSI PIL

* 安装pychart和libxslt1, 参考Reference

* [可选] 更新服务器端配置信息
> vi ~/.openerp_serverrc

* 通过命令运行服务器
> ./openerp-server

* 访问注册页面下方的Manage Databases进行数据库管理
> **注:** 1. master password是管理数据库的主密码,在(~/.openerp_serverrc)中进行配置，默认为admin.
>  2. 默认创建的管理员账号为admin,密码为admin

* 创建数据库之后记得创建一个开发账户，并赋予此账户_**技术特性**_. 没有此特性会对后续开发产生较大局限性，如无法发现和安装自定义模块


**Reference:** http://www.theopensourcerer.com/2012/12/how-to-install-openerp-7-0-on-ubuntu-12-04-lts/
http://code.zoia.org/2013/05/09/setting-up-openerp7-on-osx-using-virtualenv

## 升级系统需要注意的点：

### 1. 文件
* README.md
* .gitignore

### 2. 目录
* openerp/addons-wjzpw



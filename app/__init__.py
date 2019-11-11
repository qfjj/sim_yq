from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os

app = Flask(__name__)  # 创建Flask对象

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/sim_yq"  # 定义Mysql数据库连接
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号
app.config['SECRET_KEY'] = '6a8312d499ed42828bb85fefac3607b7'  # CSRF保护设置密钥

app.config['PAGE_SET'] = 10  # 分页上限数量
app.config['AUTH_SWITCH'] = False  # 页面访问权限开关，True为开启
app.debug = False  # 调试开关

db = SQLAlchemy(app)  # 创建db对象

from app.home import home as home_blueprint

# 注册蓝图
app.register_blueprint(home_blueprint)


# 定义404页面视图
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template("home/404.html"), 404
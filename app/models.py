from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码

    def __repr__(self):
        return "<User %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)  # 验证密码是否正确，返回True和False

# 登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员编号
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<Userlog %r>" % self.id

# 监控任务设置
class Settingtask(db.Model):
    __tablename__ = "settingtask"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    taskname = db.Column(db.String(10))    # 方案名
    keyname = db.Column(db.String(10))      # 关键词名

# 数据表
class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)   # 内容
    source = db.Column(db.String(255))      # 来源
    created_at =  db.Column(db.DateTime)   # 时间
    screen_name = db.Column(db.String(255))   # 用户名称
    html = db.Column(db.Text)   # 来源网址
    mg = db.Column(db.String(255))      # 敏感标记

# # 数据表
# class Data(db.Model):
#     __tablename__ = "data"
#     id = db.Column(db.Integer, primary_key=True)  # 编号
#     content = db.Column(db.String(255))   # 内容
#     source = db.Column(db.String(255))      # 来源
#     created_at =  db.Column(db.DateTime)   # 时间
#     screen_name = db.Column(db.String(255))   # 用户名称

# 日期表
class datetime(db.Model):
    __tablename__ = "datetime"
    date = db.Column(db.DateTime, primary_key=True)

# 建表
# db.create_all()
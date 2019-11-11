from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, ValidationError
from app.models import User
from flask import session

class LoginForm(FlaskForm):
    """会员登录表单"""
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            "autofocus": ""
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block"
        }
    )

    # 账号验证
    def validate_name(self, field):
        name = field.data
        if User.query.filter_by(name=name).count() == 0:
            raise ValidationError("账号不存在！")

class SettingTask(FlaskForm):
    taskname = StringField(
        validators=[
            DataRequired("请填写方案名，不超过10个字")
        ],
        description="方案名",
        render_kw={
            "placeholder": "请填写方案名！",
            "class": "form-control",
            "autofocus": ""
        }
    )
    keyname = StringField(
        validators=[
            DataRequired("请填写关键词，不超过10个字")
        ],
        description="关键词",
        render_kw={
            "placeholder": "请填写关键词！",
            "class": "form-control",
            "autofocus": ""
        }
    )
    submit = SubmitField(
        '保存',
        render_kw={
            "class": "btn btn-warning btn-w saveBtn"
        }
    )

class radio(FlaskForm):
    all = BooleanField(
        label="全部",
    )
    all = BooleanField(
        label="微博",
    )
    all = BooleanField(
        label="微信",
    )
    all = BooleanField(
        label="论坛",
    )
    all = BooleanField(
        label="新闻",
    )
    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-warning btn-w saveBtn"
        }
    )
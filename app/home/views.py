from app import db, app
from app.home import home
from app.forms import LoginForm, SettingTask
from app.models import User, Userlog, Settingtask, Data
from flask import render_template, redirect, url_for, flash, session, request, abort, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime
import json
import pandas as pd

timeb = '30'

@home.route("/")
def index():
    user = session.get("user")
    data = {"user_info": user if user else None}
    return render_template("auth/index.html", data = data)

# 定义登录判断装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # session不存在时请求登录
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# 定义登录视图
@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()  # 导入登录表单
    if form.validate_on_submit():  # 验证是否有提交表单
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if not user.pwd == data["pwd"]:
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user"] = data["name"]
        session["user_id"] = user.id
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.user"))
    return render_template("auth/login.html", form=form)

# 定义登出视图
@home.route("/logout/")
@user_login_req
def logout():
    session.pop("user")
    session.pop("user_id")
    return redirect(url_for("home.index"))

# 定义会员中心视图
@home.route("/user/", methods=["GET", "POST"])
@user_login_req
def user():
    username = session["user"]
    taskname = (Settingtask.query.get(int(session["user_id"]))).taskname
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    time = request.args.get("time", '')
    order = request.args.get("order", '')
    type = request.args.get("type", '')

    PER_PAGE = 10
    total = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) < 1000).filter(
        Data.content.like("%" + keyname + "%")).count()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    pagination = Pagination(bs_version=4, page=page, total=total)

    news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= 1000).filter(
        Data.content.like("%" + keyname + "%")).order_by(Data.created_at.desc()).slice(start, end)

    # if not time and not order or order == 'desc' and not type or type == 'all':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= 30).filter(
    #     Data.content.like("%" + keyname + "%")).order_by(Data.created_at.desc()).slice(start, end)
    # elif not order and not type:
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).order_by(Data.created_at.desc()).slice(start, end)
    # elif order == 'asc' and not time and not type:
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= 7).filter(
    #     Data.content.like("%" + keyname + "%")).order_by(Data.created_at.asc()).slice(start, end)
    # elif order == 'desc' or not order and not type or type == 'all':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).order_by(Data.created_at.asc()).slice(start, end)
    # elif order == 'asc' and not type or type == 'all':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).order_by(Data.created_at.asc()).slice(start, end)
    # elif order == 'asc' and type == 'mg':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).filter(Data.mg == '敏感').order_by(Data.created_at.asc()).slice(start, end)
    # elif order == 'asc' and type == 'nomg':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).filter(Data.mg == None).order_by(Data.created_at.asc()).slice(start, end)
    # elif not order or order == 'desc' and type == 'mg':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).filter(Data.mg == '敏感').order_by(Data.created_at.desc()).slice(start, end)
    # elif not time and not order or order == 'desc' and type == 'mg':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= 7).filter(
    #     Data.content.like("%" + keyname + "%")).filter(Data.mg == '敏感').order_by(Data.created_at.desc()).slice(start, end)
    # elif not time and not order or order == 'desc' and type == 'nomg':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= 7).filter(
    #     Data.content.like("%" + keyname + "%")).filter(Data.mg == None).order_by(Data.created_at.desc()).slice(start, end)
    # elif not order or order == 'desc' and type == 'nomg':
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= time).filter(
    #     Data.content.like("%" + keyname + "%")).filter(Data.mg == None).order_by(Data.created_at.desc()).slice(start, end)
    # else:
    #     news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) <= 30).filter(
    #     Data.content.like("%" + keyname + "%")).order_by(Data.created_at.desc()).slice(start, end)

    p = dict(
        time = time,
        order = order,
        type = type
    )

    context = {
        'pagination': pagination,
        'news': news
    }

    return render_template("user/home.html", username=username, taskname=taskname, keyname=keyname, p=p, **context)

# 定义信息详情视图
@home.route("/content/", methods=["GET", "POST"])
@user_login_req
def content():
    username = session["user"]
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    post_id = request.args.get("post_id", '')

    cont =Data.query.filter(Data.id == post_id).first_or_404()

    return render_template('user/content.html', username=username, keyname=keyname, cont=cont)

# 定义设置视图
@home.route("/setting/", methods=["GET", "POST"])
@user_login_req
def setting():
    username = session["user"]
    setting = SettingTask()
    user_setting = Settingtask.query.get(int(session["user_id"]))
    if request.method == "GET":
        setting.taskname.data == user_setting.taskname
        setting.keyname.data == user_setting.keyname

    if setting.validate_on_submit():
        data = setting.data
        user_setting.taskname = data["taskname"]
        user_setting.keyname = data["keyname"]
        db.session.add(user_setting)
        db.session.commit()
        flash("修改成功！", "ok")

    return render_template("user/setting.html", username=username, setting=setting)

# 定义图表视图
@home.route("/chart/", methods=["GET", "POST"])
@user_login_req
def charts():
    taskname = (Settingtask.query.get(int(session["user_id"]))).taskname
    count_all = "select count(*) from data"
    count_all = db.session.execute(count_all)
    count_all = count_all.fetchall()
    count_all = count_all[0][0]

    username = session["user"]
    return render_template("user/charts.html", username=username, taskname=taskname, count_all=count_all)

# 数据大屏视图
@home.route("/bigdata/", methods=["GET", "POST"])
@user_login_req
def bigdata():
    taskname = (Settingtask.query.get(int(session["user_id"]))).taskname
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    username = session["user"]
    news = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) < 200).filter(
        Data.content.like("%" + keyname + "%")).all()

    news_mg = Data.query.filter(db.cast(datetime.now(), db.DATE) - db.cast(Data.created_at, db.DATE) < 200).filter(Data.mg == '敏感').filter(
        Data.content.like("%" + keyname + "%")).all()


    return render_template("user/bigdata-2.html", taskname=taskname, username=username,news=news, news_mg=news_mg)

# 热门账号柱状图Ajax请求
@home.route("/bigdata/houtzh/", methods=["GET", "POST"])
@user_login_req
def hotzh():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    hotzh = "select screen_name,count(*) a from `data` where content like '"+ "%" + keyname + "%" +"' and source <> '贴吧' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +" group by screen_name ORDER BY a desc limit 5"
    hotzh = db.session.execute(hotzh)
    hotzh = hotzh.fetchall()
    jsonData = {}
    jsonData['legendData'] = [i[0] for i in hotzh]
    jsonData['datas'] = [i[1] for i in hotzh]

    return jsonData

# 定义信息数量模块Ajax请求
@home.route("/chart/countall/", methods=["GET", "POST"])
@user_login_req
def chart_countall():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    count_all = "select count(*) from data where content like '"+ "%" + keyname + "%" +"' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +";"
    count_all = db.session.execute(count_all)
    count_all = count_all.fetchall()
    jsonData = {}
    jsonData['num'] = count_all[0][0]
    return jsonData

# 定义敏感信息数量Ajax请求
@home.route("/chart/countmg/", methods=["GET", "POST"])
@user_login_req
def chart_bie_countall():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    count_mg = "select count(distinct a.content) from `data` a where a.mg = '敏感' and a.content like '"+ "%" + keyname + "%" +"' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +" ;"
    count_mg = db.session.execute(count_mg)
    count_mg = count_mg.fetchall()
    jsonData = chart_countall()
    jsonData['nummg'] = count_mg[0][0]
    per = format(jsonData['nummg'] / jsonData['num'],'.4f')
    per = format((float(per) * 100),'.2f' )
    jsonData['per'] = per
    jsonData['num_2'] = format(jsonData['num'])
    jsonData['nummg_2'] = format(jsonData['nummg'])

    return jsonData

# 定义信息走势图Ajax请求
@home.route("/chart/line/", methods=["GET", "POST"])
@user_login_req
def chart_line():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    qb_sql = "select DATE_FORMAT(datetime.date,'%m-%d'), IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where content like '"+ "%" + keyname + "%" +"' GROUP BY date_format(created_at,'%Y-%m-%d')) " \
             "t1 ON  date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    qb_sql = db.session.execute(qb_sql)
    qb_rows = qb_sql.fetchall()

    wb_sql = "select datetime.date, IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where source = '微博' and content like '"+ "%" + keyname + "%" +"' GROUP BY date_format(created_at,'%Y-%m-%d')) " \
             "t1 ON date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    wb_sql = db.session.execute(wb_sql)
    wb_rows = wb_sql.fetchall()

    tb_sql = "select datetime.date, IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where source = '贴吧' and content like '"+ "%" + keyname + "%" +"' GROUP BY date_format(created_at,'%Y-%m-%d')) " \
             "t1 ON date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    tb_sql = db.session.execute(tb_sql)
    tb_rows = tb_sql.fetchall()

    wx_sql = "select datetime.date, IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where source = '微信' and content like '" + "%" + keyname + "%" + "' GROUP BY date_format(created_at,'%Y-%m-%d')) " \
             "t1 ON date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    wx_sql = db.session.execute(wx_sql)
    wx_rows = wx_sql.fetchall()

    sh_sql = "select datetime.date, IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where source = '搜狐新闻' and content like '" + "%" + keyname + "%" + "' GROUP BY date_format(created_at,'%Y-%m-%d')) " \
             "t1 ON date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    sh_sql = db.session.execute(sh_sql)
    sh_rows = sh_sql.fetchall()

    rm_sql = "select datetime.date, IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where source = '人民网' and content like '" + "%" + keyname + "%" + "' GROUP BY date_format(created_at,'%Y-%m-%d')) " \
            "t1 ON date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    rm_sql = db.session.execute(rm_sql)
    rm_rows = rm_sql.fetchall()

    yAxisData = [[],[],[],[],[],[]]
    yAxisData[0].append([x[1] for x in qb_rows])
    yAxisData[1].append([x[1] for x in wb_rows])
    yAxisData[2].append([x[1] for x in tb_rows])
    yAxisData[3].append([x[1] for x in wx_rows])
    yAxisData[4].append([x[1] for x in sh_rows])
    yAxisData[5].append([x[1] for x in rm_rows])


    legendData = ['全部', '微博', '贴吧', '微信', '搜狐新闻', '人民网']
    xAxisData = [x[0] for x in qb_rows]
    # yAxisData = [[x[1] for x in qb_rows] + [x[1] for x in wb_rows] + [x[1] for x in tb_rows]]
    fromTime = qb_rows[0][0]
    toTime = qb_rows[-1][0]

    jsonData = {}
    jsonData['legendData'] = legendData
    jsonData['xAxisData'] = xAxisData
    jsonData['yAxisData'] = yAxisData
    jsonData['fromTime'] = fromTime
    jsonData['toTime'] = toTime

    return jsonData

# 定义“周-时”信息发布规律图Ajax请求
@home.route("/chart/heatmap/", methods=["GET", "POST"])
@user_login_req
def chart_heatmap():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    day = []
    num = []

    for i in range(24):
        count_all = "select date_format(datetime.date,'%Y-%m-%d'), IFNULL(b,0)  from datetime LEFT JOIN (select  date_format(t2.created_at,'%Y-%m-%d') a,SUM(t2.x) b from (select  t1.created_at, IFNULL(t1.count1, 0) x from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where content like '" + "%" + keyname + "%" + "' GROUP BY created_at) t1 ON  date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= 7 and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by t1.created_at) t2 where date_format(t2.created_at,'%H') < " + str(
            i + 1) + " GROUP BY date_format(t2.created_at,'%Y-%m-%d')) t3 on date_format(datetime.date,'%Y-%m-%d')  = date_format(t3.a,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= 7 and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 ORDER BY date"
        count_all = db.session.execute(count_all)
        count_all = count_all.fetchall()
        for j in range(len(count_all)):
            if i == 0:
                day.append(count_all[j][0])
                num.append(int(count_all[j][1]))
            else:
                num.append(int(count_all[j][1]))
    for i in range(len(day)):
        a = pd.to_datetime(day[i]).weekday()
        if a == 0:
            day[i] = '周一'
        elif a == 1:
            day[i] = '周二'
        elif a == 2:
            day[i] = '周三'
        elif a == 3:
            day[i] = '周四'
        elif a == 4:
            day[i] = '周五'
        elif a == 5:
            day[i] = '周六'
        elif a == 6:
            day[i] = '周日'
    hours = []
    for i in range(24):
        hours.append(i)
    num1 = []
    num2 = []
    a = 0
    for j in range(7):
        for i in range(24):
            num1.append(j)
    for i in range(168):
        num2.append(a)
        a += 1
        if a == 24:
            a = 0
    datas = list(zip(num1, num2, num))
    jsonData = {}
    jsonData['day'] = day
    jsonData['datas'] = datas
    jsonData['hours'] = hours
    jsonData['max'] = max(num)

    return jsonData

# 定义信息属性走势图Ajax请求
@home.route("/chart/counttype/", methods=["GET", "POST"])
@user_login_req
def chart_line_counttype():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    countmg = "select DATE_FORMAT(datetime.date,'%m-%d'), IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where `data`.mg = '敏感' and content like '" + "%" + keyname + "%" + "' GROUP BY date_format(created_at,'%Y-%m-%d')) t1 ON  date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    countmg = db.session.execute(countmg)
    countmg = countmg.fetchall()

    count_nomg = "select DATE_FORMAT(datetime.date,'%m-%d'), IFNULL(t1.count1, 0) from datetime LEFT JOIN (SELECT created_at, COUNT(*) AS count1 FROM `data` where `data`.mg is null and content like '" + "%" + keyname + "%" + "' GROUP BY date_format(created_at,'%Y-%m-%d')) t1 ON  date_format(datetime.date,'%Y-%m-%d')  = date_format(t1.created_at,'%Y-%m-%d') where TIMESTAMPDIFF(day,datetime.date,now()) <= "+ timeb +" and TIMESTAMPDIFF(day,datetime.date,now()) >= 1 order by datetime.date;"
    count_nomg = db.session.execute(count_nomg)
    count_nomg = count_nomg.fetchall()

    yAxisData = [[], []]
    yAxisData[0].append([x[1] for x in countmg])
    yAxisData[1].append([x[1] for x in count_nomg])

    legendData = ['敏感', '非敏感']
    xAxisData = [x[0] for x in countmg]

    jsonData = {}
    jsonData['legendData'] = legendData
    jsonData['xAxisData'] = xAxisData
    jsonData['yAxisData'] = yAxisData

    return jsonData

# 定义媒体图Ajax请求
@home.route('/chart/bie/in', methods=["GET", "POST"])
@user_login_req
def chart_bie_in():
    keyname = (Settingtask.query.get(int(session["user_id"]))).keyname
    count_wb = "select count(*) from data where source = '微博' and content like '" + "%" + keyname + "%" + "' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +" ;"
    count_wb = db.session.execute(count_wb)
    count_wb = count_wb.fetchall()

    count_tb = "select count(*) from data where source = '贴吧' and content like '" + "%" + keyname + "%" + "' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +" ;"
    count_tb = db.session.execute(count_tb)
    count_tb = count_tb.fetchall()

    count_wx = "select count(*) from data where source = '微信' and content like '" + "%" + keyname + "%" + "' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +" ;"
    count_wx = db.session.execute(count_wx)
    count_wx = count_wx.fetchall()

    count_sh = "select count(*) from data where source = '搜狐新闻' and content like '" + "%" + keyname + "%" + "' and TIMESTAMPDIFF(day,created_at,now()) <= "+ timeb +" ;"
    count_sh = db.session.execute(count_sh)
    count_sh = count_sh.fetchall()

    # count_rm = "select count(*) from data where source = '人民网' and content like '" + "%" + keyname + "%" + "' and TIMESTAMPDIFF(day,created_at,now()) <= 7 ;"
    # count_rm = db.session.execute(count_rm)
    # count_rm = count_rm.fetchall()

    legendData = ['微博', '贴吧', '微信', '搜狐新闻']
    datas = [count_wb[0][0], count_tb[0][0], count_wx[0][0], count_sh[0][0]]
    jsonData = {}
    jsonData['legendData'] = legendData
    jsonData['datas'] = datas

    return jsonData


@home.route("/test/x/", methods=["GET", "POST"])
@user_login_req
def xxx():

    return render_template('auth/test.html')

@home.route("/test/")
def test():
    pass
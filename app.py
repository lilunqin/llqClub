from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import secret
from models.base_model import db
from models.board import Board
from models.user import User

from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.message import main as message_routes
from utils import log
import time

class UserModelView(ModelView):
    column_searchable_list = ('username', 'password')


def remove_script(content):
    log('remove_script <{}> <{}>'.format(type(content), content))
    # content 在用了 | safe 过滤器后，不是 str 类型
    c = str(content)
    c = c.replace('>', '&gt;')
    c = c.replace('<', '&lt;')
    # c = c.replace('script', 'removed')
    print('remove_script after <{}>'.format(c))
    return c

def format_time(unix_timestamp):
    # enum Year():
    #     2013
    #     13
    # f = Year.2013
    current_time = time.time()
    value = (current_time - unix_timestamp) // 86400
    return value

def configured_app():
    # web framework
    # web application
    # __main__
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    # 这个字符串随便你设置什么内容都可以
    app.secret_key = secret.secret_key

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{}@localhost/llqClub?charset=utf8mb4'.format(
        secret.database_password
    )
    db.init_app(app)

    app.template_filter()(remove_script)
    app.template_filter()(format_time)

    admin = Admin(app, name='llqClub admin', template_mode='bootstrap3')
    mv = UserModelView(User, db.session)
    admin.add_view(mv)
    mv = ModelView(Board, db.session)
    admin.add_view(mv)

    register_routes(app)
    return app


def register_routes(app):
    """
    在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
    蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
    用法如下
    """
    # 注册蓝图
    # 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(message_routes, url_prefix='/message')


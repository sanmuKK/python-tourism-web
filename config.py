from redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail,Message
import pymysql
pymysql.install_as_MySQLdb()
from warnings import filterwarnings
filterwarnings("ignore",category=pymysql.Warning)


ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])



login_manager = LoginManager()
mail = Mail()
msg = Message(subject='欢迎注册我们的网站', sender='旅游网<18965600766ljl@sina.com>')
db = SQLAlchemy()
rd = Redis(host='localhost',port=6379,decode_responses=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def del_verify_code(key,email):
    import time
    time.sleep(300)
    rd.hdel(key,email)


@login_manager.user_loader
def load_user(user_id):
    from models import User
    user = User.query.get(user_id)
    return user
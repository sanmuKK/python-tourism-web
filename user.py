from flask import jsonify,request,Blueprint,json
from flask_login import login_user,logout_user,login_required,current_user
from models import User
from config import db,rd
from ast import literal_eval


user=Blueprint('user',__name__,url_prefix='/api')


@user.route('/test_login')
def test():
    user_id = request.args.get('email','test_email')
    password = request.args.get('password', 'test_password')
    name = request.args.get('name', 'test_name')
    avatar = request.args.get('avatar', '/static/haimianbaobao.jpeg')
    sex = request.args.get('sex', '保密')
    user = User(email=user_id,password=password,name=name,avatar=avatar, sex=sex)
    user_test = User.query.filter(User.email==user_id).first()
    if not user_test:
        db.session.add(user)
        db.session.commit()
        logout_user()
        login_user(user, remember=True)
    else:
        logout_user()
        login_user(user_test, remember=True)
    return jsonify({'status':'success'})


@user.route('/login',methods=['POST'])
def login():
    dict = json.loads(request.get_data(as_text=True))
    user_id = dict.get('login_id','')
    password = dict.get('login_password','')
    user = User.query.filter(User.email == user_id).first()
    if user and password == user.password:
        login_user(user,remember=True)
        return jsonify({'status':'success'})
    return jsonify({'status':'fail'})


@user.route('/register',methods=['POST'])
def register():
    dict = json.loads(request.get_data(as_text=True))
    user_id = dict.get('register_email','')
    name = dict.get('register_name', '')
    password = dict.get('register_password','')
    code = dict.get('register_code', '')
    if code != rd.hget("email_type_4",user_id):
        return jsonify({'status': '验证码错误'})
    test_user = User.query.filter(User.email == user_id).first()
    if test_user:
        rd.hdel("email_type_4",user_id)
        return jsonify({'status': '该账号已被注册'})
    else:
        user = User(email=user_id,password=password,name=name)
        db.session.add(user)
        db.session.commit()
        rd.hdel("email_type_4",user_id)
    return jsonify({'status':'success'})


@user.route('/edit_user_info',methods=['POST'])
@login_required
def editinfo():
    dict = json.loads(request.get_data(as_text=True))
    name = dict.get('edit_name', '')
    avatar = dict.get('edit_file', '')
    sex = dict.get('edit_sex', '')
    if name:
        current_user.name=name
    if avatar:
        current_user.avatar=avatar
    if sex:
        current_user.sex=sex
    db.session.commit()
    return jsonify({'用户名':current_user.name,'性别':current_user.sex,'头像':current_user.avatar})


@user.route('/change_email',methods=['POST'])
@login_required
def changeemail():
    dict = json.loads(request.get_data(as_text=True))
    email = dict.get('change_email', '')
    code = dict.get('change_code', '')
    code_new = dict.get('change_code_new', '')
    if code != rd.hget("email_type_2",current_user.email):
        return jsonify({'status': '旧邮箱的验证码错误'})
    if code_new != rd.hget("email_type_3",email):
        return jsonify({'status': '新邮箱的验证码错误'})
    user = User.query.get(current_user.id)
    user_new = User.query.filter(User.email == email).first()
    if user_new:
        rd.hdel("email_type_3", email)
        return jsonify({'status': '该邮箱已经注册过了'})
    else:
        user.email = email
        db.session.commit()
        rd.hdel("email_type_2",current_user.email)
        rd.hdel("email_type_3", email)
        return jsonify({'status':'success'})


@user.route('/fotget_password',methods=['POST'])
def fotgetpassword():
    dict = json.loads(request.get_data(as_text=True))
    user_id = dict.get('fotget_email','')
    password = dict.get('fotget_password','')
    code = dict.get('fotget_code', '')
    if code != rd.hget("email_type_1",user_id):
        return jsonify({'status': '验证码错误'})
    if password:
        user = User.query.filter(User.email == user_id).first()
        user.password = password
        db.session.commit()
        rd.hdel("email_type_1", user_id)
        return jsonify({'status':'success'})
    return jsonify({'status': 'fail'})


@user.route('/get_collection')
@login_required
def get_collection():
    co = current_user.collection_list
    list1 = []
    for i in co:
        image = literal_eval(i.owner_article.image)
        dict2 = image[0]
        dict1={
            'image':dict2['image'],
            'id':i.id,
            'article_id':i.owner_article.id,
            'article_title':i.owner_article.title
        }
        list1.append(dict1)
    return jsonify({'collections':list1})


@user.route('/get_my_article')
@login_required
def get_my_article():
    art = current_user.article
    list1 = []
    for i in art:
        image = literal_eval(i.image)
        dict2 = image[0]
        dict1={
            'image':dict2['image'],
            'article_id':i.id,
            'article_title':i.title
        }
        list1.append(dict1)
    return jsonify({'articles':list1})


@user.route('/thumb_me_list')
@login_required
def thumb_me_list():
    art = current_user.article
    list1 = []
    for i in art:
        for j in i.thumb_list:
            dict1 = {
                'article_id': i.id,
                'article_title': i.title,
                'thumb_id':j.id,
                'thumb_user_id':j.owner_user.id,
                'thumb_user_name':j.owner_user.name
            }
            list1.append(dict1)
    list2 = sorted(list1, key=lambda keys: keys['thumb_id'], reverse=True)
    return jsonify({'thumb_me_users': list2})


@user.route('/collect_me_list')
@login_required
def collect_me_list():
    art = current_user.article
    list1 = []
    for i in art:
        for j in i.collection_list:
            dict1 = {
                'article_id': i.id,
                'article_title': i.title,
                'collection_id':j.id,
                'collection_user_id':j.owner_user.id,
                'collection_user_name':j.owner_user.name
            }
            list1.append(dict1)
    list2 = sorted(list1, key=lambda keys: keys['collection_id'], reverse = True)
    return jsonify({'collect_me_users': list2})


@user.route('/comment_me_list')
@login_required
def comment_me_list():
    art = current_user.article
    list1 = []
    for i in art:
        for j in i.comment:
            dict1 = {
                'article_id': i.id,
                'article_title': i.title,
                'comment_id':j.id,
                'comment_text':j.comment,
                'comment_time':j.time.strftime('%Y-%m-%d %H:%M'),
                'comment_user_id':j.owner_user.id,
                'comment_user_name':j.owner_user.name
            }
            list1.append(dict1)
    list2 = sorted(list1, key=lambda keys: keys['comment_id'], reverse = True)
    return jsonify({'comment_me': list2})


@user.route('/reply_me_list')
@login_required
def reply_me_list():
    co = current_user.comment
    list1 = []
    for i in co:
        for j in i.reply:
            dict1 = {
                'article_id': i.owner_article.id,
                'article_title': i.owner_article.title,
                'comment_id':i.id,
                'comment_text':i.comment,
                'comment_time':i.time.strftime('%Y-%m-%d %H:%M'),
                'reply_id':j.id,
                'reply_text':j.reply,
                'reply_time':j.time.strftime('%Y-%m-%d %H:%M'),
                'reply_user_id':j.owner_user.id,
                'reply_user_name':j.owner_user.name
            }
            list1.append(dict1)
    list2 = sorted(list1, key=lambda keys: keys['reply_id'], reverse = True)
    return jsonify({'reply_me': list2})


@user.route('/getinfo')
@login_required
def getinfo():
    return jsonify({'用户id':current_user.id,'账号':current_user.email,'用户名':current_user.name
                    ,'性别':current_user.sex,'头像':current_user.avatar})


@user.route('/getotherinfo',methods=['POST'])
def getinfo2():
    dict = json.loads(request.get_data(as_text=True))
    user_id = dict.get('user_id',0)
    user = User.query.get(user_id)
    return jsonify({'用户id':user.id,'账号':user.email,'用户名':user.name,'性别':user.sex,'头像':user.avatar})


@user.route('/logout_user')
@login_required
def logoutuser():
    logout_user()
    return jsonify({'status':'success'})
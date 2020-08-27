from flask import jsonify,request,session,Blueprint,json,send_from_directory
from config import mail,msg,allowed_file,rd,del_verify_code
import random,os
import threading
import requests


others=Blueprint('others',__name__,url_prefix='/api')


@others.route('/upload',methods=['POST'])
def upload():
    avatar = request.files.get('file')
    if not avatar:
        icon = '/static/haimianbaobao.jpeg'
    elif not allowed_file(avatar.filename):
        return jsonify({'status': '图片格式不支持'})
    else:
        path = r'./static'
        avatar.save(os.path.join(path, avatar.filename))
        icon = '/static/' + avatar.filename
    return jsonify({'icon':icon})


@others.route('/static/<filename>')
def getfile(filename):
    path=os.getcwd()+'/static'
    return send_from_directory(path,filename)


@others.route('/send_email',methods=['POST'])
def send_email_edit_password():
    dict=json.loads(request.get_data(as_text=True))
    email = dict.get('email','')
    type = dict.get('type',0)
    if not type or not email:
        return jsonify({'status':'fail'})
    msg.recipients=[]
    msg.recipients.append(email)
    code = ''
    for i in range(0,4):
        code += str(random.randint(0,9))
    if type == 1:
        key = "email_type_1"
        msg.body = '您的账户正在试图修改密码,如非本人操作请忽略,您的验证码为'+code
    elif type == 2:
        key = "email_type_2"
        msg.body = '您的账户正在试图更换绑定的邮箱,如非本人操作请忽略,您的验证码为' + code
    elif type == 3:
        key = "email_type_3"
        msg.body = '有账户正在试图更换绑定的邮箱账号至此邮箱,如非本人操作请忽略,您的验证码为' + code
    else:
        key = "email_type_4"
        msg.body = '您的验证码为' + code
    mail.send(msg)
    rd.hset(key,email,code)
    thread_1 = threading.Thread(target=del_verify_code,args=(key,email))
    thread_1.start()
    return jsonify({'status':'success'})


@others.route('/scenic_introduction')
def scenic_introduction():
    dict = json.loads(request.get_data(as_text=True))
    city = dict.get('city','')
    word = dict.get('word','')
    is_spider_all = rd.hget('is_spider_all',city[:2])
    content = None
    if is_spider_all:
        data = rd.hget(city[:2], word)
        return jsonify({'name':word,'introduction':data})
    else:
        page = 1
        url1 = 'http://api.tianapi.com/txapi/scenic/index?key=41d70b21767cd950e6638d1be3fcbf11&num=15&city='+city
        res = requests.get(url1).json()
        if res['code'] == 200:
            rd.hset('is_spider_all', city[:2], 'True')
            while res['code'] == 200:
                for i in res['newslist']:
                    rd.hset(city[:2], i['name'], i['content'])
                    if i['name'] == word:
                        content = i['content']
                page += 1
                url2 = url1 + '&page='+str(page)
                res = requests.get(url2).json()
                if len(res['newslist']) < 15:
                    break
    return jsonify({'name': word, 'introduction': content})


@others.route('/get_scenic_list',methods=['POST'])
def get_scenic_list():
    dict = json.loads(request.get_data(as_text=True))
    city = dict.get('city', '')
    data = rd.hkeys(city[:2])
    if not data:
        scenic_introduction()
        data = rd.hkeys(city[:2])
    return jsonify({'scenics':data})
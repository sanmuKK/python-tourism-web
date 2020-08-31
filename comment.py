from flask import jsonify,request,Blueprint,json
from flask_login import login_required,current_user
from models import User,Article,Comment,Reply
from config import db


comment=Blueprint('comment',__name__,url_prefix='/api')

@comment.route('/comment',methods=['POST'])
@login_required
def comments():
    dict = json.loads(request.get_data(as_text=True))
    article_id = dict.get('article_id',0)
    text = dict.get('text','')
    co = Comment(user_id=current_user.id,article_id=article_id,comment=text)
    db.session.add(co)
    db.session.commit()
    return jsonify({'status':'success','comment_id':co.id})


@comment.route('/reply',methods=['POST'])
@login_required
def replies():
    dict = json.loads(request.get_data(as_text=True))
    comment_id = dict.get('comment_id',0)
    text = dict.get('text', '')
    re = Reply(comment_id=comment_id,user_id=current_user.id,reply=text)
    db.session.add(re)
    db.session.commit()
    return jsonify({'status': 'success','reply_id':re.id})


@comment.route('/getcomments',methods=['POST'])
def getcomments():
    dict = json.loads(request.get_data(as_text=True))
    article_id = dict.get('article_id', 0)
    art = Article.query.get(article_id)
    list1 = art.comment
    list2 = []
    for i in list1:
        list3 = []
        for j in i.reply:
            dict1 = {
                'id':j.id,
                'reply':j.reply,
                'comment_id':j.comment_id,
                'user_id':j.user_id,
                "name": j.owner_user.name,
                'avatar':j.owner_user.avatar,
                'time':j.time.strftime('%Y-%m-%d %H:%M')
            }
            list3.append(dict1)
        dict2 = {
            "id" : i.id,
            "user_id":i.user_id,
            "name":i.owner_user.name,
            'avatar': i.owner_user.avatar,
            "comment":i.comment,
            'time':i.time.strftime('%Y-%m-%d %H:%M'),
            "replies":list3
        }
        list2.append(dict2)
    return jsonify({'comments': list2})


@comment.route('/del_comment',methods=['DELETE'])
@login_required
def delcomment():
    dict = json.loads(request.get_data(as_text=True))
    id = dict.get('id',0)
    co=Comment.query.get(id)
    if current_user.id == co.owner_user.id:
        db.session.delete(co)
        db.session.commit()
        return jsonify({'status':'success'})
    return jsonify({'status': 'fail'})


@comment.route('/del_reply',methods=['DELETE'])
@login_required
def delreply():
    dict = json.loads(request.get_data(as_text=True))
    id = dict.get('id',0)
    re = Reply.query.get(id)
    if current_user.id == re.owner_user.id:
        db.session.delete(re)
        db.session.commit()
        return jsonify({'status':'success'})
    return jsonify({'status': 'fail'})
from ast import literal_eval
from flask import jsonify, request, Blueprint, json
from flask_login import login_required, current_user
from models import User, Article, Thumb, Collection
from config import db
from sqlalchemy import or_

article = Blueprint('article', __name__, url_prefix='/api')


@article.route('/publish', methods=['POST'])
@login_required
def publish():
    dict = json.loads(request.get_data(as_text=True))
    image = dict.get('image', "[]")
    text = dict.get('text', '无')
    title = dict.get('title', '无')
    position = dict.get('position', '无')
    start = dict.get('start', '无')
    days = dict.get('days', '无')
    people = dict.get('people', '无')
    pay = dict.get('pay', '无')
    image2 = str(image)
    article = Article(image=image2, text=text, title=title, position=position, start=start, days=days, people=people,
                      pay=pay, thumb=0, collection=0, article_id=current_user.id)
    db.session.add(article)
    db.session.commit()
    return jsonify({'status': 'success'})


@article.route('/del_article', methods=['DELETE'])
@login_required
def del_article():
    dict = json.loads(request.get_data(as_text=True))
    id = dict.get('article_id', 0)
    art = Article.query.get(id)
    if art.owner_user.id == current_user.id:
        db.session.delete(art)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'fail'})


@article.route('/getarticle')
def getarticle():
    art_id = int(request.args.get('article_id', 0))
    i = Article.query.get(art_id)
    if current_user:
        list1 = current_user.thumb_list
        list2 = current_user.collection_list
    else:
        list1 = []
        list2 = []
    for ii in list1:
        if ii.article_id == i.id and ii.userid == current_user.id:
            thumb_status = True
            break
    else:
        thumb_status = False
    for ii in list2:
        if ii.articleid == i.id and ii.userid == current_user.id:
            collection_status = True
            break
    else:
        collection_status = False
    dict1 = {
        'author_id': i.owner_user.id,
        'author': i.owner_user.name,
        'id': i.id,
        'image': literal_eval(i.image),
        'text': i.text,
        'title': i.title,
        'position': i.position,
        'start': i.start,
        'days': i.days,
        'people': i.people,
        'pay': i.pay,
        'thumb': i.thumb,
        'collection': i.collection,
        'if_thumb': thumb_status,
        'if_collection': collection_status,
        'time':i.time.strftime('%Y-%m-%d %H:%M')
    }
    return jsonify(dict1)


@article.route('/get_all_article')
def get_all_article():
    page = int(request.args.get('page', 1))
    list1 = Article.query.paginate(page, 10, error_out=False)
    list1 = list1.items
    list2 = []
    for i in list1:
        image = literal_eval(i.image)
        dict2 = image[0]
        dict1 = {
            'image':dict2['image'],
            'author': i.owner_user.name,
            'id': i.id,
            'title': i.title,
            'position': i.position,
            'time': i.time.strftime('%Y-%m-%d %H:%M')
        }
        list2.append(dict1)
    return jsonify({'articles': list2})


@article.route('/thumb', methods=['POST'])
@login_required
def thumb():
    dict = json.loads(request.get_data(as_text=True))
    id = dict.get('id', 0)
    art = Article.query.get(id)
    for i in art.thumb_list:
        if i.article_id == art.id and i.userid == current_user.id:
            art.thumb -= 1
            db.session.delete(i)
            db.session.commit()
            return jsonify({'status': 'cancel'})
    else:
        art.thumb += 1
        t = Thumb(userid=current_user.id, article_id=art.id)
        db.session.add(t)
        db.session.commit()
    return jsonify({'status': 'add'})


@article.route('/collect', methods=['POST'])
@login_required
def collect():
    dict = json.loads(request.get_data(as_text=True))
    id = dict.get('article_id', 0)
    art = Article.query.get(id)
    for i in current_user.collection_list:
        if i.articleid == int(id):
            art.collection -= 1
            db.session.delete(i)
            db.session.commit()
            return jsonify({'status': 'cancel'})
    else:
        art.collection += 1
        c = Collection(userid=current_user.id, articleid=id)
        db.session.add(c)
        db.session.commit()
    return jsonify({'status': 'add'})


@article.route('/search_article')
def search_article():
    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', '')
    list1 = Article.query.filter(or_(Article.title.like("%" + keyword + "%") if keyword is not None else "",
                                     Article.position.like("%" + keyword + "%") if keyword is not None else ""
                                     ))
    list1=list1.paginate(page, 10, error_out=False)
    allarticles = list1.total
    allpages = list1.pages
    list1 = list1.items
    list2 = []
    for i in list1:
        image = literal_eval(i.image)
        dict2 = image[0]
        dict1 = {
            'image':dict2['image'],
            'author': i.owner_user.name,
            'id': i.id,
            'title': i.title,
            'position': i.position,
            'time': i.time.strftime('%Y-%m-%d %H:%M')
        }
        list2.append(dict1)
    return jsonify({'search_result': list2,'allarticles':allarticles,'allpages':allpages})
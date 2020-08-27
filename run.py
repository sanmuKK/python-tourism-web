from __init__ import creat_app
from config import login_manager,mail,db


app = creat_app()
db.init_app(app)
login_manager.init_app(app=app)
mail.init_app(app=app)
db.drop_all(app=app)
db.create_all(app=app)


if __name__ == '__main__':
    app.run()
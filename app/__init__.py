from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

#import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    #app.config.from_object(config)#config.py 파일로부터 환경변수 가져오기
    app.config.from_envvar('APP_CONFIG_FILE')

    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    from .views import main_views, apart_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(apart_views.bp)

    return app
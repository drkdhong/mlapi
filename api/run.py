import json
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv   # .env 파일 로드
load_dotenv()
from pathlib import Path
from flask import Flask
from flask_migrate import Migrate
from api import api
from api.config import config
from api.models import db
from api import api

def create_app():
    config_name = os.environ.get("CONFIG", "local")
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    return app
app = create_app()
# DB 마이그레이션의 작성
Migrate(app, db)
# blueprint를 애플리케이션에 등록
app.register_blueprint(api)
print(f"FLASK_APP: {os.getenv('FLASK_APP')} ")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')} ")
print(f"FLASK_DEBUG: {os.getenv('FLASK_DEBUG')} ")
# /api/config/nase.py 변수 LABELS 인쇄
from api.config.base import Config
print(Config.LABELS)   # ['1', '2', '3']
print(app.config['LABELS']) # ['1', '2', '3']




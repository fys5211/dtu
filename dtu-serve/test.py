from app import app
from models import db

with app.app_context():
    db.create_all()  # 创建数据库表s

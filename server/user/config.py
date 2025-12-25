# config.py

import os

class Config:
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

    # 数据库配置（如果使用 SQLite）
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'  # 使用 SQLite 数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 邮件服务配置
    SMTP_HOST = 'smtp.163.com'
    SMTP_PORT = 465
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')  # 你的邮箱（如：your_email@163.com）
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # 你的 SMTP 授权码
    SENDER = SMTP_USERNAME  # 发件人邮箱

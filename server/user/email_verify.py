# email_verify.py

import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from models import db, EmailCode
from config import Config
from datetime import datetime, timedelta

# 生成 6 位验证码
def generate_verification_code():
    return str(random.randint(100000, 999999))

# 存储验证码到数据库
def store_verification_code(email, code):
    expiration_time = datetime.utcnow() + timedelta(minutes=5)  # 验证码有效期 5 分钟
    new_code = EmailCode(email=email, code=code, expires_at=expiration_time)
    db.session.add(new_code)
    db.session.commit()

# 发送验证码邮件
def send_verification_email(recipient_email):
    verification_code = generate_verification_code()

    # 存储验证码到数据库
    store_verification_code(recipient_email, verification_code)

    # 邮件内容
    subject = "邮箱验证码"
    body = f"您的验证码是：{verification_code}。请在 5 分钟内完成验证。"

    msg = MIMEMultipart()
    msg['From'] = formataddr(('Admin', Config.SMTP_USERNAME))
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.sendmail(Config.SMTP_USERNAME, recipient_email, msg.as_string())
        print(f"验证码已发送到 {recipient_email}")
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False

    return True

from flask import Flask, request, jsonify
from models import db, User, EmailCode
from email_verify import send_verification_email
from config import Config
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # 用于加密和验证密码
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 重新初始化数据库表
with app.app_context():
    db.create_all()  # 创建所有数据库表

# 定时任务：清理过期验证码
def cleanup_expired_codes():
    expired_codes = EmailCode.query.filter(EmailCode.expires_at < datetime.utcnow()).all()
    for code in expired_codes:
        db.session.delete(code)
    db.session.commit()
    print(f"已删除 {len(expired_codes)} 条过期验证码记录")

# 初始化定时任务
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_expired_codes, 'interval', hours=1)  # 每小时清理一次过期验证码
    scheduler.start()

# 启动定时任务
start_scheduler()

# 路由：发送验证码邮件
@app.route('/send_register_email', methods=['POST'])
def send_register_email():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"ok": False, "message": "请提供邮箱地址"})

    # 检查用户是否已经注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"ok": False, "message": "该邮箱已注册"})

    # 发送验证码邮件
    if send_verification_email(email):
        return jsonify({"ok": True, "message": "验证码/验证邮件已发送（检查收件箱或垃圾邮件）"})
    else:
        return jsonify({"ok": False, "message": "发送邮件失败"})

# 路由：验证验证码
@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    # 查找验证码记录
    code_record = EmailCode.query.filter_by(code=token).first()

    if not code_record:
        return jsonify({"ok": False, "message": "验证码无效或已过期"})
    
    # 验证验证码是否过期
    if datetime.utcnow() > code_record.expires_at:
        return jsonify({"ok": False, "message": "验证码已过期"})
    
    return jsonify({"ok": True, "message": "验证码验证成功，请继续注册用户"})

# 路由：注册用户
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"ok": False, "message": "请提供邮箱和密码"})

    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"ok": False, "message": "该邮箱已注册"})

    # 将密码进行加密存储
    hashed_password = generate_password_hash(password)

    # 创建新用户
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"ok": True, "message": "注册成功", "user": {"email": email}})

# 路由：登录验证
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"ok": False, "message": "请提供邮箱和密码"})

    # 查找用户
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"ok": False, "message": "该邮箱未注册"})

    # 检查密码是否正确
    if not check_password_hash(user.password, password):
        return jsonify({"ok": False, "message": "密码错误"})

    return jsonify({"ok": True, "message": "登录成功", "user": {"email": email}})

# 路由：验证旧密码
@app.route('/verify_old_password', methods=['POST'])
def verify_old_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('old_password')

    if not email or not old_password:
        return jsonify({"ok": False, "message": "请提供邮箱和旧密码"})

    # 查找用户
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"ok": False, "message": "该邮箱未注册"})

    # 检查旧密码是否正确
    if not check_password_hash(user.password, old_password):
        return jsonify({"ok": False, "message": "旧密码错误"})

    return jsonify({"ok": True, "message": "旧密码验证成功，请输入新密码"})

# 路由：更新密码
@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not email or not old_password or not new_password:
        return jsonify({"ok": False, "message": "请提供邮箱、旧密码和新密码"})

    # 查找用户
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"ok": False, "message": "该邮箱未注册"})

    # 检查旧密码是否正确
    if not check_password_hash(user.password, old_password):
        return jsonify({"ok": False, "message": "旧密码错误"})

    # 将新密码进行加密存储
    hashed_new_password = generate_password_hash(new_password)

    # 更新密码
    user.password = hashed_new_password
    db.session.commit()

    return jsonify({"ok": True, "message": "密码修改成功"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

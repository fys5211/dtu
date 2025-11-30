from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import db, User  # 假设你的模型定义在 models.py 中

# 连接到数据库
DATABASE_URI = 'sqlite:////root/dtu-serve/instance/users.db'  # 这里使用 SQLite 数据库，可以根据需要更改为 MySQL 或 PostgreSQL 等
engine = create_engine(DATABASE_URI, echo=True)
Base = declarative_base()

# 创建 Session 类
Session = sessionmaker(bind=engine)
session = Session()

def show_all_users():
    """显示所有用户"""
    users = session.query(User).all()
    print(f"共 {len(users)} 个注册用户：")
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}")

def show_user_details(email):
    """根据邮箱显示用户详细信息"""
    user = session.query(User).filter_by(email=email).first()
    if user:
        print(f"用户详情：")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
    else:
        print("用户不存在！")

def add_user(email, password):
    """添加新用户"""
    if session.query(User).filter_by(email=email).first():
        print("该邮箱已经注册！")
        return
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    session.add(new_user)
    session.commit()
    print(f"用户 {email} 添加成功！")

def delete_user(email):
    """删除用户"""
    user = session.query(User).filter_by(email=email).first()
    if user:
        session.delete(user)
        session.commit()
        print(f"用户 {email} 已删除！")
    else:
        print("用户不存在！")

def update_password(email, new_password):
    """修改用户密码"""
    user = session.query(User).filter_by(email=email).first()
    if user:
        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        session.commit()
        print(f"用户 {email} 的密码已修改！")
    else:
        print("用户不存在！")

def main():
    while True:
        print("\n用户管理系统")
        print("1. 查看所有用户")
        print("2. 查看用户详情")
        print("3. 添加新用户")
        print("4. 删除用户")
        print("5. 修改密码")
        print("6. 退出")
        
        choice = input("请输入选项：")
        
        if choice == '1':
            show_all_users()
        elif choice == '2':
            email = input("请输入用户邮箱：")
            show_user_details(email)
        elif choice == '3':
            email = input("请输入新用户邮箱：")
            password = input("请输入密码：")
            add_user(email, password)
        elif choice == '4':
            email = input("请输入要删除的用户邮箱：")
            delete_user(email)
        elif choice == '5':
            email = input("请输入要修改密码的用户邮箱：")
            new_password = input("请输入新密码：")
            update_password(email, new_password)
        elif choice == '6':
            print("退出系统")
            break
        else:
            print("无效的选项，请重新输入！")

if __name__ == '__main__':
    main()

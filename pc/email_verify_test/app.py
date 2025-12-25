import requests
import json


# 请求发送验证码邮件
def send_email_for_verification(email):
    url = "http://127.0.0.1:5000/send_register_email"  # 服务器的发送验证码邮件接口
    data = {"email": email}  # 发送给服务器的数据

    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = response.json()
        if response_data['ok']:
            print("验证码已发送，请检查您的邮箱")
            return True
        else:
            print(f"发送失败：{response_data['message']}")
            return False
    else:
        print("请求失败，无法连接到服务器")
        return False


# 验证验证码
def verify_email_code(token):
    url = f"http://127.0.0.1:5000/verify_email/{token}"  # 服务器的验证验证码接口

    response = requests.get(url)

    if response.status_code == 200:
        response_data = response.json()
        if response_data['ok']:
            print("验证码验证成功！")
            return True
        else:
            print(f"验证失败：{response_data['message']}")
            return False
    else:
        print("请求失败，无法连接到服务器")
        return False


# 注册新用户
def register_user(email, password):
    url = "http://127.0.0.1:5000/register"  # 服务器的注册接口
    data = {
        "email": email,
        "password": password
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = response.json()
        if response_data['ok']:
            print("用户注册成功！")
            return True
        else:
            print(f"注册失败：{response_data['message']}")
            return False
    else:
        print("请求失败，无法连接到服务器")
        return False


# 修改密码
def change_password(email, old_password, new_password):
    # 先验证旧密码
    url = "http://127.0.0.1:5000/verify_old_password"  # 服务器的验证旧密码接口
    data = {
        "email": email,
        "old_password": old_password
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = response.json()
        if response_data['ok']:
            # 如果旧密码验证成功，继续修改密码
            url = "http://127.0.0.1:5000/change_password"  # 服务器的修改密码接口
            data = {
                "email": email,
                "old_password": old_password,
                "new_password": new_password
            }

            response = requests.post(url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data['ok']:
                    print("密码修改成功！")
                    return True
                else:
                    print(f"修改失败：{response_data['message']}")
                    return False
            else:
                print("请求失败，无法连接到服务器")
                return False
        else:
            print("旧密码错误，无法修改密码！")
            return False
    else:
        print("请求失败，无法连接到服务器")
        return False


# 用户登录
def login_user(email, password):
    url = "http://127.0.0.1:5000/login"  # 服务器的登录接口
    data = {
        "email": email,
        "password": password
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = response.json()
        if response_data['ok']:
            print("登录成功！")
        else:
            print(f"登录失败：{response_data['message']}")
    else:
        print("请求失败，无法连接到服务器")


# 主程序
def main():
    email = input("请输入您的邮箱：")
    old_password = input("请输入旧密码：")

    # 先验证旧密码
    print("正在验证旧密码...")
    # 验证旧密码
    if change_password(email, old_password, ""):
        new_password = input("请输入新密码：")
        change_password(email, old_password, new_password)


if __name__ == "__main__":
    main()

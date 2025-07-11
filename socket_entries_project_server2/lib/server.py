import hashlib
import socket
import threading
import random # 导入 random 模块
import time

from api import user_i

class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f"服务器 {self.host}:{self.port} 启动成功")
        except Exception as e:
            print(f"服务器启动失败: {e}")
            return

        while True:
            conn, addr = self.server.accept()
            print(f"新客户端连接: {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def handle_client(self, conn, addr):
        print(f"开始与客户端 {addr[0]}:{addr[1]} 交互")
        try:
            while True:
                # 显示主菜单
                conn.send(
                    "欢迎来到游戏服务器！请选择操作：\n"
                    "1. 登录\n"
                    "2. 注册\n"
                    "3. 退出\n"
                    "请输入选项 (1, 2 或 3): ".encode('utf-8')
                )

                choice_data = conn.recv(1024)
                if not choice_data:
                    print(f"客户端 {addr[0]}:{addr[1]} 在主菜单前断开连接")
                    break

                choice = choice_data.decode('utf-8').strip()
                print(f"客户端 {addr[0]}:{addr[1]} 主菜单选择了: {choice}")

                if choice == '1':
                    self.handle_login(conn, addr)

                elif choice == '2':
                    self.handle_register(conn, addr)
                elif choice == '3':
                    conn.send("再见！".encode('utf-8'))
                    break
                else:
                    conn.send("无效的选择，请重新输入。\n".encode('utf-8'))

        except ConnectionResetError:
            print(f"客户端 {addr[0]}:{addr[1]} 强制关闭了连接")
        except Exception as e:
            print(f"与客户端 {addr[0]}:{addr[1]} 的交互出现异常: {e}")
        finally:
            conn.close()
            print(f"与客户端 {addr[0]}:{addr[1]} 的连接已关闭")

    # def show_game_menu(self, conn, addr):
    #     conn.send(
    #         "请选择游戏:\n"
    #         "1. 猜数字\n"
    #         "2. 石头剪刀布\n"
    #         "请输入选项 (1 或 2): ".encode('utf-8')
    #     )
    #
    #     game_choice_data = conn.recv(1024)
    #     if not game_choice_data:
    #         print(f"客户端 {addr[0]}:{addr[1]} 在游戏选择前断开连接")
    #         return
    #
    #     game_choice = game_choice_data.decode('utf-8').strip()
    #
    #     if game_choice == '1':
    #         self.play_guess_the_number(conn, addr)
    #     elif game_choice == '2':
    #         self.play_rock_paper_scissors(conn, addr)
    #     else:
    #         conn.send("无效的游戏选择，返回主菜单。\n".encode('utf-8'))

    def handle_register(self, conn, addr):
        try:
            # 用户名输入和查重
            while True:
                conn.send("请输入用户名:".encode('utf-8'))
                username = conn.recv(1024).decode('utf-8').strip()
                userRegistObj1 = user_i.UserData(userName=username, userPassword=None, index=1)
                userSelect = user_i.UserSelectName(selectObj=userRegistObj1)
                flag, massg = userSelect.selectName()
                if flag and massg[0]:
                    conn.send("该用户已经注册了，请使用其他用户名注册".encode('utf-8'))
                    continue
                break
            from lib.use_saved_model import predict_password_strength
            while True:
                while True:
                    conn.send("请输入密码：\n密码要求：\n- 弱密码：纯数字/纯字母且长度小于8位\n- 强密码：包含数字和字母且长度大于等于8位\n- 很强密码：包含数字、大小写字母和特殊字符且长度大于等于12位\n请输入：".encode('utf-8'))
                    password = conn.recv(1024).decode('utf-8').strip()
                    strength = predict_password_strength(password)
                    conn.send(f"密码强度：{strength}".encode('utf-8'))
                    if strength == "弱":
                        conn.send("密码强度太弱，请设置至少为'强'级别的密码".encode('utf-8'))
                        continue
                    break
                conn.send("请再次输入密码：".encode('utf-8'))
                rePassword = conn.recv(1024).decode('utf-8').strip()
                if password != rePassword:
                    conn.send("两次输入的密码不一致，请重新输入密码。".encode('utf-8'))
                    continue
                Password = hashlib.md5(password.encode("utf-8")).hexdigest()
                user_obj = user_i.UserData(userName=username, userPassword=Password, index=1)
                register_handler = user_i.UserRegist(userRegistObj=user_obj)
                flag, message = register_handler.userRegistData()
                if flag:
                    conn.send(f"注册成功！{message}".encode('utf-8'))
                    break
                else:
                    conn.send(f"注册失败：{message}".encode('utf-8'))
                    break
        except Exception as e:
            print(f"注册过程中发生异常: {e}")
            conn.send("注册过程中发生错误，连接将关闭。".encode('utf-8'))

    def handle_login(self, conn, addr):
        try:
            while True:
                conn.send("请输入用户名:".encode('utf-8'))
                username = conn.recv(1024).decode('utf-8').strip()
                userRegistObj1 = user_i.UserData(userName=username, userPassword=None, index=1)
                userSelect = user_i.UserSelectName(selectObj=userRegistObj1)
                flag, massg = userSelect.selectName()
                if not (flag and massg[0]):
                    conn.send("用户名不存在，请重新输入用户名。".encode('utf-8'))
                    continue
                break
            while True:
                conn.send("请输入密码:".encode('utf-8'))
                password = conn.recv(1024).decode('utf-8').strip()
                password_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
                user_obj = user_i.UserData(userName=username, userPassword=password_md5, index=1)
                login_handler = user_i.UserLogin(userLoginObj=user_obj)
                flag, message = login_handler.userLogin()
                if flag:
                    conn.send(f"登录成功！{message}\n请选择游戏:\n1. 猜数字\n2. 石头剪刀布\n".encode('utf-8'))
                    game_choice = conn.recv(1024).decode('utf-8').strip()
                    if game_choice == '1':
                        self.play_guess_the_number(conn, addr)
                    elif game_choice == '2':
                        self.play_rock_paper_scissors(conn, addr)
                    else:
                        conn.send("无效的游戏选择，连接将关闭。".encode('utf-8'))
                    break
                else:
                    conn.send("密码错误，请重新输入密码。".encode('utf-8'))
        except Exception as e:
            print(f"登录过程中发生异常: {e}")
            conn.send("登录过程中发生错误，连接将关闭。".encode('utf-8'))

    def play_guess_the_number(self, conn, addr):
        """处理猜数字游戏"""
        conn.send("游戏开始：猜数字 (1-100)".encode('utf-8'))
        secret_number = random.randint(1, 100)
        attempts = 0
        print(f"为 {addr[0]}:{addr[1]} 生成的数字是: {secret_number}") # 服务器端日志

        while True:
            try:
                guess_data = conn.recv(1024)
                if not guess_data:
                    print(f"客户端 {addr[0]}:{addr[1]} 在游戏中途断开连接")
                    break
                
                guess = int(guess_data.decode('utf-8').strip())
                attempts += 1
                print(f"收到客户端 {addr[0]}:{addr[1]} 的猜测: {guess}")

                if guess < secret_number:
                    conn.send("太小了!".encode('utf-8'))
                elif guess > secret_number:
                    conn.send("太大了!".encode('utf-8'))
                else:
                    conn.send(f"恭喜你猜对了! 数字是 {secret_number}。你用了 {attempts} 次尝试。".encode('utf-8'))
                    break
            except ValueError:
                 conn.send("请输入有效的数字!".encode('utf-8'))
            except Exception as e:
                print(f"猜数字游戏中出现异常: {e}")
                break

    def play_rock_paper_scissors(self, conn, addr):
        """处理石头剪刀布游戏"""
        conn.send("游戏开始：石头剪刀布 (输入 'rock', 'paper', 或 'scissors')".encode('utf-8'))
        choices = ['rock', 'paper', 'scissors']

        while True:
            try:
                client_choice_data = conn.recv(1024)
                if not client_choice_data:
                    print(f"客户端 {addr[0]}:{addr[1]} 在游戏中途断开连接")
                    break

                client_choice = client_choice_data.decode('utf-8').strip().lower()
                print(f"收到客户端 {addr[0]}:{addr[1]} 的选择: {client_choice}")

                if client_choice not in choices:
                    conn.send("无效的选择，请输入 'rock', 'paper', 或 'scissors'".encode('utf-8'))
                    continue

                server_choice = random.choice(choices)
                print(f"服务器为 {addr[0]}:{addr[1]} 的选择: {server_choice}")

                result = ""
                if client_choice == server_choice:
                    result = "平局!"
                elif (client_choice == 'rock' and server_choice == 'scissors') or \
                     (client_choice == 'scissors' and server_choice == 'paper') or \
                     (client_choice == 'paper' and server_choice == 'rock'):
                    result = "你赢了!"
                else:
                    result = "你输了!"

                response = f"服务器选择了 {server_choice}. {result} \n是否再玩一局? (yes/no): ".encode('utf-8')
                conn.send(response)

                # 询问是否继续
                play_again_data = conn.recv(1024)
                if not play_again_data:
                     print(f"客户端 {addr[0]}:{addr[1]} 在询问是否继续时断开连接")
                     break
                play_again = play_again_data.decode('utf-8').strip().lower()
                if play_again != 'yes':
                    conn.send("游戏结束。".encode('utf-8'))
                    break
                else:
                     conn.send("新一局开始... 请出拳:".encode('utf-8')) # 提示开始新一局

            except Exception as e:
                print(f"石头剪刀布游戏中出现异常: {e}")
                conn.send("游戏出错，连接将关闭。".encode('utf-8'))
                break


class UDPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            print(f"UDP 服务器 {self.host}:{self.port} 启动成功")
        except Exception as e:
            print(f"UDP 服务器启动失败: {e}")
            return

        while True:
            data, addr = self.server.recvfrom(2048)  # 接收数据
            message = data.decode('utf-8')
            print(f"收到客户端 {addr[0]}:{addr[1]} 的消息: {message}")

            # 创建一个线程来处理这个客户端请求
            client_thread = threading.Thread(target=self.handle_udp_client, args=(data, addr))
            client_thread.start()

    # 新增方法
    def handle_udp_client(self, data, addr):
        message = data.decode('utf-8')
        print(f"收到客户端 {addr[0]}:{addr[1]} 的消息: {message}")
        # 回复消息
        response = input("请输入要回复的消息 (输入 'exit' 断开连接): ")
        while not response.strip():
            print("输入不能为空，请重新输入")
            response = input("请输入要回复的消息: ")
        self.server.sendto(response.encode('utf-8'), addr)  # 发送数据
        if response.lower() == 'exit':
            print(f"主动断开与客户端 {addr[0]}:{addr[1]} 的连接")


if __name__ == '__main__':
    print("你是想要使用什么协议?")
    socket1 = input("请输入tcp或udp:")
    if socket1 == 'tcp' or socket1 == 'TCP':
        server = TCPServer('172.20.10.5', 45001) # 确保 IP 和端口正确
    else:
        # 提示 UDP 游戏功能未实现
        print("注意：UDP 模式当前不支持交互式游戏。")
        server = UDPServer('10.191.188.13', 45001) # 确保 IP 和端口正确
    server.start()

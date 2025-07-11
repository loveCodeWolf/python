import socket
import threading # threading 在此文件中未使用，可以考虑移除


class TCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            print(f"成功连接到服务器 {self.host}:{self.port}")
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
        return True

    def start(self):
        if not self.connect():
            return

        try:
            while True:
                # 接收主菜单信息
                main_menu = self.client.recv(2048).decode('utf-8')
                print(main_menu)

                choice = input("请输入选项: ").strip()
                self.client.send(choice.encode('utf-8'))

                if choice == '1':
                    success = self.handle_login()
                    if success:
                        self.show_game_menu()
                elif choice == '2':
                    success = self.handle_register()
                    #这里登录成功之后会回到主界面，从而再次进行选择接下来要进行的操作
                elif choice == '3':
                    print("已退出，再见！")
                    break
                else:
                    print("无效的选择，请重新输入。")

        except ConnectionAbortedError:
            print("与服务器的连接被中止。")
        except Exception as e:
            print(f"与服务器的连接出现异常: {e}")
        finally:
            self.client.close()
            print("客户端已关闭")

    def handle_login(self):
        try:
            while True:
                response = self.client.recv(2048).decode('utf-8')
                print(response)
                if "用户名不存在" in response:
                    response = self.client.recv(2048).decode('utf-8')
                    print(response)
                    username = input("")
                    self.client.send(username.encode('utf-8'))
                    continue
                elif "请输入用户名" in response:
                    username = input("")
                    self.client.send(username.encode('utf-8'))
                    continue
                elif "请输入密码" in response:
                    password = input("")
                    self.client.send(password.encode('utf-8'))
                    continue
                elif "密码错误" in response:
                    print(response)
                    # 这里直接提示输入密码并发送，避免等待服务端的下一个提示
                    password = input("请重新输入密码: ")
                    self.client.send(password.encode('utf-8'))
                    continue
                elif "登录成功" in response:
                    print("登录成功！")
                    return True
                elif "登录过程中发生错误" in response:
                    print(response)
                    return False
                else:
                    print(response)
                    return False
        except Exception as e:
            print(f"登录过程中发生错误: {e}")
            return False

    def handle_register(self):
        try:
            while True:
                response = self.client.recv(2048).decode('utf-8')
                print(response)
                if "请输入用户名" in response:
                    username = input("")
                    self.client.send(username.encode('utf-8'))
                elif "该用户已经注册了" in response:
                    continue  # 服务器会再次提示输入用户名
                elif "请输入密码" in response:
                    password = input("")
                    self.client.send(password.encode('utf-8'))
                elif "密码强度：" in response:
                    print(response)
                    # 服务器会继续提示强度太弱或进入下一步
                elif "密码强度太弱" in response:
                    continue  # 服务器会再次提示输入密码
                elif "请再次输入密码" in response:
                    rePassword = input("")
                    self.client.send(rePassword.encode('utf-8'))
                elif "两次输入的密码不一致" in response:
                    print(response)
                    return False
                elif "注册成功" in response:
                    print(response)
                    return True
                elif "注册失败" in response:
                    print(response)
                    return False
                elif "注册过程中发生错误" in response:
                    print(response)
                    return False
        except Exception as e:
            print(f"注册过程中发生错误: {e}")
            return False


    def show_game_menu(self):
        try:
            game_choice = input("请选择游戏: ")
            self.client.send(game_choice.encode('utf-8'))

            if game_choice == '1':
                self.play_guess_the_number()
            elif game_choice == '2':
                self.play_rock_paper_scissors()
            else:
                print("无效的选择，返回主菜单。")
        except Exception as e:
            print(f"游戏菜单中发生错误: {e}")

    def play_guess_the_number(self):
        """客户端处理猜数字游戏"""
        try:
            # 接收游戏开始提示
            game_prompt = self.client.recv(1024).decode('utf-8')
            print(f"服务器: {game_prompt}")

            while True:
                guess = input("请输入你的猜测: ")
                if not guess.isdigit():
                    print("请输入一个有效的数字。")
                    continue

                self.client.send(guess.encode('utf-8'))

                response = self.client.recv(1024).decode('utf-8')
                print(f"服务器: {response}")

                if "恭喜你猜对了" in response:
                    break
                elif "请输入有效的数字" in response: # 处理服务器端的校验信息
                    continue # 让用户重新输入

        except Exception as e:
            print(f"猜数字游戏中出现异常: {e}")


    def play_rock_paper_scissors(self):
        """客户端处理石头剪刀布游戏"""
        try:
            # 接收游戏开始提示
            game_prompt = self.client.recv(1024).decode('utf-8')
            print(f"服务器: {game_prompt}")

            while True:
                client_choice = input("请出拳 (rock, paper, scissors): ").lower()
                if client_choice not in ['rock', 'paper', 'scissors']:
                     print("无效的选择，请重新输入。")
                     continue

                self.client.send(client_choice.encode('utf-8'))

                # 接收结果和是否继续的询问
                response = self.client.recv(2048).decode('utf-8')
                print(f"服务器: {response}")

                if "游戏结束" in response:
                    break
                elif "无效的选择" in response: # 如果服务器认为选择无效
                    continue # 让用户重新输入

                # 检查是否包含 "是否再玩一局?"
                if "是否再玩一局?" in response:
                    play_again = input().lower()
                    self.client.send(play_again.encode('utf-8'))
                    if play_again != 'yes':
                        # 接收最终的游戏结束消息
                        final_msg = self.client.recv(1024).decode('utf-8')
                        print(f"服务器: {final_msg}")
                        break
                    else:
                        # 接收新一局的提示
                        new_round_prompt = self.client.recv(1024).decode('utf-8')
                        print(f"服务器: {new_round_prompt}")


        except Exception as e:
            print(f"石头剪刀布游戏中出现异常: {e}")


class UDPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        while True:
            try:
                # 发送消息
                message = input("请输入要发送的消息 (输入 'exit' 断开连接): ")
                while not message.strip():
                    print("输入不能为空，请重新输入")
                    message = input("请输入要发送的消息: ")

                self.client.sendto(message.encode('utf-8'), (self.host, self.port))

                if message.lower() == 'exit':
                    print("断开与服务器的连接")
                    break

                # 接收消息
                data, _ = self.client.recvfrom(2048)
                if not data:
                    print("服务器没有数据发送过来")
                    continue

                print(f"收到服务器的消息: {data.decode('utf-8')}")

            except Exception as e:
                print(f"与服务器的通信出现异常: {e}")
                break

        self.client.close()
        print("UDP 客户端已关闭")


if __name__ == '__main__':
    print("你是想要使用什么协议?")
    socket2 = input("请输入tcp或udp:")
    if socket2 == 'tcp' or socket2 == 'TCP':
        client = TCPClient('172.20.10.5', 45001) # 确保 IP 和端口正确
        client.start() # 直接调用 start
    else:
        print("注意：UDP 模式当前不支持交互式游戏。")
        client = UDPClient('10.191.188.13', 45001) # 确保 IP 和端口正确
        # client.start() # UDP start 保持原样，不进行游戏交互
        print("UDP 客户端启动，但游戏功能不可用。")

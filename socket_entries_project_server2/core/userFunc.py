#所有用户收集的信息都在这里
#可以认为是前端的数据收集，

import hashlib #进行加密

from api.user_i import *


from lib.isLogin import IsLogin
from lib.client import TCPClient,UDPClient

from lib.use_saved_model import predict_password_strength # Changed import
# 用户权限
userLoginName = None

class User:
    def __init__(self):
        self.userName = "用户名"
        self.userPassword = "密码"
        self.flag = True
        self.messg = ""


class UserFunc(User):
    def __init__(self,index):
        super(UserFunc,self).__init__()
        self.index = index  #这里的就是来权限分流的
    def userRegist(self):
        while True:
            self.userName = input("请输入用户名：")
            #提前验证用户名是否有重复
            userRegistObj1 = UserData(userName=self.userName,userPassword=None,index=self.index)
            userSelect = UserSelectName(selectObj=userRegistObj1)
            flag, massg = userSelect.selectName()
            if flag and massg[0]:
                print("该用户已经注册了，请使用其他用户名注册")
                continue
            break

        self.userPassword = input("请输入密码：\n密码要求：\n- 弱密码：纯数字/纯字母且长度小于8位\n- 强密码：包含数字和字母且长度大于等于8位\n- 很强密码：包含数字、大小写字母和特殊字符且长度大于等于12位\n请输入：")
        while True:
            strength = predict_password_strength(self.userPassword) # Changed function call
            print("密码强度：",strength)
            if strength == "弱":
                print("密码强度太弱，请设置至少为'强'级别的密码")
                self.userPassword = input("请换一个密码输入：")
                continue
            # print(f"当前密码强度：{strength}") # 暂时禁用强度显示
            break # 暂时跳过强度检查
        rePassword = input("请再次输入密码：")

        if self.userPassword == rePassword:
            self.userPassword = hashlib.md5(self.userPassword.encode("utf-8")).hexdigest()
            userDataObj = UserData(userName=self.userName,userPassword=self.userPassword,index=self.index)

            #这里实例化注册对象进行注册
            userRegistObj = UserRegist(userRegistObj=userDataObj)
            self.flag ,self.messg = userRegistObj.userRegistData()
            if self.flag:
                print(self.messg)

            elif not self.flag:
                print(self.messg)

    def userLogin(self):
        self.userName = input("请输入用户名：")
        self.userPassword = input("请输入密码：")
        self.userPassword = hashlib.md5(self.userPassword.encode("utf-8")).hexdigest()
        userDataObj = UserData(userName=self.userName,userPassword=self.userPassword,index=self.index)

        userLogin = UserLogin(userLoginObj=userDataObj)
        self.flag,self.messg = userLogin.userLogin()

        if self.flag:
            global userLoginName
            userLoginName = self.userName
            print(userLoginName)
            print(self.messg)
        else:
            print(self.messg)
    @IsLogin
    def userClient(self):
        print("你是想要使用什么协议?")
        socket2 = input("请输入tcp或udp:")
        if socket2 == 'tcp' or socket2 == 'TCP':
            client = TCPClient('10.191.177.53', 45001)
        else:
            client = UDPClient('10.191.177.53', 45001)
        client.start()
    


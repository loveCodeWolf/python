from core.userFunc import UserFunc
from lib import *
from lib.isLogin import IsLogin
from lib.server import TCPServer,UDPServer


class ManageFunc(UserFunc):
    def __init__(self, index):
        super(ManageFunc, self).__init__(index)
        self.index = index

    def manageRegist(self):  #这里可以直接使用user的登陆注册的方法，因为一开始就做了index的分流了，会在后端查表的时候做分流
        UserFunc.userRegist(self)

    def manageLogin(self):
        UserFunc.userLogin(self)

    @IsLogin
    def manageServer(self):
        print("你是想要使用什么协议?")
        socket1 = input("请输入tcp或udp:")
        if socket1 == 'tcp' or socket1 == 'TCP':
            server = TCPServer('192.168.137.1', 45001)
        else:
            server = UDPServer('10.191.177.53', 45001)
        server.start()


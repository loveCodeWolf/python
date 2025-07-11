# 注册的时候，数据需要进一步处理
# 现在面向对象的用户数据是以类整理

# 传参都是以对象传参
from DB.DBHandle import RegistMysql,SelectMysql

class UserData:  #这里方便之后的账号密码的数据传入
    def __init__(self,userName,userPassword,index):
        self.userName = userName
        self.userPassword = userPassword
        self.index = index


class UserRegist:
    def __init__(self,userRegistObj):
        self.userRegistObj = userRegistObj

    def userRegistData(self):
        #先查询数据库
        userSelect = UserSelectName(selectObj = self.userRegistObj)
        flag , massg = userSelect.selectName()
        if flag and massg[0]:
            return False,"该用户已经注册了，请使用其他用户名注册"

        elif flag and not massg[0]:
            #直接传入数据库
            userRegister = RegistMysql(userDataObj = self.userRegistObj)
            flag , massg = userRegister.setUserMysql()

            if flag:
                return True,"注册成功，请及时登录"
            elif not flag:
                return flag, massg
        else:
            return False,"系统正在维护中......."


class UserSelectName:  #这里的作用是查找数据库是否有这个人的信息
    def __init__(self,selectObj):
        self.selectObj = selectObj

    def selectName(self):
        # 先查询数据库
        selectMysql = SelectMysql(selectObj=self.selectObj)
        flag, massg = selectMysql.userSelect()

        #这里会有三种结果，第一种是查询成功，第二种是查询失败数据库报错，第三种是查询成功但是没有数据。
        if flag:
            if massg: #这里是查询是否有用户的信息
                return True,[True,massg]

            else:
                return True,[False,"用户名不存在"]

        else:
            return False,[False,"系统正在维护中......."]

class UserLogin:
    def __init__(self,userLoginObj):
        self.userLoginObj = userLoginObj

    def userLogin(self):
        userSelect = UserSelectName(selectObj = self.userLoginObj)

        flag , massg = userSelect.selectName()

        if flag and massg[0]:
            userPassword = massg[1][0][2]

            if self.userLoginObj.userPassword == userPassword:  #这里的密码是加密的，所以需要比对加密串的方式搞
                return True,"登录成功，请选择其他功能"
            else:
                return False,"密码错误,请重新登录"
        elif flag and not massg[0]:
            return False,massg[1]

        else:
            return False,massg[1]


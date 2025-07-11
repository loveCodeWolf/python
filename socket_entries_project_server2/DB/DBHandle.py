#这里的是数据库的内容

import pymysql
from Exception.Exception_i import MysqlException


#直接创建一个链接数据库的对象，进行对数据库的统一管理
class MysqlLink:
    def __init__(self):
        self.db = pymysql.connect(host='127.0.0.1',
                                  user='root',
                                  password='root',
                                  database='CarRent928',
                                  charset='utf8')
        #初始化游标，用于执行SQL语句并与数据库进行交互。
        self.cur = self.db.cursor()
        #数据分类,判断是否正确
        self.flag = True
        #数据信息内容,返回的信息
        self.messg = ""

    #数据三步骤：提交，回滚（错误），关闭
    def commitMysql(self,sql): #插入、更新、删除
        self.cur.execute(sql)
        self.db.commit()

    def rollbackMysql(self): #撤销未提交的更改。
        self.db.rollback() #回滚事务，恢复到上一次提交的状态。

    # def closeMysql(self): #关闭数据库连接
    #     self.cur.close()
    #     self.db.close()

class RegistMysql(MysqlLink):
    def __init__(self,userDataObj):
        super(RegistMysql, self).__init__() #调用RegistMysql的父类的初始化方法
        self.userDataObj = userDataObj

    def setUserMysql(self):
        #这里的需要用到引号括起%s
        if self.userDataObj.index == 0:
            self.userRegistSql = "insert into users(userName, userPassword) values ('%s', '%s')" % (self.userDataObj.userName, self.userDataObj.userPassword)

        elif self.userDataObj.index == 1:
            self.userRegistSql = "insert into managers(manageName, managePassword) values ('%s', '%s')" % (self.userDataObj.userName, self.userDataObj.userPassword)

        """
        # DBobj = MysqlLink() #在这里实例化对象，从而传给Exception_i中的异常报错的对象
        mysqlEp = MysqlException(sql=self.userRegistSql, DBobj=self)
           当你使用 DBobj = MysqlLink() 创建新连接时：
                DBobj 和 self 是两个独立的数据库连接。
                DBobj 的事务未提交时，self 的提交不会影响它。
           改为 DBobj=self 后：
                self 和 DBobj 是同一个对象，事务共享。
                mysqlException 和 commitMysql 都作用于同一个连接，导致重复执行。
        """
        DBobj = MysqlLink() #在这里实例化对象，从而传给Exception_i中的异常报错的对象
        mysqlEp = MysqlException(sql=self.userRegistSql, DBobj=DBobj)  #我这里还是选择进行双对象的方式
        self.flag ,self.massg = mysqlEp.mysqlException()
        if self.flag:
            MysqlLink.commitMysql(self, self.userRegistSql)  #这里需要使用当前的self的实例进行提交
            return True, "入库成功"

        elif not self.flag:
            #这里的显示调用的方式和与 self.rollbackMysql() 等价
            MysqlLink.rollbackMysql(self) #回滚
            return False, self.massg #返回错误的信息

        self.db.close()
        self.cur.close()

class SelectMysql(MysqlLink):
    def __init__(self,selectObj):
        super(SelectMysql,self).__init__()
        self.selectObj = selectObj

    def userSelect(self):
        if self.selectObj.index == 0:
            #这里都是要这样些的，防止sql注入的风险
            self.userSelectSql = f"select * from users where userName='%s'" % self.selectObj.userName

        elif self.selectObj.index == 1:
            self.userSelectSql = f"select * from managers where manageName='%s'" % self.selectObj.userName
        #这里默认就是不能有相同的用户名
        DBobj = MysqlLink()
        mysqlEp = MysqlException(sql=self.userSelectSql, DBobj=DBobj)

        self.flag, self.massg = mysqlEp.mysqlException()
        if self.flag:
            MysqlLink.commitMysql(self, self.userSelectSql)
            """
            fetchall 是游标对象的一个方法，用于获取所有查询结果。
                返回值：返回一个包含所有查询结果的列表，每个元素通常是一个元组，代表一行数据。"""
            return True, self.cur.fetchall()
        elif not self.flag:
            MysqlLink.rollbackMysql(self)
            return False, self.massg

        self.db.close()
        self.cur.close()


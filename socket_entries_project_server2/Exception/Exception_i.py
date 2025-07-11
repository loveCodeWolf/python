#这里的是专门写错误报错的文件
##这里有一个注意点，不能两个python文件相互import的方式引用，
##因为python解释器会先加载一个文件，然后再加载另一个文件，
class MysqlException(Exception):
    def __init__(self,sql,DBobj): #这里的是处理sql的数据的时候的出错处理的一个处理的对象
        self.sql = sql
        self.DBobj = DBobj

    def mysqlException(self):
        try:
            self.DBobj.cur.execute(self.sql)

        except Exception as e:
            return False,e

        else:
            return True,"sql语句和链接都没有任何问题"

        finally:
            # pass #这里的finally函数是一定会执行的，如果是不同两个事务流的时候是没有必要的，但是如果都使用的是一个事务流的话，需要回滚（第一个事务留是测试用的，测试完了需要关闭）
            self.DBobj.rollbackMysql()
            self.DBobj.cur.close()
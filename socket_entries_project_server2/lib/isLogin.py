# 就是如果但引入一个变量值的时候，那么只是引入那时刻的参数值
"""这里是需要特别注意的，我一开始就是只引入了userFunc中的userLoginName变量，这里的值其实是从引入那时起就是不变的"""
# 如果引入整个文件的时候，文件的数值都是可以变化

from core import userFunc

#类装饰
class IsLogin:
    def __init__(self,func):
        self.func = func
        #self.userLoginName = userFunc.userLoginName  # 只在装饰时取了一次值，后面就不会变了
    def __call__(self,*args,**kwargs):
        #这里直接引入对象，然后进行判断，值会随对象的变化而变化
        if userFunc.userLoginName is None:
            print("您还没有登录，请先登录")
        else:
            self.func(self,*args,**kwargs)
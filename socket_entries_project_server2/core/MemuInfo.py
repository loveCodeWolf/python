from core.MenuDict import MenuDictInfo,userDict,manageDict
from core.manageFunc import ManageFunc
from core.userFunc import *


def userInfo():
    while 1:
        print("欢迎来到用户使用李叶凯的网络交互系统".center(40))
        for i in userDict:
            print(i,userDict[i][0])
        while True:
            choice = input("请选择: ")
            if choice.isdigit():
                Select = int(choice)
                break
            else:
                print("请输入有效的数字！")
        if Select not in userDict:
            print("请重新选择")

        elif Select == 0:
            exit()
        else:
            funcUser= UserFunc(0)  # 实例化一个对象,这里的0可以代表一类的用户 这里就是index参数
            func_name = userDict[Select][1]  #这里的作用是选择注册的方法
            if hasattr(funcUser, func_name):   #如果在userDict的对象中存在这个方法的话就执行下面的方法
                getattr(funcUser, func_name)()
            else:
                print(f"方法 {func_name} 不存在")



def manageInfo():
    while 1:
        print("欢迎来到管理员使用李叶凯的网络交互系统".center(40))
        for i in manageDict:
            print(i, manageDict[i][0])
        while True:
            choice = input("请选择: ")
            if choice.isdigit():
                Select = int(choice)
                break
            else:
                print("请输入有效的数字！")
        if Select not in manageDict:
            print("请重新选择")

        elif Select == 0:
            exit()
        else:
            funcManage = ManageFunc(1)
            func_name = manageDict[Select][1]  # 这里的作用是选择注册的方法
            if hasattr(funcManage, func_name):  # 如果在userDict的对象中存在这个方法的话就执行下面的方法
                getattr(funcManage, func_name)()
            else:
                print(f"方法 {func_name} 不存在")



def run():
    print("欢迎来到李叶凯的网络交互系统".center(40))

    for i in MenuDictInfo:
        print(i,MenuDictInfo[i][0])

    Select = int(input("请选择主页面"))

    if Select in MenuDictInfo:
        eval(MenuDictInfo[Select][1])()  #取出函数后直接运行
    else:
        print("请重新选择,您输入的选项有错误！")
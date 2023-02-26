def singleton(cls):
    '''
    单例模式的装饰器
    ----------------------
    使用：
    @singleton \n
    class Cls(object):
        def __init__(self):
            pass

    cls1 = Cls() \n
    cls2 = Cls() \n
    print(id(cls1) == id(cls2)) # True
    '''
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner
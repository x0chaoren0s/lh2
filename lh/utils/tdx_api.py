from lh.utils.singleton_ import singleton
from pytdx.hq import TdxHq_API

@singleton
def get_tdx_api():
    '''
    返回一个单例 TdxHq_API 对象，已初始化成功连接
    
    用完后可使用 disconnect 方法断开连接
    '''
    tdx_api = TdxHq_API(heartbeat=True)
    tdx_ip = '119.147.212.81'
    tdx_port = 7709
    if not tdx_api.connect(tdx_ip, tdx_port):
        raise RuntimeError('通达信服务器连接失败。')
    print('tdx_api connected from get_tdx_api()')
    return tdx_api

def tdx_disconnect(btn=None, api=None, **args):
    '''断开由 get_tdx_api() 获取的api与通达信服务器的连接'''
    if api is None:
        api = get_tdx_api() # 单例
    api.disconnect()
    print('tdx_api disconnected from tdx_disconnect()')
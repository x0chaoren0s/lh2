def tscode2secid(ts_code):
    '''将tushare的ts_code(如000638.SZ)转换成东方财富的secid(如0.000638)'''
    return '0.'+ts_code[:-3] if ts_code[-2:]=='SZ' else '1.'+ts_code[:-3]
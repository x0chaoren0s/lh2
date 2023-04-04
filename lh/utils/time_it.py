

def time_it(func):
    import timeit
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        ret = func(*args, **kwargs)
        end = timeit.default_timer()
        print(f"{func.__name__}() 执行用时 {end-start:.8f}s")
        return ret
    return wrapper

@time_it
def demo(n):
    for _ in range(n):
        a=3.15

if __name__ == '__main__':
    demo(1000)
    # time_it((lambda n:[str(3.15) for _ in range(n)])(1000))
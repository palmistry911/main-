import asyncio
from functools import wraps
import hashlib


class Cache:
    def __init__(self):
        self.data = {}

    def generate_key(self, func_name, args, kwargs):
        key = f"{func_name}({args}, {kwargs})"
        return hashlib.md5(key.encode()).hexdigest()

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if func.__name__ not in self.data:
                self.data[func.__name__] = {}

            key = str(args) + str(kwargs)
            if key in self.data[func.__name__]:
                return self.data[func.__name__][key]

            ans = await func(*args, **kwargs)
            self.data[func.__name__][key] = ans
            return ans

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if func.__name__ not in self.data:
                self.data[func.__name__] = {}

            key = str(args) + str(kwargs)
            if key in self.data[func.__name__]:
                return self.data[func.__name__][key]

            ans = func(*args, **kwargs)
            self.data[func.__name__][key] = ans
            return ans

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def invalidate(self, func):
        if func.__name__ in self.data:
            del self.data[func.__name__]


cache = Cache()


@cache
def slow_function(arg):
    return arg


class MyClass:
    @cache
    def method(self, arg):
        return arg


@cache
async def async_func(arg):
    return arg

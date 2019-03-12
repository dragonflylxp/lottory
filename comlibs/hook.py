#coding=utf-8

from functools import wraps
from util.tools import Log

logger = Log().getLog()


class Hook(object):
    @classmethod
    def run(cls, target_function_list={}, ret=None, *input_args, **input_kwargs):
        for f_name, func in target_function_list.items():
            func(ret, *input_args, **input_kwargs)

    @classmethod
    def pre_hook(cls, name, condition=lambda *args, **kwargs: True):
        """前置挂钩点
        """
        target_f = getattr(cls, name, None)
        if target_f is None:
            setattr(cls, name, {})

        def _wrapper(f):
            @wraps(f)
            def __wrapper(*args, **kwargs):
                target_f = getattr(cls, name, None)
                if condition(*args, **kwargs):
                    cls.run(target_f, None, *args, **kwargs)
                ret = f(*args, **kwargs)
                return ret
            return __wrapper
        return _wrapper

    @classmethod
    def post_hook(cls, name, condition=lambda *args, **kwargs: True):
        """后置挂钩点
        """
        target_f = getattr(cls, name, None)
        if target_f is None:
            setattr(cls, name, {})

        def _wrapper(f):
            @wraps(f)
            def __wrapper(*args, **kwargs):
                target_f = getattr(cls, name, None)
                ret = f(*args, **kwargs)
                if condition(*args, **kwargs):
                    cls.run(target_f, ret, *args, **kwargs)
                return ret
            return __wrapper
        return _wrapper

    @classmethod
    def register_callback(cls, name):
        target_f = getattr(cls, name, None)
        if target_f is None:
            setattr(cls, name, {})

        def _wrapper(f):
            target_f = getattr(cls, name, None)
            target_f[f.func_name] = f

            @wraps(f)
            def __wrapper(*args, **kwargs):
                pass

            return __wrapper

        return _wrapper

import functools


def SingletonDecorator(cls):
    ins = dict()

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in ins:
            ins[cls] = cls(*args, **kwargs)
        return ins[cls]

    return get_instance


def global_init():
    global _global_dict

    _global_dict = dict()


def set_value(key, value):
    _global_dict[key] = value


def get_value(key, default=None):
    return _global_dict.get(key, default)

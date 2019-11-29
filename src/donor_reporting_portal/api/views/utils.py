import collections


def get_cache_key(args, **kwargs):
    joint_args = ''.join(args)
    order_dict = collections.OrderedDict(kwargs)
    return hash(joint_args) + hash(frozenset(order_dict.items()))

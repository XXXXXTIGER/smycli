# coding:utf8
from __future__ import print_function
import sys


def getfunctionbyname(module_name, function_name):
    '''import function from module'''
    origin_module_name = module_name
    try:

        module = __import__(module_name)
        if module_name.split('.').__len__() == 2:
            module_name = module_name.split('.')[1]
            module = getattr(module, module_name)
        return getattr(module, function_name)
    except ImportError:
        print('no module {a1} found'.format(a1=module_name))
        sys.exit(1)
    except AttributeError:
        print('"{a1}""  does not have function "{a2}"'.format(
            a1=origin_module_name, a2=function_name))
        sys.exit(1)


def failed(exception):
    print(exception.message)
    return 1

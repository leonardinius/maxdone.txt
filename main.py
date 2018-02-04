# coding=utf-8

import os
import sys

from maxdone import ApiV1, MaxdoneTxt

if __name__ == '__main__':
    api = ApiV1().login(os.environ['USERNAME'], os.environ['PASSWORD'])
    txt = MaxdoneTxt(api)
    txt.writeTo(out=sys.stdout)

# coding=utf-8

import json
import operator
import os
import re
import string
import sys
from operator import itemgetter

import html2text as html2text
import requests

from maxdone import ApiV1
from maxdone import MaxdoneTxt

if __name__ == '__main__':
    api = ApiV1().login(os.environ['USERNAME'], os.environ['PASSWORD'])
    txt = MaxdoneTxt(api)
    txt.writeTo()
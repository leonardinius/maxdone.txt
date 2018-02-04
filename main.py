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

from api import ApiV1
from todo import MaxdoneTxt

if __name__ == '__main__':
    api = ApiV1().login(os.environ['USERNAME'], os.environ['PASSWORD'])
    txt = MaxdoneTxt(api)
    txt.writeTo()
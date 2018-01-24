# coding=utf-8

import os
import json
import requests
import html2text as _html2text
import string
import re


def enable_loging():
    import logging
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def html2text(html):
    h = _html2text.HTML2Text()
    h.ignore_links = False
    return h.handle(html)


RE_PUNCTUATION = re.compile(r'[\s{}]+'.format(re.escape(string.punctuation)))


def _namify(name):
    if isinstance(name, str):
        cap = string.capwords(name.decode('utf-8'))
    else:
        cap = string.capwords(name)
    return ''.join(RE_PUNCTUATION.split(cap))


def projectify(name):
    return '+' + _namify(name)


def tagify(name):
    return '@' + _namify(name)


def prettyprint(jsondata):
    return json.dumps(jsondata,
                      ensure_ascii=False, encoding='utf-8',
                      sort_keys=True,
                      indent=4, separators=(',', ': '))


class ApiV1:
    json_headers = dict(
        {'Content-Type': 'application/json', 'Accept': 'application/json'})

    def __init__(self, base_uri='https://maxdone.micromiles.co'):
        self.base_uri = base_uri
        self.cookies = dict()

    def login(self, username, password):
        req = requests.post('{0}/services/j_spring_security_check'.format(self.base_uri), allow_redirects=False, data={
            '_spring_security_remember_me':	'on',
            'j_username':  username,
            'j_password': password,
            'spring-security-redirect': ''
        })
        req.raise_for_status()
        self.cookies = req.cookies
        return self

    def todos(self):
        req = requests.get(
            '{0}/services/v1/tasks/todo'.format(self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers)
        req.raise_for_status()
        return req.json()

    def completed(self, page, pagesize):
        req = requests.get(
            '{0}/services/v1/tasks/completed'.format(
                self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers,
            params={
                'size': pagesize,
                'page': page,
                'format': 'json'
            })
        req.raise_for_status()
        return req.json()

    def contexts(self):
        req = requests.get(
            '{0}/services/v1/user-contexts'.format(
                self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers)
        req.raise_for_status()
        return req.json()

    def categories(self):
        req = requests.get(
            '{0}/services/v1/tasks/projects'.format(
                self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers)
        req.raise_for_status()
        return req.json()

    def goals(self, page, pagesize):
        req = requests.get(
            '{0}/services/v1/private-goals/my'.format(
                self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers,
            params={
                'size': pagesize,
                'page': page,
                'format': 'json'
            })
        req.raise_for_status()
        return req.json()


def obj2dict(data):
    obj = {kv['id']: kv['title'] for kv in data}
    return obj


def uprint(s):
    if isinstance(s, unicode):
        print(s.encode('utf-8'))
    else:
        print(s)


if __name__ == '__main__':
    if 'HTTP_DEBUG' in os.environ:
        enable_loging()

    api = ApiV1().login(os.environ['USERNAME'], os.environ['PASSWORD'])

    uprint(prettyprint(obj2dict(api.todos())))
    uprint(prettyprint(obj2dict(api.completed(0, 10 ** 9)['content'])))

    tags_v1 = obj2dict(api.contexts())
    uprint(prettyprint(list(tagify(v) for k, v in tags_v1.iteritems())))

    tags_v2 = obj2dict(api.categories())
    uprint(prettyprint(list(tagify(v) for k, v in tags_v2.iteritems())))

    goals = obj2dict(api.goals(0, 10 ** 9)['content'])
    uprint(prettyprint(list(projectify(v) for k, v in goals.iteritems())))

    uprint(prettyprint('This is Это я задача'))

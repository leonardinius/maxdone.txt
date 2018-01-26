# coding=utf-8

import json
import os
import re
import signal
import SimpleHTTPServer
import SocketServer
import string
import sys
import threading

import html2text as _html2text
import requests


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


def obj2dict(data):
    obj = {kv['id']: kv['title'] for kv in data}
    return obj


def uprint(s):
    if isinstance(s, unicode):
        print(s.encode('utf-8'))
    else:
        print(s)


def prettydumps(jsondata):
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


class MaxdoneTxt:
    tags = {}
    projects = {}
    todo = {}
    done = {}

    def __init__(self, api):
        self.api = api

    def _merge(self, dict1, dict2):
        newdict = dict1.copy()
        newdict.update(dict2)
        return newdict

    def _tags(self):
        tags_v1 = obj2dict(self.api.contexts())
        tags_v2 = obj2dict(self.api.categories())
        self.tags = self._merge(tags_v1, tags_v2)
        return self.tags

    def _projects(self):
        goals = obj2dict(self.api.goals(0, 10 ** 9)['content'])
        self.projects = goals
        return self.projects

    def _todos(self):
        todos = self.api.todos()
        result = []
        for item in todos:
            obj = {
                "id" : item.get("id"), 
                "title" : item.get("title"), 
                "checklistItems":item.get("checklistItems"),
                "startDatetime": item.get("startDatetime"),
                "completionDate": item.get("completionDate"),
                "goalId": item.get("goalId"),
                "path": item.get("path"),
                "done": item.get("done")
                }
            result.append(obj)
        return result

    def _done(self):
        done = self.api.completed(0, 10 ** 9)['content']
        result = []
        for item in done:
            obj = {
                "id" : item.get("id"), 
                "title" : item.get("title"), 
                "checklistItems":item.get("checklistItems"),
                "startDatetime": item.get("startDatetime"),
                "completionDate": item.get("completionDate"),
                "goalId": item.get("goalId"),
                "path": item.get("path"),
                "done": item.get("done")
                }
            result.append(obj)
        return result


class HtmlLocalhostClient:
    def __init__(self, port=8000):
        self.port = port
        self.handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", port), self.handler)

    def serve_forever(self):
        self.httpd.serve_forever()


def signal_handler(signal, frame):
    uprint("\nYou pressed Ctrl+C!")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    if 'HTTP_DEBUG' in os.environ:
        enable_loging()

    api = ApiV1().login(os.environ['USERNAME'], os.environ['PASSWORD'])
    txt = MaxdoneTxt(api)

    uprint(prettydumps(txt._tags()))
    uprint(prettydumps(txt._projects()))
    uprint(prettydumps(txt._todos()))
    uprint(prettydumps(txt._done()))

    # server = HtmlLocalhostClient()
    # uprint(("The maxdone.txt client is running at http://127.0.0.1:{0}\n" +
    #         "Press Ctrl+C to exit." +
    #         "").format(server.port))
    # server.serve_forever()

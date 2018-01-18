import requests
import os


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


def prettyprint(jsondata):
    import json
    return json.dumps(jsondata, sort_keys=True,
                      indent=4, separators=(',', ': '))


class API:
    host_url = 'https://maxdone.micromiles.co'
    json_headers = dict({'Content-Type': 'application/json', 'Accept': 'application/json'})

    def __init__(self):
        self.cookies = dict()

    def login(self, username, password):
        req = requests.post('{0}/services/j_spring_security_check'.format(self.host_url), allow_redirects=False, data={
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
            '{0}/services/v1/tasks/todo'.format(self.host_url), cookies=self.cookies, headers=self.json_headers)
        req.raise_for_status()
        return req.json()

    def completed(self, page, pagesize):
        req = requests.get(
            '{0}/services/v1/tasks/completed'.format(
                self.host_url),
            cookies=self.cookies,
            headers=self.json_headers,
            params={
                'size': pagesize,
                'page': page,
                'format': 'json'
            })
        req.raise_for_status()
        return req.json()

    # https://maxdone.micromiles.co/services/v1/user-contexts?_=1516242861670
    # https://maxdone.micromiles.co/services/v1/private-goals/my?size=27&page=0&title=&mode=&statuses=canceled,postponed,not_started,in_progress,completed&format=json&_=1516242687474


if __name__ == '__main__':
    if 'HTTP_DEBUG' in os.environ:
        enable_loging()

    api = API().login(os.environ['USERNAME'], os.environ['PASSWORD'])
    print(prettyprint(api.todos()))
    print(prettyprint(api.completed(0, 10 ** 9)))

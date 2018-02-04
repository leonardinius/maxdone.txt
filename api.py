# coding=utf-8

import json
import requests


class ApiV1:
    json_headers = dict({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })

    def __init__(self, base_uri='https://maxdone.micromiles.co'):
        self.base_uri = base_uri
        self.cookies = dict()

    def login(self, username, password):
        req = requests.post(
            '{0}/services/j_spring_security_check'.format(self.base_uri),
            allow_redirects=False,
            data={
                '_spring_security_remember_me': 'on',
                'j_username': username,
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
            '{0}/services/v1/tasks/completed'.format(self.base_uri),
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
            '{0}/services/v1/user-contexts'.format(self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers)
        req.raise_for_status()
        return req.json()

    def categories(self):
        req = requests.get(
            '{0}/services/v1/tasks/projects'.format(self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers)
        req.raise_for_status()
        return req.json()

    def goals(self, page, pagesize):
        req = requests.get(
            '{0}/services/v1/private-goals/my'.format(self.base_uri),
            cookies=self.cookies,
            headers=self.json_headers,
            params={
                'size': pagesize,
                'page': page,
                'format': 'json'
            })
        req.raise_for_status()
        return req.json()

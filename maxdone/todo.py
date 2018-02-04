# coding=utf-8

import re
import string
import sys
from operator import itemgetter

import html2text as _html2text


def html2text(html):
    h = _html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(html)


RE_PUNCTUATION = re.compile(r'[\s{}]+'.format(re.escape(string.punctuation)))


def namify(name):
    if isinstance(name, str):
        cap = string.capwords(name.decode('utf-8'))
    else:
        cap = string.capwords(name)
    return ''.join(RE_PUNCTUATION.split(cap))


def projectify(name):
    return '+' + namify(name)


def tagify(name):
    return '@' + namify(name)


def uprint(s, out=sys.stdout):
    if isinstance(s, unicode):
        out.writelines(s.encode('utf-8'))
    else:
        out.writelines(s)


def _strip_spaces(item):
    item = re.sub(r'\s{2,}', ' ', item)
    item = item.strip()
    return item


def _merge(dict1, dict2):
    newdict = dict1.copy()
    newdict.update(dict2)
    return newdict


def _obj2dict(data):
    obj = {kv['id']: kv['title'] for kv in data}
    return obj


class MaxdoneTxt:
    tags = {}
    projects = {}
    todo = {}
    done = {}

    def __init__(self, api):
        self.api = api

    def _rawTags(self):
        tags_v1 = _obj2dict(self.api.contexts())
        tags_v2 = _obj2dict(self.api.categories())
        self.tags = _merge(tags_v1, tags_v2)
        return self.tags

    def _rawProjects(self):
        goals = _obj2dict(self.api.goals(0, 10**9)['content'])
        self.projects = goals
        return self.projects

    def _rawTodos(self):
        todos = self.api.todos()
        result = []
        for item in todos:
            obj = {
                'id': item.get('id'),
                'title': item.get('title'),
                'goalId': item.get('goalId'),
                'path': item.get('path'),
                'creationDatetime': item.get('ct'),
                'modifiedDatetime': item.get('mt'),
                'startDatetime': item.get('startDatetime'),
                'dueDate': item.get('dueDate'),
                'completionDate': item.get('completionDate'),
                'recurRule': item.get('recurRule'),
                'notes': item.get('notes'),
                'checklistItems': item.get('checklistItems', []),
                'priority': item.get('priority', 0),
                'done': item.get('done', False)
            }
            result.append(obj)
        result = sorted(result, key=itemgetter('priority'), reverse=True)
        return result

    def _rawDone(self):
        done = self.api.completed(0, 10**9)['content']
        result = []
        for item in done:
            obj = {
                'id': item.get('id'),
                'title': item.get('title'),
                'goalId': item.get('goalId'),
                'path': item.get('path'),
                'creationDatetime': item.get('ct'),
                'modifiedDatetime': item.get('mt'),
                'startDatetime': item.get('startDatetime'),
                'dueDate': item.get('dueDate'),
                'completionDate': item.get('completionDate'),
                'recurRule': item.get('recurRule'),
                'notes': item.get('notes'),
                'checklistItems': item.get('checklistItems', []),
                'priority': item.get('priority', 0),
                'done': item.get('done', True)
            }
            result.append(obj)
        return result

    def _uprint(self, ctx):
        h = lambda s: re.sub(r'[\r\n]+', ' ', html2text(s)).strip() if s else ''
        n = lambda s: h(s).encode('utf-8') if s else ''
        datef = lambda d: d.split('T')[0]
        out = []

        items = ctx['todos'] + ctx['done']
        for item in items:
            done = n('x' if item['done'] else '')
            completionDate = datef(n(item['completionDate']))
            creationDatetime = datef(n(
                item['creationDatetime'])) if completionDate else ''

            title = n(item['title'])

            notes = n(item['notes'])
            notes = 'Notes: ' + notes if notes else ''

            checklistItems = [
                '{0} {1}'.format('[x]' if check['done'] else '[ ]',
                                 n(check['title']))
                for check in item['checklistItems']
            ]
            checklistItems = '. '.join(checklistItems)
            checklistItems = 'Checklist: (' + checklistItems + ')' if checklistItems else ''

            goalId = item['goalId']
            projects = projectify(ctx['projects'][goalId]) if goalId else ''
            projects = n(projects)

            tagIds = item['path'].split(',')
            tags = [
                tagify(tag)
                for tag in [ctx['tags'].get(tagId, '') for tagId in tagIds]
                if tag
            ]
            tags = n(' '.join(tags))

            extrakv = ''
            extrakv = extrakv + ' due:' + datef(n(
                item['dueDate'])) if item['dueDate'] else extrakv
            extrakv = extrakv + ' recur:' + item['recurRule'] if item[
                'recurRule'] else extrakv

            out.append(
                _strip_spaces(
                    "{done} {completionDate} {creationDatetime} {title} {notes} {checklistItems} {projects} {tags} {extrakv}".
                    format(
                        **{
                            'done': done,
                            'completionDate': completionDate,
                            'creationDatetime': creationDatetime,
                            'title': title,
                            'notes': notes,
                            'checklistItems': checklistItems,
                            'projects': projects,
                            'tags': tags,
                            'extrakv': extrakv
                        })))
        return '\n'.join(out)

    def writeTo(self, out=sys.stdout):
        ctx = {
            'todos': self._rawTodos(),
            'projects': self._rawProjects(),
            'tags': self._rawTags(),
            'done': self._rawDone()
        }

        uprint(self._uprint(ctx), out)

import os, json
import sqlite3

from app import app

def setup_db(conn):
    statements = [
        "create table if not exists tool (node_id int primary key, name text, status int)",
        "create table if not exists permission (node_id int, timestamp datetime default (CURRENT_TIMESTAMP), card_id text, granter_card_id text, is_maintainer boolean default 0, primary key (node_id, card_id))",
        "create table if not exists tool_usage (node_id int, timestamp datetime default (CURRENT_TIMESTAMP), status int, card_id text)",
        "create table if not exists case_alert (node_id int, timestamp datetime default (CURRENT_TIMESTAMP), status int)",

        "create index if not exists tool_usage_index_by_time on tool_usage (node_id, timestamp)",
        "create index if not exists tool_usage_index_by_card on tool_usage (node_id, card_id)",
        "create index if not exists case_alert_index_by_time on case_alert (node_id, timestamp)",
        "insert or replace into tool (node_id, name, status) values (1, 'testtool', 1)",
        "insert or replace into permission (node_id, card_id, is_maintainer) values (1, 'abcde12345', 1)",
    ]

    c = conn.cursor()
    for s in statements:
        c.execute(s)
        conn.commit()
    print "Database initialized"

class CardTable(object):
    def __init__(self):
        self.cardFile = app.config.get('CARDFILE')
        self.mTime = None

    def reload(self):
        try:
            currentMtime = os.path.getmtime(self.cardFile)
        except IOError, e:
            app.logger.critical('Cannot read card file: %s', repr(e))
            raise

        if self.mTime != currentMtime:

            app.logger.debug('Loading card table, mtime %d', currentMtime)
            self.mTime = currentMtime
            self.cards = {}

            file = open(self.cardFile)

            users = json.load(file)
            perms = {}

            for user in users:
                for card in user['cards']:
                    card = card.encode('utf-8')
                    nick = user['nick'].encode('utf-8')
                    self.cards[card] = nick
                    perms[card] = user['perms']

            for node in app.nodes.values():
                node.updatePerms(perms)

            app.logger.info('Loaded %d cards', len(self.cards))

    # TODO: use inotify


class Node(object):
    def __init__(self, nodeid, perm):
        self.nodeid = nodeid
        self.perm = perm
        self.status = 1
        self.tooluse = 0
        self.case = 0

    def updatePerms(self, perms):
        self.perms = {}
        cards = []
        for card, userperms in perms.items():
            if self.perm in userperms:
                self.perms[card] = 1
                cards.append(card)
            if '%s-maintainer' % self.perm in userperms:
                self.perms[card] = 2

        print self.perms
        self.cards = sorted(self.perms.keys())

    def checkCard(self, uid):
        app.carddb.reload()
        return self.perms.get(uid, 0)

    def getCard(self, uid=None):
        if not uid:
            app.carddb.reload()
            index = 0
        else:
            # ValueError if unknown card
            index = self.cards.index(uid) + 1

        try:
            return self.cards[index]
        except IndexError, e:
            return None

    def addCard(self, uid):
        self.newperms[uid] = 1
        self.perms.update(self.newperms)
        # FIXME: insert permission into DB

def get_nodes():
    nodes = {}
    for nodeid, perm in app.config['NODEPERMS'].items():
        nodes[nodeid] = Node(nodeid, perm)
    return nodes

class Permission(object):
    pass





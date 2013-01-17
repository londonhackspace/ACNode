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

NOT_ALLOWED = 0
ALLOWED = 1
MAINTAINER = 2

def get_permission(conn, node_id, card_id):
    """
    Returns one of the three permission levels.
    """
    c = conn.cursor()
    c.execute(
        "select is_maintainer from permission where node_id = ? and card_id = ?",
        (node_id, card_id)
    )
    row = c.fetchone()
    if row is None:
        return NOT_ALLOWED
    if bool(row[0]):
        return MAINTAINER
    return ALLOWED


def set_permission(conn, node_id, card_id, granter_id, level):
    if level == NOT_ALLOWED:
        cmd = "delete from permission where node_id = ? and card_id = ?"
        params = (card_id, node_id)
    elif level == ALLOWED:
        cmd = "insert or replace into permission (node_id, card_id, granter_card_id) values (?, ?, ?)"
        params = (node_id, card_id, granter_id)
    elif level == MAINTAINER:
        cmd = "insert or replace into permission (node_id, card_id, granter_card_id, is_maintainer) values (?, ?, ?, 1)"
        params = (node_id, card_id, granter_id)
    else:
        raise ValueError("Invalid Permmison Level: %s" % level)
    conn.cursor().execute(cmd, params)
    conn.commit()


def get_next_card(conn, node_id, last_card_id):
    c = conn.cursor()
    if last_card_id is None:
        c.execute(
            "select card_id from permission where node_id = ? order by card_id limit 1",
            (node_id,)
        )
    else:
        c.execute(
            "select card_id from permission where node_id = ? and card_id > ? order by card_id limit 1",
            (node_id, last_card_id)
        )
    row = c.fetchone()
    if row is None:
        return None
    return row[0]


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
        self.status = 1
        self.tooluse = 0
        self.case = 0

    def checkCard(self, db, uid):
        return get_permission(db, self.nodeid, uid)

    def getCard(self, db, uid=None):
        return get_next_card(db, self.nodeid, uid)

    def addCard(self, db, uid, maintainer_uid):
        set_permission(db, self.nodeid, uid, maintainer_uid, ALLOWED)

def get_nodes():
    nodes = {}
    for nodeid, perm in app.config['NODEPERMS'].items():
        nodes[nodeid] = Node(nodeid, perm)
    return nodes

class Permission(object):
    pass





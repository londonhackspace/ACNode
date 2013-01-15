import os, json

from app import app

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





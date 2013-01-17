import re

from flask import request, Blueprint, render_template, abort, g
from werkzeug.exceptions import NotFound

from app import app

nodes = Blueprint('nodes', __name__, url_prefix='/<int:node>')

@nodes.url_value_preprocessor
def check_node(endpoint, values):
    try:
        request.nodeid = values.pop('node')
        request.node = app.nodes[request.nodeid]
    except KeyError:
        raise NotFound


@nodes.route('/status', methods=['GET', 'PUT'])
def status():
    if request.method == 'PUT':
        status = request.data
        if status not in ('1', '0'):
            return 'Invalid status', 400

        request.node.status = status
        return 'OK'

    else:
        return str(request.node.status)


@nodes.route('/tooluse', methods=['GET', 'PUT'])
def tooluse():
    if request.method == 'GET':
        return str(request.node.tooluse)

    m = re.match('^([0-9]+),([A-Z0-9]+)$', request.data)
    if not m:
        return 'Invalid arguments', 400

    tooluse, uid = m.groups()
    access = node.checkCard(uid)

    if not access:
        abort(403)

    if tooluse in ('1', '0'):
        request.node.tooluse = int(tooluse)
        return 'OK'


@nodes.route('/tooluse/time/', methods=['GET'])
def get_tool_time():
    pass

@nodes.route('/tooluse/time/', methods=['POST'])
def add_tool_time():

    if request.headers['Content-type'] == 'text/plain':
        m = re.match('^([0-9]+),([A-Z0-9]+)$', request.data)
        if not m:
            return 'Invalid content', 400

        tooluse, uid = m.groups()

    else:
        abort(415)

    access = request.node.checkCard(uid)
    if not access:
        abort(403)

    if tooluse not in ('1', '0'):
        return 'Invalid tooluse', 400

    request.node.tooluse = int(tooluse)
    return 'OK'


@nodes.route('/case', methods=['GET', 'PUT'])
def case():
    if request.method == 'GET':
        return str(request.node.case)

    case = request.data
    if case not in ('1', '0'):
        return 'Invalid case', 400

    request.node.case = int(case)
    return 'OK'


@nodes.route('/card/<uid>', methods=['GET', 'POST'])
def card(uid):
    if request.method == 'GET':
        access = request.node.checkCard(g.db, uid)
        return str(access)

    granter_uid = request.data
    granter_access = request.node.checkCard(g.db, granter_uid)
    if granter_access != 2:
        abort(403)

    user_access = request.node.checkCard(g.db, uid)
    if user_access: # no change
        return 'OK (was %s)' % user_access

    else:
        request.node.addCard(g.db, uid, granter_uid)
        return 'OK', 201


@nodes.route('/sync/')
@nodes.route('/sync/<from_uid>')
def sync(from_uid=None):
    json, text, html = 'application/json', 'text/plain', 'text/html'
    # In order of preference
    best_match = request.accept_mimetypes.best_match([html, json, text])
    if not best_match:
        return not_acceptable

    # If no DB, return 204

    if best_match == text:
        next_card = request.node.getCard(g.db, from_uid)
        if not next_card:
            return 'END'
        # this used to return response 206, but that's doesn't really
        # satisfy the http specification.
        # is there any reason not to return all the cards at once here?
        return next_card

    elif best_match == json:
        card = request.node.card
        return jsonify(cards)

    else:
        return render_template('cards.html', cards=request.node.cards)



import re

from flask import request, Blueprint, render_template, abort
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
        m = re.match('^([0-9]+),([A-Z0-9]+)$', request.data.strip())
        if not m:
            return 'Invalid content', 400

        tooluse, uid = m.groups()

    else:
        abort(415)

    access = request.node.checkCard(uid)
    if not access:
        abort(403)

    if tooluse.strip() not in ('1', '0'):
        return 'Invalid tooluse', 400

    request.node.tooluse = int(tooluse)
    return 'OK'


@nodes.route('/case', methods=['GET', 'PUT'])
def case():
    if request.method == 'GET':
        return str(request.node.case)

    case = request.data.strip()
    if case not in ('1', '0'):
        return 'Invalid case', 400

    request.node.case = int(case)
    return 'OK'


@nodes.route('/card/<uid>', methods=['GET', 'POST'])
def card(uid):
    if request.method == 'GET':
        access = request.node.checkCard(uid)
        return str(access)

    maintainer_uid = request.data
    maintainer_access = request.node.checkCard(maintainer_uid)
    if maintainer_access < 2:
        abort(403)

    user_access = request.node.checkCard(user_uid)
    if user_access: # no change
        return 'OK (was %s)' % user_access

    else:
        request.node.addCard(user_uid)
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
        next = request.node.getCard(from_uid)
        if not next:
            return 'END'
        return next, 206

    elif best_match == json:
        card = request.node.card
        return jsonify(cards)

    else:
        return render_template('cards.html', cards=request.node.cards)



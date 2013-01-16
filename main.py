#!/usr/bin/env python

import logging
import sqlite3

from flask import make_response, g
from werkzeug.exceptions import default_exceptions, HTTPException

from app import app
from carddb import get_nodes, CardTable, setup_db
from logutil import set_default_format, add_context_filter

def connect_db():
    return sqlite3.connect(app.config.get('DB_FILE'))

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db')
    if db:
        db.close()

logging.basicConfig(level=logging.NOTSET)
logging.info('Starting ACNode')

app.config.from_envvar('SETTINGS_FILE')

app.debug_log_format = '' # it's a bit intrusive
set_default_format(app, '%(levelname)s:%(name)s:%(node)s:%(message)s')
add_context_filter(app, node=lambda ctx: ctx.request.nodeid)

def text_error_handler(e):
    response = make_response(str(e), 500)
    if isinstance(e, HTTPException):
        response.status_code = e.code
    return response

for code in default_exceptions:
    app.error_handler_spec[None][code] = text_error_handler

with connect_db() as db:
    setup_db(db)

app.nodes = get_nodes()
app.carddb = CardTable()
app.carddb.reload()

@app.route('/')
def home():
    return 'http://hack.rs/p/ACNode'


if __name__ == "__main__":
    app.run(port=app.config['TCPPORT'])


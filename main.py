#!/usr/bin/env python

import logging

from flask import make_response
from werkzeug.exceptions import default_exceptions, HTTPException

from app import app
from carddb import get_nodes, CardTable
from logutil import set_default_format, add_context_filter


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

app.nodes = get_nodes()
app.carddb = CardTable()
app.carddb.reload()

@app.route('/')
def home():
    return 'http://hack.rs/p/ACNode'


if __name__ == "__main__":
    app.run(port=app.config['TCPPORT'])


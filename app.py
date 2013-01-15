from flask import Flask

app = Flask(__name__)

from nodes import nodes

app.register_blueprint(nodes)

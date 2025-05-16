from flask import Flask

app = Flask(__name__)

from quiz_backend import routes  
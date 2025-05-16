from flask import render_template
from quiz_backend import app


@app.route('/')
def index():
    msg='user'
    return render_template('index.html', var1=msg)
from flask import Flask
from flask_globals import gramm

app = Flask(__name__)



@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/word/<word>')
def show_word(word):
    ret = ""
    if word in gramm:
        for f in gramm[word]:
            ret += "{}<br/>".format(f)
        return ret
    else:
        return 'mot inconnu'

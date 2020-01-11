from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return f"Hello World"


@app.route('/upload')
def upload():
    return render_template('templates/upload.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

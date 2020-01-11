from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return f"Hello World"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

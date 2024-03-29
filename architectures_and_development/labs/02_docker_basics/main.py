import os

from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/')
def hello():
    redis.incr('hits')
    counter = str(redis.get('hits'), 'utf-8')
    return f"This is {os.environ.get('USER')}'s webpage. It has been viewed {counter} time(s)"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="9000", debug=True)

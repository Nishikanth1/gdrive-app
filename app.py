import logging
import sys 

from flask import Flask

app = Flask(__name__)

app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)
logger = app.logger

@app.route('/healthcheck')
def hello_world():
    return 'App is up and running'

@app.route('/v1/list')
def list_files():
    return 'API WIP'

if __name__ == '__main__':
    app.run(debug = True)

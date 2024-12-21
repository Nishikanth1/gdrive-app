from flask import Flask

app = Flask(__name__)

@app.route('/healthcheck')
def hello_world():
    return 'App is up and running'

@app.route('/v1/list')
def list_files():
    return 'API WIP'

if __name__ == '__main__':
    app.run(debug = True)

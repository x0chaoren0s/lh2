import flask, os
from blueprints.huice import huice_bp

app = flask.Flask(__name__)
app.register_blueprint(huice_bp)

@app.route('/')
def index():
    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run()
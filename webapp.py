import flask, os, json
from blueprints.huice import huice_bp

app = flask.Flask(__name__)
app.register_blueprint(huice_bp)

@app.template_filter('json')
def my_to_json(string):
    return json.loads(string)

@app.route('/')
def index():
    # return flask.render_template('test.html')
    index=['2017-10-24', '2017-10-25', '2017-10-26', '2017-10-27']
    data=[
        [20, 34, 10, 38],
        [40, 35, 30, 50],
        [31, 38, 33, 44],
        [38, 15, 5, 42]
      ]
    insert1=flask.render_template('candles.html',chart_id='main',index=index,data=data)
    insert2=flask.render_template('candles.html',chart_id='main2')
    # return flask.render_template('index.html',insert1=insert1,insert2=insert2)
    return flask.render_template('index.html',insert2=insert2, insert1=insert1)


if __name__ == '__main__':
    app.run()
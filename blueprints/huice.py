import flask

huice_bp = flask.Blueprint(name='huice', import_name=__name__, url_prefix='/huice')

class T:
    def __init__(self) -> None:
        vb='1'
        ve='2'
t=T()

@huice_bp.route('/2ban')
def huice_2ban():
    return flask.render_template('huice/2ban.html')
@huice_bp.route('/2ban/set_time_span', methods=['POST'])
def huice_2ban_set_time_span():
    print('in set_time_span')
    print(flask.request.form.get('trade_time_beg'))
    return flask.render_template('huice/2ban.html')
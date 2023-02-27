import flask
from lh import Engine_2ban, SingleStock_daily, AllStock_daily

huice_bp = flask.Blueprint(name='huice', import_name=__name__, url_prefix='/huice')

e = Engine_2ban()

@huice_bp.route('/2ban', methods=['GET', 'POST'])
def huice_2ban():
    return flask.render_template('huice/2ban_setting.html')
@huice_bp.route('/2ban/set_time_span', methods=['POST'])
def huice_2ban_set_time_span():
    print('in set_time_span')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    if e.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end):
        return flask.redirect('/huice/2ban/working')
    else:
        return flask.redirect('/huice/2ban')
@huice_bp.route('/2ban/working')
def huice_2ban_working():
    daily_pool_tscode_list = AllStock_daily().get_least_2bans_list(trade_date=e.trade_date)
    daily_pool_dict_list = []
    for ts_code in daily_pool_tscode_list:
        # stk_dict = {'ts_code': ts_code}
        # stk_dict['ts_name'] = SingleStock_daily().getName()
        stk_dict = SingleStock_daily().getInfo(ts_code=ts_code, trade_date=e.trade_date, 
                                               need_tags=True, need_candles_day_df=True)
        stk_dict['candles_day_df'] = stk_dict['candles_day_df'].iloc[-15:].reset_index(drop=True)
        stk_dict['candles_day_index'] = stk_dict['candles_day_df']['trade_date'].tolist()
        stk_dict['candles_day_data'] = [
                                        [stk_dict['candles_day_df'].iloc[i]['open'],
                                         stk_dict['candles_day_df'].iloc[i]['close'],
                                         stk_dict['candles_day_df'].iloc[i]['low'],
                                         stk_dict['candles_day_df'].iloc[i]['high']]
                                    for i in stk_dict['candles_day_df'].index]
        stk_dict['candles_html'] = flask.render_template('candles.html',chart_id=ts_code,
                                                         index=stk_dict['candles_day_index'],
                                                         data=stk_dict['candles_day_data'])
        daily_pool_dict_list.append(stk_dict)
    return flask.render_template('huice/2ban_working.html',
                                 beg_date=e.beg_date, end_date=e.end_date,
                                 trade_date=e.trade_date,
                                 daily_pool=daily_pool_dict_list)
@huice_bp.route('/2ban/working/choosing', methods=['POST'])
def huice_2ban_working_choosing():
    buy_hands_list = flask.request.form.getlist('buy_hands')
    pass
    e.move_on()
    return flask.redirect('/huice/2ban/working')
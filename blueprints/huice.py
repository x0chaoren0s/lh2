import flask, json
from lh import Engine_2ban, SingleStock_daily, AllStock_daily
from lh.utils.tdx_df_fetcher import Tdx_df_fetcher

huice_bp = flask.Blueprint(name='huice', import_name=__name__, url_prefix='/huice')

e = Engine_2ban()
tf = Tdx_df_fetcher()

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
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        stk_dict['candles_html'] = flask.render_template('candles.html',
                                                         chart_id='daily_candles_'+ts_code,
                                                         index=stk_dict['candles_day_index'],
                                                         data=stk_dict['candles_day_data'])
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e.trade_date).close.tolist()[0]
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    end_pool_dict_list = []
    for ts_code, vol in e.dayStamps[e.trade_date].end_tscode2vol_dict.items():
        stk_dict = SingleStock_daily().getInfo(ts_code=ts_code, trade_date=e.trade_date, 
                                               need_tags=True, need_candles_day_df=True)
        stk_dict['have_vol'] = vol
        stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e.trade_date).close.tolist()[0]
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        stk_dict['candles_day_df'] = stk_dict['candles_day_df'].iloc[-15:].reset_index(drop=True)
        stk_dict['candles_day_index'] = stk_dict['candles_day_df']['trade_date'].tolist()
        stk_dict['candles_day_data'] = [
                                        [stk_dict['candles_day_df'].iloc[i]['open'],
                                         stk_dict['candles_day_df'].iloc[i]['close'],
                                         stk_dict['candles_day_df'].iloc[i]['low'],
                                         stk_dict['candles_day_df'].iloc[i]['high']]
                                    for i in stk_dict['candles_day_df'].index]
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        stk_dict['candles_html'] = flask.render_template('candles.html',
                                                         chart_id='end_candles_'+ts_code,
                                                         index=stk_dict['candles_day_index'],
                                                         data=stk_dict['candles_day_data'])
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        end_pool_dict_list.append(stk_dict)
    return flask.render_template('huice/2ban_working.html',
                                 beg_date=e.beg_date, end_date=e.end_date,
                                 trade_date=e.trade_date,
                                 end_total=e.dayStamps[e.trade_date].end_total,
                                 end_cash=e.dayStamps[e.trade_date].end_cash,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/2ban/working/choosing', methods=['POST'])
def huice_2ban_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }

    pass
    e.move_on(buy_form_dict=buy_form_dict)
    return flask.redirect('/huice/2ban/working')
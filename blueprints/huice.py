import flask, json, random
from lh import Engine_2ban, Engine_2ban_dixi, Engine_1ban_dixi, Engine_weipandieting, Engine_wencai, SingleStock_daily, AllStock_daily
from lh.utils.tdx_df_fetcher import Tdx_df_fetcher
from lh.utils.dongcai_df_fetcher import Dongcai_df_fetcher
import lh.stockinfo.data_fetcher as df
from lh.time import Trade_time

import wencai as wc

import pandas as pd

from tqdm import tqdm

huice_bp = flask.Blueprint(name='huice', import_name=__name__, url_prefix='/huice')

e = Engine_2ban()
e_2d = Engine_2ban_dixi()
e_1d = Engine_1ban_dixi()
e_wp = Engine_weipandieting()
e_wc = Engine_wencai()
# tf = Tdx_df_fetcher()
# ddf = Dongcai_df_fetcher()
tf = df
ddf = df
tt = Trade_time()

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
    daily_pool_tscode_list = AllStock_daily().get_least_2bans_list(trade_date=e.trade_date, sort=True, only_hs=True)
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
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
    print(f'end_tscode2vol_dict len: {len(e.dayStamps[e.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e.dayStamps[e.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        stk_dict['have_vol'] = vol
        stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e.trade_date).close.tolist()[0]
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        end_pool_dict_list.append(stk_dict)
    
    account_data = {
        'trade_date': list(e.dayStamps.keys()),
        'totals': [ds.end_total for ds in e.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    return flask.render_template('huice/2ban_working.html',
                                 beg_date=e.beg_date, end_date=e.end_date,
                                 trade_date=e.trade_date,
                                 end_total=e.dayStamps[e.trade_date].end_total,
                                 end_cash=e.dayStamps[e.trade_date].end_cash,
                                 account_lines_html=account_lines_html,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/2ban/working/choosing', methods=['POST'])
def huice_2ban_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
    }
    pass
    e.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict)
    return flask.redirect('/huice/2ban/working')


@huice_bp.route('/2ban_dixi', methods=['GET', 'POST'])
def huice_2ban_dixi():
    return flask.render_template('huice/2ban_dixi_setting.html')
@huice_bp.route('/2ban_dixi/set_time_span', methods=['POST'])
def huice_2ban_dixi_set_time_span():
    print('in set_time_span')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    if e_2d.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end):
        return flask.redirect('/huice/2ban_dixi/working')
    else:
        return flask.redirect('/huice/2ban_dixi')
@huice_bp.route('/2ban_dixi/working')
def huice_2ban_dixi_working():

    end_pool_dict_list = []
    print(f'end_tscode2vol_dict len: {len(e_2d.dayStamps[e_2d.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e_2d.dayStamps[e_2d.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_2d.dayTags[e_2d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        stk_dict['have_vol'] = vol
        try:
            stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_2d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_2d.trade_date}'
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_2d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_2d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_2d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_2d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        end_pool_dict_list.append(stk_dict)
    
    daily_pool_tscode_list = AllStock_daily().get_least_2bans_list(trade_date=e_2d.trade_date, sort=True, only_hs=True)
    remain_pool = list(set(e_2d.dayStamps[e_2d.trade_date].meta_dict.get('dixi_track_tscode_list',[]))-set(daily_pool_tscode_list))
    daily_pool_tscode_list.extend(random.sample(list(remain_pool), min(len(remain_pool),10))) # 最多保留10个非板待观察
    daily_pool_tscode_list = [ts_code for ts_code in daily_pool_tscode_list if ts_code not in e_2d.dayStamps[e_2d.trade_date].end_tscode2vol_dict.keys()]
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_2d.dayTags[e_2d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_2d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_2d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_2d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_2d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    
    account_data = {
        'trade_date': list(e_2d.dayStamps.keys()),
        'totals': [ds.end_total for ds in e_2d.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e_2d.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    # end_tags = sorted(list(e_2d.dayTags[e_2d.trade_date]['end_tags2count_dict'].items()),
    #                   key=lambda tag_count:tag_count[1], reverse=True)
    end_tags = dict()
    for tag,count in e_2d.dayTags[e_2d.trade_date]['end_tags2count_dict'].items():
        end_tags.setdefault(count, [])
        end_tags[count].append(tag)
    end_tags = sorted(list(end_tags.items()), key=lambda i:i[0], reverse=True)
    # end_tags = '\n'.join([str(ti).replace("[","").replace("]","").replace("'","") for ti in end_tags])
    return flask.render_template('huice/2ban_dixi_working.html',
                                 beg_date=e_2d.beg_date, end_date=e_2d.end_date,
                                 trade_date=e_2d.trade_date,
                                 end_total=e_2d.dayStamps[e_2d.trade_date].end_total,
                                 end_cash=e_2d.dayStamps[e_2d.trade_date].end_cash,
                                 account_lines_html=account_lines_html,
                                 end_tags = end_tags,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/2ban_dixi/working/choosing', methods=['POST'])
def huice_2ban_dixi_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
    }
    dixi_tscode_from_sell_list = flask.request.form.getlist('dixi_tscode_from_sell')
    dixi_choice_from_sell_list = [flask.request.form.get(f'dixi_from_sell_{tscode}') for tscode in dixi_tscode_from_sell_list]
    dixi_tscode_from_buy_list = flask.request.form.getlist('dixi_tscode_from_buy')
    dixi_choice_from_buy_list = [flask.request.form.get(f'dixi_from_buy_{tscode}') for tscode in dixi_tscode_from_buy_list]
    dixi_track_dict = {
        'dixi_track_tscode_list' : list(
                set([tscode for tscode,choice in zip(dixi_tscode_from_sell_list,dixi_choice_from_sell_list) if choice=='yes']) | \
                set([tscode for tscode,choice in zip(dixi_tscode_from_buy_list,dixi_choice_from_buy_list) if choice=='yes'])
            )
    }
    pass
    e_2d.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict, meta_dict=dixi_track_dict)
    return flask.redirect('/huice/2ban_dixi/working')


@huice_bp.route('/1ban_dixi', methods=['GET', 'POST'])
def huice_1ban_dixi():
    return flask.render_template('huice/1ban_dixi_setting.html')
@huice_bp.route('/1ban_dixi/set_time_span', methods=['POST'])
def huice_1ban_dixi_set_time_span():
    print('in set_time_span')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    if e_1d.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end):
        return flask.redirect('/huice/1ban_dixi/working')
    else:
        return flask.redirect('/huice/1ban_dixi')
@huice_bp.route('/1ban_dixi/working')
def huice_1ban_dixi_working():

    end_pool_dict_list = []
    print(f'end_tscode2vol_dict len: {len(e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        stk_dict['have_vol'] = vol
        try:
            stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_1d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_1d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        end_pool_dict_list.append(stk_dict)
    
    # daily_pool_tscode_list = AllStock_daily().get_least_2bans_list(trade_date=e_1d.trade_date, sort=True, only_hs=True)
    daily_pool_tscode_list = AllStock_daily().getLimitUps(trade_date=e_1d.trade_date, sort=True, only_hs=True)
    remain_pool = list(set(e_1d.dayStamps[e_1d.trade_date].meta_dict.get('dixi_track_tscode_list',[]))-set(daily_pool_tscode_list))
    daily_pool_tscode_list.extend(random.sample(list(remain_pool), min(len(remain_pool),10))) # 最多保留10个非板待观察
    daily_pool_tscode_list = [ts_code for ts_code in daily_pool_tscode_list if ts_code not in e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict.keys()]
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_1d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_1d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    
    account_data = {
        'trade_date': list(e_1d.dayStamps.keys()),
        'totals': [ds.end_total for ds in e_1d.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e_1d.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    # end_tags = sorted(list(e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'].items()),
    #                   key=lambda tag_count:tag_count[1], reverse=True)
    change=e_1d.dayStamps[e_1d.trade_date].end_total - e_1d.dayStamps[e_1d.trade_date].start_total
    chg_pct=change/e_1d.dayStamps[e_1d.trade_date].start_total
    end_tags = dict()
    for tag,count in e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'].items():
        end_tags.setdefault(count, [])
        end_tags[count].append(tag)
    end_tags = sorted(list(end_tags.items()), key=lambda i:i[0], reverse=True)
    # end_tags = '\n'.join([str(ti).replace("[","").replace("]","").replace("'","") for ti in end_tags])
    return flask.render_template('huice/1ban_dixi_working.html',
                                 beg_date=e_1d.beg_date, end_date=e_1d.end_date,
                                 trade_date=e_1d.trade_date,
                                 end_total=e_1d.dayStamps[e_1d.trade_date].end_total,
                                 end_cash=e_1d.dayStamps[e_1d.trade_date].end_cash,
                                 change=f'{change:.1f}',
                                 chg_pct=f'{chg_pct:.2f}',
                                 account_lines_html=account_lines_html,
                                 end_tags = end_tags,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/1ban_dixi/working/choosing', methods=['POST'])
def huice_1ban_dixi_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
    }
    dixi_tscode_from_sell_list = flask.request.form.getlist('dixi_tscode_from_sell')
    dixi_choice_from_sell_list = [flask.request.form.get(f'dixi_from_sell_{tscode}') for tscode in dixi_tscode_from_sell_list]
    dixi_tscode_from_buy_list = flask.request.form.getlist('dixi_tscode_from_buy')
    dixi_choice_from_buy_list = [flask.request.form.get(f'dixi_from_buy_{tscode}') for tscode in dixi_tscode_from_buy_list]
    dixi_track_dict = {
        'dixi_track_tscode_list' : list(
                set([tscode for tscode,choice in zip(dixi_tscode_from_sell_list,dixi_choice_from_sell_list) if choice=='yes']) | \
                set([tscode for tscode,choice in zip(dixi_tscode_from_buy_list,dixi_choice_from_buy_list) if choice=='yes'])
            )
    }
    pass
    e_1d.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict, meta_dict=dixi_track_dict)
    return flask.redirect('/huice/1ban_dixi/working')


    daily_pool_tscode_list = AllStock_daily().get_least_2bans_list(trade_date=e.trade_date)
    daily_pool_dict_list = []
    for ts_code in daily_pool_tscode_list:
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



@huice_bp.route('/liudongxing', methods=['GET', 'POST'])
def huice_liudongxing():
    return flask.render_template('huice/liudongxing_setting.html')
@huice_bp.route('/liudongxing/set_time_span', methods=['POST'])
def huice_liudongxing_set_time_span():
    print('in set_time_span')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    if e_1d.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end):
        return flask.redirect('/huice/liudongxing/working')
    else:
        return flask.redirect('/huice/liudongxing')
@huice_bp.route('/liudongxing/working')
def huice_liudongxing_working():

    end_pool_dict_list = []
    print(f'end_tscode2vol_dict len: {len(e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        stk_dict['have_vol'] = vol
        try:
            stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_1d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_1d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        end_pool_dict_list.append(stk_dict)
    
    daily_pool_tscode_list = AllStock_daily().getFakeLimitUps(trade_date=e_1d.trade_date, sort=True)
    remain_pool = list(set(e_1d.dayStamps[e_1d.trade_date].meta_dict.get('dixi_track_tscode_list',[]))-set(daily_pool_tscode_list))
    # remain_pool = sorted(remain_pool, key=lambda tscode: SingleStock_daily().numLimitedUps(tscode,list(e_1d.dayStamps.keys())[-2]))
    # daily_pool_tscode_list.extend(random.sample(list(remain_pool), min(len(remain_pool),10))) # 最多保留10个非板待观察
    daily_pool_tscode_list.extend(remain_pool)
    daily_pool_tscode_list = [ts_code for ts_code in daily_pool_tscode_list if ts_code not in e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict.keys()]
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_1d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_1d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    
    account_data = {
        'trade_date': list(e_1d.dayStamps.keys()),
        'totals': [ds.end_total for ds in e_1d.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e_1d.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    # end_tags = sorted(list(e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'].items()),
    #                   key=lambda tag_count:tag_count[1], reverse=True)
    change=e_1d.dayStamps[e_1d.trade_date].end_total - e_1d.dayStamps[e_1d.trade_date].start_total
    chg_pct=change/e_1d.dayStamps[e_1d.trade_date].start_total
    end_tags = dict()
    for tag,count in e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'].items():
        end_tags.setdefault(count, [])
        end_tags[count].append(tag)
    end_tags = sorted(list(end_tags.items()), key=lambda i:i[0], reverse=True)
    # end_tags = '\n'.join([str(ti).replace("[","").replace("]","").replace("'","") for ti in end_tags])
    return flask.render_template('huice/liudongxing_working.html',
                                 beg_date=e_1d.beg_date, end_date=e_1d.end_date,
                                 trade_date=e_1d.trade_date,
                                 end_total=e_1d.dayStamps[e_1d.trade_date].end_total,
                                 end_cash=e_1d.dayStamps[e_1d.trade_date].end_cash,
                                 change=f'{change:.1f}',
                                 chg_pct=f'{chg_pct*100:.2f}',
                                 account_lines_html=account_lines_html,
                                 end_tags = end_tags,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/liudongxing/working/choosing', methods=['POST'])
def huice_liudongxing_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
    }
    dixi_tscode_from_sell_list = flask.request.form.getlist('dixi_tscode_from_sell')
    dixi_choice_from_sell_list = [flask.request.form.get(f'dixi_from_sell_{tscode}') for tscode in dixi_tscode_from_sell_list]
    dixi_tscode_from_buy_list = flask.request.form.getlist('dixi_tscode_from_buy')
    dixi_choice_from_buy_list = [flask.request.form.get(f'dixi_from_buy_{tscode}') for tscode in dixi_tscode_from_buy_list]
    dixi_track_dict = {
        'dixi_track_tscode_list' : list(
                set([tscode for tscode,choice in zip(dixi_tscode_from_sell_list,dixi_choice_from_sell_list) if choice=='yes']) | \
                set([tscode for tscode,choice in zip(dixi_tscode_from_buy_list,dixi_choice_from_buy_list) if choice=='yes'])
            )
    }
    pass
    e_1d.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict, meta_dict=dixi_track_dict)
    return flask.redirect('/huice/liudongxing/working')


    daily_pool_tscode_list = AllStock_daily().get_least_2bans_list(trade_date=e.trade_date)
    daily_pool_dict_list = []
    for ts_code in daily_pool_tscode_list:
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



@huice_bp.route('/liudongxing_3ptr', methods=['GET', 'POST'])
def huice_liudongxing_3ptr():
    return flask.render_template('huice/liudongxing_3ptr_setting.html')
@huice_bp.route('/liudongxing_3ptr/set_time_span', methods=['POST'])
def huice_liudongxing_3ptr_set_time_span():
    print('in set_time_span')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    if e_1d.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end):
        return flask.redirect('/huice/liudongxing_3ptr/working')
    else:
        return flask.redirect('/huice/liudongxing_3ptr')
@huice_bp.route('/liudongxing_3ptr/working')
def huice_liudongxing_3ptr_working():

    end_pool_dict_list = []
    print(f'end_tscode2vol_dict len: {len(e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        stk_dict['have_vol'] = vol
        try:
            stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_1d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_1d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        end_pool_dict_list.append(stk_dict)
    
    daily_pool_tscode_list = AllStock_daily().get_least_k_ptr_list(k=3, date=e_1d.trade_date, sort=True)
    remain_pool = list(set(e_1d.dayStamps[e_1d.trade_date].meta_dict.get('dixi_track_tscode_list',[]))-set(daily_pool_tscode_list))
    remain_pool = sorted(remain_pool, key=lambda tscode: SingleStock_daily().numLimitedUps(tscode,list(e_1d.dayStamps.keys())[-2]))
    # daily_pool_tscode_list.extend(random.sample(list(remain_pool), min(len(remain_pool),10))) # 最多保留10个非板待观察
    daily_pool_tscode_list.extend(remain_pool)
    daily_pool_tscode_list = [ts_code for ts_code in daily_pool_tscode_list if ts_code not in e_1d.dayStamps[e_1d.trade_date].end_tscode2vol_dict.keys()]
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_1d.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_1d.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_1d.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_1d.trade_date}'
        buy_price = close*1.1-0.11 if 'ST' not in stk_dict['ts_name'] \
            else close*1.05-0.11 if 0.11<close*0.05 \
            else close*1.05-0.05 if 0.05<close*0.05 \
            else close*1.05-0.01
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    
    account_data = {
        'trade_date': list(e_1d.dayStamps.keys()),
        'totals': [ds.end_total for ds in e_1d.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e_1d.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    # end_tags = sorted(list(e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'].items()),
    #                   key=lambda tag_count:tag_count[1], reverse=True)
    change=e_1d.dayStamps[e_1d.trade_date].end_total - e_1d.dayStamps[e_1d.trade_date].start_total
    chg_pct=change/e_1d.dayStamps[e_1d.trade_date].start_total
    end_tags = dict()
    for tag,count in e_1d.dayTags[e_1d.trade_date]['end_tags2count_dict'].items():
        end_tags.setdefault(count, [])
        end_tags[count].append(tag)
    end_tags = sorted(list(end_tags.items()), key=lambda i:i[0], reverse=True)
    # end_tags = '\n'.join([str(ti).replace("[","").replace("]","").replace("'","") for ti in end_tags])
    return flask.render_template('huice/liudongxing_3ptr_working.html',
                                 beg_date=e_1d.beg_date, end_date=e_1d.end_date,
                                 trade_date=e_1d.trade_date,
                                 end_total=e_1d.dayStamps[e_1d.trade_date].end_total,
                                 end_cash=e_1d.dayStamps[e_1d.trade_date].end_cash,
                                 change=f'{change:.1f}',
                                 chg_pct=f'{chg_pct*100:.2f}',
                                 account_lines_html=account_lines_html,
                                 end_tags = end_tags,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/liudongxing_3ptr/working/choosing', methods=['POST'])
def huice_liudongxing_3ptr_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_type_list' : [flask.request.form.get(f'sell_type_{tscode}') for tscode in flask.request.form.getlist('sell_tscode')]
    }
    dixi_tscode_from_sell_list = flask.request.form.getlist('dixi_tscode_from_sell')
    dixi_choice_from_sell_list = [flask.request.form.get(f'dixi_from_sell_{tscode}') for tscode in dixi_tscode_from_sell_list]
    dixi_tscode_from_buy_list = flask.request.form.getlist('dixi_tscode_from_buy')
    dixi_choice_from_buy_list = [flask.request.form.get(f'dixi_from_buy_{tscode}') for tscode in dixi_tscode_from_buy_list]
    dixi_track_dict = {
        'dixi_track_tscode_list' : list(
                set([tscode for tscode,choice in zip(dixi_tscode_from_sell_list,dixi_choice_from_sell_list) if choice=='yes']) | \
                set([tscode for tscode,choice in zip(dixi_tscode_from_buy_list,dixi_choice_from_buy_list) if choice=='yes'])
            )
    }
    pass
    e_1d.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict, meta_dict=dixi_track_dict)
    return flask.redirect('/huice/liudongxing_3ptr/working')

    

@huice_bp.route('/weipandieting', methods=['GET', 'POST'])
def huice_weipandieting():
    return flask.render_template('huice/weipandieting_setting.html')
@huice_bp.route('/weipandieting/set_time_span', methods=['POST'])
def huice_weipandieting_set_time_span():
    print('in set_time_span')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    if e_wp.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end):
        return flask.redirect('/huice/weipandieting/working')
    else:
        return flask.redirect('/huice/weipandieting')
@huice_bp.route('/weipandieting/working')
def huice_weipandieting_working():

    end_pool_dict_list = []
    print(f'end_tscode2vol_dict len: {len(e_wp.dayStamps[e_wp.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e_wp.dayStamps[e_wp.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_wp.dayTags[e_wp.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        stk_dict['have_vol'] = vol
        try:
            stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_wp.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_wp.trade_date}'
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_wp.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_wp.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        stk_dict['sell_price_str'] = '0.00'
        end_pool_dict_list.append(stk_dict)
    
    data_got = False
    while not data_got:
        try:
            daily_pool_tscode_list = wc.search(f'{e_wp.trade_date}跌停').股票代码.tolist()
            daily_pool_tscode_list.extend(wc.search(f'{tt.preTradeDate(e_wp.trade_date)}跌停').股票代码.tolist())
            data_got = True
        except:
            pass
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_wp.dayTags[e_wp.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_wp.trade_date)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist()
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_wp.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_wp.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_wp.trade_date}'
        buy_price = close
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    
    account_data = {
        'trade_date': list(e_wp.dayStamps.keys()),
        'totals': [ds.end_total for ds in e_wp.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e_wp.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    # end_tags = sorted(list(e_wp.dayTags[e_wp.trade_date]['end_tags2count_dict'].items()),
    #                   key=lambda tag_count:tag_count[1], reverse=True)
    change=e_wp.dayStamps[e_wp.trade_date].end_total - e_wp.dayStamps[e_wp.trade_date].start_total
    chg_pct=change/e_wp.dayStamps[e_wp.trade_date].start_total
    return flask.render_template('huice/weipandieting_working.html',
                                 beg_date=e_wp.beg_date, end_date=e_wp.end_date,
                                 trade_date=e_wp.trade_date,
                                 end_total=e_wp.dayStamps[e_wp.trade_date].end_total,
                                 end_cash=e_wp.dayStamps[e_wp.trade_date].end_cash,
                                 change=f'{change:.1f}',
                                 chg_pct=f'{chg_pct*100:.2f}',
                                 account_lines_html=account_lines_html,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/weipandieting/working/choosing', methods=['POST'])
def huice_weipandieting_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_price_list' : flask.request.form.getlist('sell_price')
    }
    pass
    e_wp.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict)
    return flask.redirect('/huice/weipandieting/working')

    

@huice_bp.route('/wencaiShoudong', methods=['GET', 'POST'])
def huice_wencaiShoudong():
    return flask.render_template('huice/wencaiShoudong_setting.html')
@huice_bp.route('/wencaiShoudong/setting', methods=['POST'])
def huice_wencaiShoudong_setting():
    print('[huice_wencaiShoudong_setting]')
    trade_time_beg = flask.request.form.get('trade_time_beg')
    trade_time_end = flask.request.form.get('trade_time_end')
    wencai_query = flask.request.form.get('wencai_query')
    if e_wc.set_date_span(beg_date=trade_time_beg, end_date=trade_time_end) and e_wc.set_wencai_query(wencai_query):
        return flask.redirect('/huice/wencaiShoudong/working')
    else:
        return flask.redirect('/huice/wencaiShoudong')
@huice_bp.route('/wencaiShoudong/working')
def huice_wencaiShoudong_working():

    print(f'[huice_wencaiShoudong_working] {e_wc.trade_date}')
    end_pool_dict_list = []
    print(f'end_tscode2vol_dict len: {len(e_wc.dayStamps[e_wc.trade_date].end_tscode2vol_dict)}')
    for ts_code, vol in tqdm(e_wc.dayStamps[e_wc.trade_date].end_tscode2vol_dict.items()):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['pre_close'] = ddf.get_pre_close(ts_code,e_wc.trade_date)
        stk_dict['high'] = ddf.get_high(ts_code,e_wc.trade_date)
        stk_dict['open'] = ddf.get_open(ts_code,e_wc.trade_date)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_wc.dayTags[e_wc.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        stk_dict['have_vol'] = vol
        try:
            stk_dict['have_amount'] = vol*SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_wc.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_wc.trade_date}'
        stk_dict['have_amount'] = '%.2f'%stk_dict['have_amount']
        # fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_wc.trade_date)
        fenshi_df = tf.get_fenshi_df_k_days(ts_code, e_wc.trade_date, 3)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist(),
            'pre_close': ddf.get_pre_close(ts_code,tt.preTradeDate(tt.preTradeDate(e_wc.trade_date)))
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_wc.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick),
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        candles_data_json = json.dumps(candles_data)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='end_fenshi_'+ts_code, 
                                                        chart_type='fenshi_duori', 
                                                        chart_data_json=fenshi_data_json)
        stk_dict['sell_price_str'] = '0.00'
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_wc.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_wc.trade_date}'
        buy_price = close
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        end_pool_dict_list.append(stk_dict)
    
    try_times_max = 10
    for try_times in range(try_times_max):
        try:
            pre_daily_pool_tscode_list = wc.search(e_wc.pre_wencai_query).股票代码.tolist()
            pre_daily_pool_tscode_list = list(set(pre_daily_pool_tscode_list)-set(e_wc.pre_dayStamp.end_tscode2vol_dict.keys()))
            break
        except:
            pre_daily_pool_tscode_list = []
    print(f'pre_daily_pool_tscode_list len: {len(pre_daily_pool_tscode_list)}')
    pre_daily_pool_dict_list = []
    for ts_code in tqdm(pre_daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['pre_close'] = ddf.get_pre_close(ts_code,e_wc.trade_date)
        stk_dict['high'] = ddf.get_high(ts_code,e_wc.trade_date)
        stk_dict['open'] = ddf.get_open(ts_code,e_wc.trade_date)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_wc.dayTags[e_wc.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        # fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_wc.trade_date)
        fenshi_df = tf.get_fenshi_df_k_days(ts_code, e_wc.trade_date, 3)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist(),
            'pre_close': ddf.get_pre_close(ts_code,tt.preTradeDate(tt.preTradeDate(e_wc.trade_date)))
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_wc.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi_duori', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_wc.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_wc.trade_date}'
        buy_price = close
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        pre_daily_pool_dict_list.append(stk_dict)

    
    try_times_max = 10
    for try_times in range(try_times_max):
        try:
            daily_pool_tscode_list = wc.search(e_wc.wencai_query).股票代码.tolist()
            daily_pool_tscode_list = list(set(daily_pool_tscode_list)-set(e_wc.pre_dayStamp.end_tscode2vol_dict.keys()))
            daily_pool_tscode_list = list(set(daily_pool_tscode_list)-set(pre_daily_pool_tscode_list))
            break
        except:
            daily_pool_tscode_list = []
    print(f'daily_pool_tscode_list len: {len(daily_pool_tscode_list)}')
    daily_pool_dict_list = []
    for ts_code in tqdm(daily_pool_tscode_list):
        stk_dict = dict()
        stk_dict['ts_code'] = ts_code
        stk_dict['ts_name'] = ddf.get_name(ts_code=ts_code)
        stk_dict['pre_close'] = ddf.get_pre_close(ts_code,e_wc.trade_date)
        stk_dict['high'] = ddf.get_high(ts_code,e_wc.trade_date)
        stk_dict['open'] = ddf.get_open(ts_code,e_wc.trade_date)
        stk_dict['tags'] = ddf.get_tags(ts_code=ts_code)
        try:
            stk_dict['tags'] = sorted(stk_dict['tags'], reverse=True,
                                    key=lambda tag:e_wc.dayTags[e_wc.trade_date]['end_tags2count_dict'][tag])
        except:
            pass
        # fenshi_df = tf.get_fenshi_df(ts_code=ts_code,trade_date=e_wc.trade_date)
        fenshi_df = tf.get_fenshi_df_k_days(ts_code, e_wc.trade_date, 3)
        fenshi_data_json = json.dumps({
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'price': fenshi_df.price.tolist(),
            'vol': fenshi_df.vol.tolist(),
            'pre_close': ddf.get_pre_close(ts_code,tt.preTradeDate(tt.preTradeDate(e_wc.trade_date)))
        })
        candleSticks_df=ddf.daily(ts_code=ts_code,end_date=e_wc.trade_date
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        candleSticks_list = []
        turnovers_list = []
        for i in range(len(candleSticks_df)):
            candleStick = [
                candleSticks_df.iloc[i].trade_date,
                candleSticks_df.iloc[i].open*1.0,
                candleSticks_df.iloc[i].close*1.0,
                candleSticks_df.iloc[i].low*1.0,
                candleSticks_df.iloc[i].high*1.0,
                candleSticks_df.iloc[i].vol*1.0,
            ]
            candleSticks_list.append(candleStick)
            turnovers_list.append(candleSticks_df.iloc[i].turnover*1.0)
        candles_data = {
            'ts_code': ts_code,
            'ts_name': stk_dict['ts_name'],
            'candleSticks_list': candleSticks_list,
            'turnovers_list': turnovers_list
        }
        try:
            candles_data_json = json.dumps(candles_data)
        except Exception as exce:
            print(exce)
        stk_dict['candles_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_candles_'+ts_code, 
                                                        chart_type='candles', 
                                                        chart_data_json=candles_data_json)
        stk_dict['fenshi_html'] = flask.render_template('echarts_declare_one_fig.html', 
                                                        chart_id='daily_fenshi_'+ts_code, 
                                                        chart_type='fenshi_duori', 
                                                        chart_data_json=fenshi_data_json)
        try:
            close = SingleStock_daily().getDaily_df(ts_code=ts_code,trade_date=e_wc.trade_date).close.iloc[0]
        except:
            assert False, f'{ts_code}, {e_wc.trade_date}'
        buy_price = close
        stk_dict['buy_price_str'] = '%.2f'%buy_price
        daily_pool_dict_list.append(stk_dict)

    
    account_data = {
        'trade_date': list(e_wc.dayStamps.keys()),
        'totals': [ds.end_total for ds in e_wc.dayStamps.values()],
        'positions': [1-ds.end_cash/ds.end_total for ds in e_wc.dayStamps.values()]
    }
    account_json = json.dumps(account_data)
    account_lines_html = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='account', chart_data_json=account_json)
    # end_tags = sorted(list(e_wc.dayTags[e_wc.trade_date]['end_tags2count_dict'].items()),
    #                   key=lambda tag_count:tag_count[1], reverse=True)
    change=e_wc.dayStamps[e_wc.trade_date].end_total - e_wc.dayStamps[e_wc.trade_date].start_total
    chg_pct=change/e_wc.dayStamps[e_wc.trade_date].start_total
    return flask.render_template('huice/wencaiShoudong_working.html',
                                 beg_date=e_wc.beg_date, end_date=e_wc.end_date,
                                 trade_date=e_wc.trade_date,
                                 wencai_query=e_wc.wencai_query,
                                 end_total=e_wc.dayStamps[e_wc.trade_date].end_total,
                                 end_cash=e_wc.dayStamps[e_wc.trade_date].end_cash,
                                 change=f'{change:.1f}',
                                 chg_pct=f'{chg_pct*100:.2f}',
                                 account_lines_html=account_lines_html,
                                 pre_daily_pool=pre_daily_pool_dict_list,
                                 daily_pool=daily_pool_dict_list,
                                 end_pool=end_pool_dict_list)
@huice_bp.route('/wencaiShoudong/working/choosing', methods=['POST'])
def huice_wencaiShoudong_working_choosing():
    buy_form_dict = {
        'buy_tscode_list' : flask.request.form.getlist('buy_tscode'),
        'buy_price_list' : [float(p) for p in flask.request.form.getlist('buy_price')],
        'buy_hands_list' : [int(h) for h in flask.request.form.getlist('buy_hands')]
    }
    sell_form_dict = {
        'sell_tscode_list' : flask.request.form.getlist('sell_tscode'),
        'sell_price_list' : flask.request.form.getlist('sell_price')
    }
    pass
    e_wc.move_on(sell_form_dict=sell_form_dict,buy_form_dict=buy_form_dict)
    return flask.redirect('/huice/wencaiShoudong/working')


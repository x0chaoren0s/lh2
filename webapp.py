import flask, os, json, random
from blueprints.huice import huice_bp
from lh.stockinfo import SingleStock_daily
from lh.utils.dongcai_df_fetcher import Dongcai_df_fetcher
from lh.utils.tushare_df_fetcher import Tushare_df_fetcher
from lh.utils.tdx_df_fetcher import Tdx_df_fetcher
import lh.stockinfo.data_fetcher as df

from tqdm import tqdm

app = flask.Flask(__name__)
app.register_blueprint(huice_bp)

# df = Dongcai_df_fetcher()
# tf = Tushare_df_fetcher()
# tdf = Tdx_df_fetcher()
tf = df
tdf = df

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
    # insert1=flask.render_template('candles.html',chart_id='main',index=index,data=data)
    # insert2=flask.render_template('fenshi.html',chart_id='main2')
    # return flask.render_template('index.html',insert1=insert1,insert2=insert2)"
    data=[
              { 'value': 7, 'name': '亏' },
              { 'value': 2, 'name': '平' },
              { 'value': 1, 'name': '赚' }
            ]
    data_json=json.dumps(data)
    fenshi_data={
        'ts_code': '603528.SH',
        'ts_name': '多伦科技',
        'pre_close': 8.9,
        'price': [8.99, 9.01, 9.01, 9.11, 9.05, 8.97, 9.08, 9.1, 9.04, 9.08, 9.0, 9.01, 8.96, 9.0, 9.01, 9.06, 9.01, 9.02, 9.07, 9.13, 9.12, 9.17, 9.23, 9.14, 9.23, 9.17, 9.3, 9.29, 9.39, 9.29, 9.39, 9.4, 9.57, 9.53, 9.65, 9.6, 9.6, 9.7, 9.77, 9.76, 9.68, 9.69, 9.78, 9.76, 9.62, 9.54, 9.66, 9.56, 9.61, 9.65, 9.59, 9.62, 9.63, 9.6, 9.61, 9.6, 9.54, 9.53, 9.57, 9.6, 9.66, 9.75, 9.74, 9.9, 10.04, 9.94, 9.89, 9.98, 9.92, 9.98, 10.02, 9.93, 9.93, 9.97, 9.81, 9.85, 9.88, 9.8, 9.76, 9.82, 9.85, 9.82, 9.78, 9.79, 9.86, 9.85, 9.87, 9.91, 9.97, 9.93, 9.9, 9.89, 9.85, 9.81, 9.92, 9.86, 9.86, 9.89, 9.89, 9.88, 9.85, 9.83, 9.81, 9.83, 9.78, 9.79, 9.74, 9.7, 9.72, 9.78, 9.81, 9.74, 9.74, 9.76, 9.74, 9.7, 9.66, 9.75, 9.75, 9.78, 9.73, 9.76, 9.85, 9.79, 9.78, 9.77, 9.76, 9.76, 9.75, 9.7, 9.68, 9.67, 9.67, 9.71, 9.73, 9.73, 9.77, 9.78, 9.73, 9.72, 9.73, 9.73, 9.7, 9.69, 9.67, 9.67, 9.69, 9.66, 9.64, 9.63, 9.64, 9.57, 9.6, 9.62, 9.65, 9.65, 9.63, 9.63, 9.67, 9.71, 9.73, 9.78, 9.83, 9.85, 9.73, 9.83, 9.81, 9.8, 9.82, 9.79, 9.75, 9.78, 9.75, 9.75, 9.79, 9.82, 9.84, 10.0, 9.92, 10.01, 10.07, 10.0, 9.99, 9.97, 9.93, 9.9, 10.0, 10.0, 10.0, 9.98, 9.96, 9.97, 9.97, 9.95, 9.88, 9.88, 9.91, 9.93, 9.93, 9.94, 9.93, 9.9, 9.87, 9.86, 9.87, 9.85, 9.81, 9.78, 9.76, 9.74, 9.7, 9.74, 9.75, 9.75, 9.77, 9.77, 9.77, 9.77, 9.76, 9.76, 9.75, 9.7, 9.67, 9.68, 9.71, 9.74, 9.77, 9.8, 9.89, 10.05, 10.03, 9.97, 9.97, 9.94, 9.96, 9.95, 9.95, 9.96, 9.96, 9.96]+[random.randint(980,1999)/100 for _ in range(240)],
        'vol': [100909, 30707, 21514, 15498, 18678, 13620, 11239, 8838, 9385, 8796, 5963, 7384, 6154, 7859, 4475, 7155, 3812, 5137, 3198, 6027, 6525, 4844, 11538, 11194, 4392, 5235, 8178, 4066, 5692, 6666, 5755, 5673, 11665, 19039, 12901, 22999, 8392, 9915, 16530, 17295, 9826, 6896, 4125, 9639, 7090, 6410, 4903, 6115, 3915, 3021, 3533, 2629, 2063, 1571, 1848, 1322, 2516, 5154, 2134, 1631, 3438, 5976, 6607, 11603, 20526, 9805, 4611, 3661, 7435, 3094, 4754, 3820, 2074, 1909, 5008, 1780, 1486, 2327, 2752, 1449, 1063, 2135, 1754, 1373, 1231, 744, 962, 1446, 3517, 2193, 1391, 913, 1691, 844, 1494, 784, 1181, 1060, 946, 649, 1196, 677, 929, 854, 3916, 1228, 2040, 2009, 2062, 1213, 1137, 1122, 1619, 565, 1075, 1461, 1967, 872, 1081, 854, 2425, 898, 3210, 972, 645, 801, 914, 708, 1072, 1246, 943, 1028, 1029, 897, 1317, 1530, 933, 1703, 1907, 1190, 1592, 951, 1171, 1037, 1167, 1215, 713, 1600, 1667, 1851, 765, 3810, 2804, 1372, 1818, 1300, 1402, 571, 1528, 1279, 1931, 2019, 2925, 2424, 1651, 1440, 1093, 682, 1048, 1283, 903, 578, 591, 406, 642, 1535, 1644, 9658, 3568, 5442, 7894, 3746, 2073, 2220, 796, 1015, 1796, 3120, 1138, 1220, 1594, 935, 916, 1096, 1406, 1126, 1039, 1064, 607, 952, 989, 1299, 465, 1025, 1300, 1423, 1711, 1286, 1543, 1336, 1990, 2306, 1742, 1928, 988, 1288, 1347, 934, 1540, 1256, 2062, 2117, 2285, 2253, 2510, 1606, 1871, 2606, 3202, 9625, 10206, 4997, 4058, 5094, 4534, 7274, 8594, 290, 0, 8335]+[random.randint(0,8335) for _ in range(240)]
    }
    fenshi_data_json=json.dumps(fenshi_data)
    # candleSticks_df=SingleStock_daily().getCandles_day_df(ts_code='002089.SZ',end_date='20230307'
    #         ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
    candleSticks_df=df.daily(ts_code='002089.SZ',end_date='20230307'
            ).sort_values(by='trade_date', ascending=True).reset_index(drop=True)
    candleSticks_list = []
    for i in range(len(candleSticks_df)):
        candleStick = [
            candleSticks_df.iloc[i].trade_date,
            candleSticks_df.iloc[i].open,
            candleSticks_df.iloc[i].close,
            candleSticks_df.iloc[i].low,
            candleSticks_df.iloc[i].high,
            candleSticks_df.iloc[i].vol,
        ]
        candleSticks_list.append(candleStick)
    candles_data = {
        'ts_code': '002089.SZ',
        'ts_name': '*ST新海',
        'candleSticks_list': candleSticks_list
    }
    # candles_data_json = json.dumps(candles_data)
        
    for _ in tqdm(range(100)):
        a=3+6
        'debug'
    # insert1 = flask.render_template('echarts_declare_one_fig.html', chart_id='fenshi', chart_type='fenshi', chart_data_json=fenshi_data_json)
    insert1 = flask.render_template('echarts_declare_one_fig.html', chart_id='fenshi', chart_type='fenshi_2ri', chart_data_json=fenshi_data_json)
    insert2 = flask.render_template('echarts_declare_one_fig.html', chart_id='test', chart_type='pie', chart_data_json=data_json)
    # insert3 = flask.render_template('echarts_declare_one_fig.html', chart_id='candles', chart_type='candles', chart_data_json=candles_data_json)
    return flask.render_template('index.html',insert1=insert1,insert2=insert2)
    # return flask.render_template('index.html')

@app.route('/save_buf', methods=['POST'])
def save_buf():
    print('[save_buf]')
    tf.save_buf()
    tdf.save_buf()
    df.save_buf()
    return flask.redirect(flask.request.referrer)


if __name__ == '__main__':
    app.run()
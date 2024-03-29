const type2drawfun = new Map([
    ['pie', draw_pie],
    ['fenshi', draw_fenshi],
    ['fenshi_duori', draw_fenshi_duori],
    ['candles', draw_candleStickBrush],
    ['account', draw_accountLines]
]) // 图表类型及该类型的option的构建函数，各函数在本文件下面定义

var chart_doms = []
var charts = []
var chart_types = []
var chart_datas = []
var chart_options = []
for(var i=0; i<chart_ids.length; ++i){
    chart_doms[i] = document.getElementById(chart_ids[i])
    // charts[i] = echarts.init(chart_doms[i])
    chart_types[i] = chart_doms[i].getAttribute('chart_type')
    chart_datas[i] = JSON.parse(chart_doms[i].getAttribute('chart_data_json'))
    
    // chart_options[i] = type2builder.get(chart_types[i])(chart_datas[i])

    // chart_options[i] && charts[i].setOption(chart_options[i])
    type2drawfun.get(chart_types[i])(chart_doms[i], chart_datas[i])
}

// 下面都是函数定义

function draw_pie(chart_dom, chart_data) {
    option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          top: '5%',
          left: 'center'
        },
        series: [
          {
            name: 'Access From',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: 40,
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: false
            },
            // data: [
            //   { value: 1048, name: 'Search Engine' },
            //   { value: 735, name: 'Direct' },
            //   { value: 580, name: 'Email' },
            //   { value: 484, name: 'Union Ads' },
            //   { value: 300, name: 'Video Ads' }
            // ]
            data: chart_data
          }
        ]
      };
    // return option
    charts = echarts.init(chart_dom)
    option && charts.setOption(option)
}

function draw_fenshi(chart_dom, chart_data) {
    // var ts_code = '603528.SH'
    // var ts_name = '多伦科技'
    // var price = [8.99, 9.01, 9.01, 9.11, 9.05, 8.97, 9.08, 9.1, 9.04, 9.08, 9.0, 9.01, 8.96, 9.0, 9.01, 9.06, 9.01, 9.02, 9.07, 9.13, 9.12, 9.17, 9.23, 9.14, 9.23, 9.17, 9.3, 9.29, 9.39, 9.29, 9.39, 9.4, 9.57, 9.53, 9.65, 9.6, 9.6, 9.7, 9.77, 9.76, 9.68, 9.69, 9.78, 9.76, 9.62, 9.54, 9.66, 9.56, 9.61, 9.65, 9.59, 9.62, 9.63, 9.6, 9.61, 9.6, 9.54, 9.53, 9.57, 9.6, 9.66, 9.75, 9.74, 9.9, 10.04, 9.94, 9.89, 9.98, 9.92, 9.98, 10.02, 9.93, 9.93, 9.97, 9.81, 9.85, 9.88, 9.8, 9.76, 9.82, 9.85, 9.82, 9.78, 9.79, 9.86, 9.85, 9.87, 9.91, 9.97, 9.93, 9.9, 9.89, 9.85, 9.81, 9.92, 9.86, 9.86, 9.89, 9.89, 9.88, 9.85, 9.83, 9.81, 9.83, 9.78, 9.79, 9.74, 9.7, 9.72, 9.78, 9.81, 9.74, 9.74, 9.76, 9.74, 9.7, 9.66, 9.75, 9.75, 9.78, 9.73, 9.76, 9.85, 9.79, 9.78, 9.77, 9.76, 9.76, 9.75, 9.7, 9.68, 9.67, 9.67, 9.71, 9.73, 9.73, 9.77, 9.78, 9.73, 9.72, 9.73, 9.73, 9.7, 9.69, 9.67, 9.67, 9.69, 9.66, 9.64, 9.63, 9.64, 9.57, 9.6, 9.62, 9.65, 9.65, 9.63, 9.63, 9.67, 9.71, 9.73, 9.78, 9.83, 9.85, 9.73, 9.83, 9.81, 9.8, 9.82, 9.79, 9.75, 9.78, 9.75, 9.75, 9.79, 9.82, 9.84, 10.0, 9.92, 10.01, 10.07, 10.0, 9.99, 9.97, 9.93, 9.9, 10.0, 10.0, 10.0, 9.98, 9.96, 9.97, 9.97, 9.95, 9.88, 9.88, 9.91, 9.93, 9.93, 9.94, 9.93, 9.9, 9.87, 9.86, 9.87, 9.85, 9.81, 9.78, 9.76, 9.74, 9.7, 9.74, 9.75, 9.75, 9.77, 9.77, 9.77, 9.77, 9.76, 9.76, 9.75, 9.7, 9.67, 9.68, 9.71, 9.74, 9.77, 9.8, 9.89, 10.05, 10.03, 9.97, 9.97, 9.94, 9.96, 9.95, 9.95, 9.96, 9.96, 9.96]
    // var vol = [100909, 30707, 21514, 15498, 18678, 13620, 11239, 8838, 9385, 8796, 5963, 7384, 6154, 7859, 4475, 7155, 3812, 5137, 3198, 6027, 6525, 4844, 11538, 11194, 4392, 5235, 8178, 4066, 5692, 6666, 5755, 5673, 11665, 19039, 12901, 22999, 8392, 9915, 16530, 17295, 9826, 6896, 4125, 9639, 7090, 6410, 4903, 6115, 3915, 3021, 3533, 2629, 2063, 1571, 1848, 1322, 2516, 5154, 2134, 1631, 3438, 5976, 6607, 11603, 20526, 9805, 4611, 3661, 7435, 3094, 4754, 3820, 2074, 1909, 5008, 1780, 1486, 2327, 2752, 1449, 1063, 2135, 1754, 1373, 1231, 744, 962, 1446, 3517, 2193, 1391, 913, 1691, 844, 1494, 784, 1181, 1060, 946, 649, 1196, 677, 929, 854, 3916, 1228, 2040, 2009, 2062, 1213, 1137, 1122, 1619, 565, 1075, 1461, 1967, 872, 1081, 854, 2425, 898, 3210, 972, 645, 801, 914, 708, 1072, 1246, 943, 1028, 1029, 897, 1317, 1530, 933, 1703, 1907, 1190, 1592, 951, 1171, 1037, 1167, 1215, 713, 1600, 1667, 1851, 765, 3810, 2804, 1372, 1818, 1300, 1402, 571, 1528, 1279, 1931, 2019, 2925, 2424, 1651, 1440, 1093, 682, 1048, 1283, 903, 578, 591, 406, 642, 1535, 1644, 9658, 3568, 5442, 7894, 3746, 2073, 2220, 796, 1015, 1796, 3120, 1138, 1220, 1594, 935, 916, 1096, 1406, 1126, 1039, 1064, 607, 952, 989, 1299, 465, 1025, 1300, 1423, 1711, 1286, 1543, 1336, 1990, 2306, 1742, 1928, 988, 1288, 1347, 934, 1540, 1256, 2062, 2117, 2285, 2253, 2510, 1606, 1871, 2606, 3202, 9625, 10206, 4997, 4058, 5094, 4534, 7274, 8594, 290, 0, 8335]
    var ts_code = chart_data.ts_code, ts_name = chart_data.ts_name
    var price = chart_data.price, vol = chart_data.vol
    var pre_close = chart_data.pre_close
    var avg_price = compute_avg_price(price, vol)
    option = {
    title: {
        text: ts_name,
        subtext: ts_code,
        left: '3%'
    },
    color: ["#3398DB"],
    tooltip: {
        trigger: "axis",
        axisPointer: {
        type: "shadow"
        }
    },
    grid: [
        { top: '15%', height: '50%', left: '10%', right: '6%' },
        { bottom: '10%', height: '23%', left: '10%', right: '6%' }
        ],
    xAxis: [{
        gridIndex: 0,
        type: "category",
        show: false,
        axisLabel: {
        interval:59
        },
        data:["09:30","09:31","09:32","09:33","09:34","09:35","09:36","09:37","09:38","09:39","09:40","09:41","09:42","09:43","09:44","09:45","09:46","09:47","09:48","09:49","09:50","09:51","09:52","09:53","09:54","09:55","09:56","09:57","09:58","09:59","10:00","10:01","10:02","10:03","10:04","10:05","10:06","10:07","10:08","10:09","10:10","10:11","10:12","10:13","10:14","10:15","10:16","10:17","10:18","10:19","10:20","10:21","10:22","10:23","10:24","10:25","10:26","10:27","10:28","10:29","10:30","10:31","10:32","10:33","10:34","10:35","10:36","10:37","10:38","10:39","10:40","10:41","10:42","10:43","10:44","10:45","10:46","10:47","10:48","10:49","10:50","10:51","10:52","10:53","10:54","10:55","10:56","10:57","10:58","10:59","11:00","11:01","11:02","11:03","11:04","11:05","11:06","11:07","11:08","11:09","11:10","11:11","11:12","11:13","11:14","11:15","11:16","11:17","11:18","11:19","11:20","11:21","11:22","11:23","11:24","11:25","11:26","11:27","11:28","11:29","11:30/13:00","13:01","13:02","13:03","13:04","13:05","13:06","13:07","13:08","13:09","13:10","13:11","13:12","13:13","13:14","13:15","13:16","13:17","13:18","13:19","13:20","13:21","13:22","13:23","13:24","13:25","13:26","13:27","13:28","13:29","13:30","13:31","13:32","13:33","13:34","13:35","13:36","13:37","13:38","13:39","13:40","13:41","13:42","13:43","13:44","13:45","13:46","13:47","13:48","13:49","13:50","13:51","13:52","13:53","13:54","13:55","13:56","13:57","13:58","13:59","14:00","14:01","14:02","14:03","14:04","14:05","14:06","14:07","14:08","14:09","14:10","14:11","14:12","14:13","14:14","14:15","14:16","14:17","14:18","14:19","14:20","14:21","14:22","14:23","14:24","14:25","14:26","14:27","14:28","14:29","14:30","14:31","14:32","14:33","14:34","14:35","14:36","14:37","14:38","14:39","14:40","14:41","14:42","14:43","14:44","14:45","14:46","14:47","14:48","14:49","14:50","14:51","14:52","14:53","14:54","14:55","14:56","14:57","14:58","14:59","15:00"]
    },{
        gridIndex: 1,
        type: "category",
        axisLabel: {
        interval:59
        },
        data:["09:30","09:31","09:32","09:33","09:34","09:35","09:36","09:37","09:38","09:39","09:40","09:41","09:42","09:43","09:44","09:45","09:46","09:47","09:48","09:49","09:50","09:51","09:52","09:53","09:54","09:55","09:56","09:57","09:58","09:59","10:00","10:01","10:02","10:03","10:04","10:05","10:06","10:07","10:08","10:09","10:10","10:11","10:12","10:13","10:14","10:15","10:16","10:17","10:18","10:19","10:20","10:21","10:22","10:23","10:24","10:25","10:26","10:27","10:28","10:29","10:30","10:31","10:32","10:33","10:34","10:35","10:36","10:37","10:38","10:39","10:40","10:41","10:42","10:43","10:44","10:45","10:46","10:47","10:48","10:49","10:50","10:51","10:52","10:53","10:54","10:55","10:56","10:57","10:58","10:59","11:00","11:01","11:02","11:03","11:04","11:05","11:06","11:07","11:08","11:09","11:10","11:11","11:12","11:13","11:14","11:15","11:16","11:17","11:18","11:19","11:20","11:21","11:22","11:23","11:24","11:25","11:26","11:27","11:28","11:29","11:30/13:00","13:01","13:02","13:03","13:04","13:05","13:06","13:07","13:08","13:09","13:10","13:11","13:12","13:13","13:14","13:15","13:16","13:17","13:18","13:19","13:20","13:21","13:22","13:23","13:24","13:25","13:26","13:27","13:28","13:29","13:30","13:31","13:32","13:33","13:34","13:35","13:36","13:37","13:38","13:39","13:40","13:41","13:42","13:43","13:44","13:45","13:46","13:47","13:48","13:49","13:50","13:51","13:52","13:53","13:54","13:55","13:56","13:57","13:58","13:59","14:00","14:01","14:02","14:03","14:04","14:05","14:06","14:07","14:08","14:09","14:10","14:11","14:12","14:13","14:14","14:15","14:16","14:17","14:18","14:19","14:20","14:21","14:22","14:23","14:24","14:25","14:26","14:27","14:28","14:29","14:30","14:31","14:32","14:33","14:34","14:35","14:36","14:37","14:38","14:39","14:40","14:41","14:42","14:43","14:44","14:45","14:46","14:47","14:48","14:49","14:50","14:51","14:52","14:53","14:54","14:55","14:56","14:57","14:58","14:59","15:00"]
        
    }],
    
    yAxis: [{
        gridIndex: 0,
        type: "value",
        show: true,
        // min: get_yAxis_min_max(ts_name, pre_close)[0],
        // max: get_yAxis_min_max(ts_name, pre_close)[1],
    },{
        gridIndex: 1,
        type: "value",
    }],
    axisPointer: {
        link: {
        xAxisIndex: 'all'
        }
    },
    series: [{
        xAxisIndex: 0,
        yAxisIndex: 0,
        name: "分时",
        type: "line",
        showSymbol: false,
        data: price
    },{
        xAxisIndex: 0,
        yAxisIndex: 0,
        name: "均价",
        type: "line",
        showSymbol: false,
        lineStyle:{
        color: 'yellow'
        },
        data: avg_price
    },{
        xAxisIndex: 1,
        yAxisIndex: 1,
        name: "成交量",
        type: "bar",
        showSymbol: false,
        data: vol
        
    }]
    }
    function compute_avg_price(price, vol){
        tot_price = [price[0]*vol[0]]
        for(var i=1;i<price.length;++i){
            tot_price.push(tot_price[i-1]+price[i]*vol[i])
        }
        tot_vol = [vol[0]]
        for(i=1;i<vol.length;++i){
            tot_vol.push(tot_vol[i-1]+vol[i])
        }
        avg_price = []
        for(i=0;i<vol.length;++i){
            avg_price.push(round(tot_price[i]/tot_vol[i]))
        }
        return avg_price  
    }
    // return option
    charts = echarts.init(chart_dom)
    option && charts.setOption(option)
}
function draw_fenshi_duori(chart_dom, chart_data) {
    // var ts_code = '603528.SH'
    // var ts_name = '多伦科技'
    // var price = [8.99, 9.01, 9.01, 9.11, 9.05, 8.97, 9.08, 9.1, 9.04, 9.08, 9.0, 9.01, 8.96, 9.0, 9.01, 9.06, 9.01, 9.02, 9.07, 9.13, 9.12, 9.17, 9.23, 9.14, 9.23, 9.17, 9.3, 9.29, 9.39, 9.29, 9.39, 9.4, 9.57, 9.53, 9.65, 9.6, 9.6, 9.7, 9.77, 9.76, 9.68, 9.69, 9.78, 9.76, 9.62, 9.54, 9.66, 9.56, 9.61, 9.65, 9.59, 9.62, 9.63, 9.6, 9.61, 9.6, 9.54, 9.53, 9.57, 9.6, 9.66, 9.75, 9.74, 9.9, 10.04, 9.94, 9.89, 9.98, 9.92, 9.98, 10.02, 9.93, 9.93, 9.97, 9.81, 9.85, 9.88, 9.8, 9.76, 9.82, 9.85, 9.82, 9.78, 9.79, 9.86, 9.85, 9.87, 9.91, 9.97, 9.93, 9.9, 9.89, 9.85, 9.81, 9.92, 9.86, 9.86, 9.89, 9.89, 9.88, 9.85, 9.83, 9.81, 9.83, 9.78, 9.79, 9.74, 9.7, 9.72, 9.78, 9.81, 9.74, 9.74, 9.76, 9.74, 9.7, 9.66, 9.75, 9.75, 9.78, 9.73, 9.76, 9.85, 9.79, 9.78, 9.77, 9.76, 9.76, 9.75, 9.7, 9.68, 9.67, 9.67, 9.71, 9.73, 9.73, 9.77, 9.78, 9.73, 9.72, 9.73, 9.73, 9.7, 9.69, 9.67, 9.67, 9.69, 9.66, 9.64, 9.63, 9.64, 9.57, 9.6, 9.62, 9.65, 9.65, 9.63, 9.63, 9.67, 9.71, 9.73, 9.78, 9.83, 9.85, 9.73, 9.83, 9.81, 9.8, 9.82, 9.79, 9.75, 9.78, 9.75, 9.75, 9.79, 9.82, 9.84, 10.0, 9.92, 10.01, 10.07, 10.0, 9.99, 9.97, 9.93, 9.9, 10.0, 10.0, 10.0, 9.98, 9.96, 9.97, 9.97, 9.95, 9.88, 9.88, 9.91, 9.93, 9.93, 9.94, 9.93, 9.9, 9.87, 9.86, 9.87, 9.85, 9.81, 9.78, 9.76, 9.74, 9.7, 9.74, 9.75, 9.75, 9.77, 9.77, 9.77, 9.77, 9.76, 9.76, 9.75, 9.7, 9.67, 9.68, 9.71, 9.74, 9.77, 9.8, 9.89, 10.05, 10.03, 9.97, 9.97, 9.94, 9.96, 9.95, 9.95, 9.96, 9.96, 9.96]
    // var vol = [100909, 30707, 21514, 15498, 18678, 13620, 11239, 8838, 9385, 8796, 5963, 7384, 6154, 7859, 4475, 7155, 3812, 5137, 3198, 6027, 6525, 4844, 11538, 11194, 4392, 5235, 8178, 4066, 5692, 6666, 5755, 5673, 11665, 19039, 12901, 22999, 8392, 9915, 16530, 17295, 9826, 6896, 4125, 9639, 7090, 6410, 4903, 6115, 3915, 3021, 3533, 2629, 2063, 1571, 1848, 1322, 2516, 5154, 2134, 1631, 3438, 5976, 6607, 11603, 20526, 9805, 4611, 3661, 7435, 3094, 4754, 3820, 2074, 1909, 5008, 1780, 1486, 2327, 2752, 1449, 1063, 2135, 1754, 1373, 1231, 744, 962, 1446, 3517, 2193, 1391, 913, 1691, 844, 1494, 784, 1181, 1060, 946, 649, 1196, 677, 929, 854, 3916, 1228, 2040, 2009, 2062, 1213, 1137, 1122, 1619, 565, 1075, 1461, 1967, 872, 1081, 854, 2425, 898, 3210, 972, 645, 801, 914, 708, 1072, 1246, 943, 1028, 1029, 897, 1317, 1530, 933, 1703, 1907, 1190, 1592, 951, 1171, 1037, 1167, 1215, 713, 1600, 1667, 1851, 765, 3810, 2804, 1372, 1818, 1300, 1402, 571, 1528, 1279, 1931, 2019, 2925, 2424, 1651, 1440, 1093, 682, 1048, 1283, 903, 578, 591, 406, 642, 1535, 1644, 9658, 3568, 5442, 7894, 3746, 2073, 2220, 796, 1015, 1796, 3120, 1138, 1220, 1594, 935, 916, 1096, 1406, 1126, 1039, 1064, 607, 952, 989, 1299, 465, 1025, 1300, 1423, 1711, 1286, 1543, 1336, 1990, 2306, 1742, 1928, 988, 1288, 1347, 934, 1540, 1256, 2062, 2117, 2285, 2253, 2510, 1606, 1871, 2606, 3202, 9625, 10206, 4997, 4058, 5094, 4534, 7274, 8594, 290, 0, 8335]
    var num_days = chart_data.price.length/240
    var time_tick_label_base = ["09:30","09:31","09:32","09:33","09:34","09:35","09:36","09:37","09:38","09:39","09:40","09:41","09:42","09:43","09:44","09:45","09:46","09:47","09:48","09:49","09:50","09:51","09:52","09:53","09:54","09:55","09:56","09:57","09:58","09:59","10:00","10:01","10:02","10:03","10:04","10:05","10:06","10:07","10:08","10:09","10:10","10:11","10:12","10:13","10:14","10:15","10:16","10:17","10:18","10:19","10:20","10:21","10:22","10:23","10:24","10:25","10:26","10:27","10:28","10:29","10:30","10:31","10:32","10:33","10:34","10:35","10:36","10:37","10:38","10:39","10:40","10:41","10:42","10:43","10:44","10:45","10:46","10:47","10:48","10:49","10:50","10:51","10:52","10:53","10:54","10:55","10:56","10:57","10:58","10:59","11:00","11:01","11:02","11:03","11:04","11:05","11:06","11:07","11:08","11:09","11:10","11:11","11:12","11:13","11:14","11:15","11:16","11:17","11:18","11:19","11:20","11:21","11:22","11:23","11:24","11:25","11:26","11:27","11:28","11:29","11:30/13:00","13:01","13:02","13:03","13:04","13:05","13:06","13:07","13:08","13:09","13:10","13:11","13:12","13:13","13:14","13:15","13:16","13:17","13:18","13:19","13:20","13:21","13:22","13:23","13:24","13:25","13:26","13:27","13:28","13:29","13:30","13:31","13:32","13:33","13:34","13:35","13:36","13:37","13:38","13:39","13:40","13:41","13:42","13:43","13:44","13:45","13:46","13:47","13:48","13:49","13:50","13:51","13:52","13:53","13:54","13:55","13:56","13:57","13:58","13:59","14:00","14:01","14:02","14:03","14:04","14:05","14:06","14:07","14:08","14:09","14:10","14:11","14:12","14:13","14:14","14:15","14:16","14:17","14:18","14:19","14:20","14:21","14:22","14:23","14:24","14:25","14:26","14:27","14:28","14:29","14:30","14:31","14:32","14:33","14:34","14:35","14:36","14:37","14:38","14:39","14:40","14:41","14:42","14:43","14:44","14:45","14:46","14:47","14:48","14:49","14:50","14:51","14:52","14:53","14:54","14:55","14:56","14:57","14:58","14:59","15:00"]
    // time_tick_label = time_tick_label_base.concat(time_tick_label_base)
    var time_tick_label = []
    for(var i=0;i<num_days;i++){
        time_tick_label = time_tick_label.concat(time_tick_label_base)
    }
    var ts_code = chart_data.ts_code, ts_name = chart_data.ts_name
    var price = chart_data.price, vol = chart_data.vol
    var pre_close = chart_data.pre_close
    var pre_closes = []
    for(j=0;j<240;++j){
        pre_closes.push(pre_close)
    }
    for(i=1;i<num_days;++i){
        for(j=0;j<240;++j){
            pre_closes.push(price[i*240-1])
        }
    }
    // var avg_price = compute_avg_price(price, vol)
    var avg_price = []
    for(i=0;i<num_days;++i){
        avg_price=avg_price.concat(compute_avg_price(price.slice(i*240,(i+1)*240),vol.slice(i*240,(i+1)*240)))
    }
    option = {
    title: {
        text: ts_name,
        subtext: ts_code,
        left: '3%'
    },
    color: ["#3398DB"],
    tooltip: {
        trigger: "axis",
        axisPointer: {
        type: "shadow"
        }
    },
    grid: [
        { top: '15%', height: '60%', left: '10%', right: '6%' },
        { bottom: '10%', height: '15%', left: '10%', right: '6%' }
        ],
    xAxis: [{
        gridIndex: 0,
        type: "category",
        show: false,
        axisLabel: {
        interval:59
        },
        data:time_tick_label
    },{
        gridIndex: 1,
        type: "category",
        axisLabel: {
        interval:59
        },
        data:time_tick_label
        
    }],
    
    yAxis: [{
        gridIndex: 0,
        type: "value",
        show: true,
        min: get_yAxis_min_max(ts_name, pre_closes)[0],
        max: get_yAxis_min_max(ts_name, pre_closes)[1],
    },{
        gridIndex: 1,
        type: "value",
    }],
    axisPointer: {
        link: {
        xAxisIndex: 'all'
        }
    },
    series: [{
        xAxisIndex: 0,
        yAxisIndex: 0,
        name: "分时",
        type: "line",
        showSymbol: false,
        data: price
    },{
        xAxisIndex: 0,
        yAxisIndex: 0,
        name: "均价",
        type: "line",
        showSymbol: false,
        lineStyle:{
        color: 'yellow'
        },
        data: avg_price
    },{
        xAxisIndex: 0,
        yAxisIndex: 0,
        name: "零轴",
        type: "line",
        showSymbol: false,
        lineStyle:{
        color: 'gray'
        },
        data: pre_closes
    },{
        xAxisIndex: 1,
        yAxisIndex: 1,
        name: "成交量",
        type: "bar",
        showSymbol: false,
        data: vol
        
    }]
    }
    function compute_avg_price(price, vol){
        tot_price = [price[0]*vol[0]]
        for(var i=1;i<price.length;++i){
            tot_price.push(tot_price[i-1]+price[i]*vol[i])
        }
        tot_vol = [vol[0]]
        for(i=1;i<vol.length;++i){
            tot_vol.push(tot_vol[i-1]+vol[i])
        }
        avg_price = []
        for(i=0;i<vol.length;++i){
            avg_price.push(round(tot_price[i]/tot_vol[i]))
        }
        return avg_price  
    }
    // return option
    charts = echarts.init(chart_dom)
    option && charts.setOption(option)
}

function draw_candleStickBrush(chart_dom, chart_data) {
    var ts_code = chart_data.ts_code, ts_name = chart_data.ts_name
    var rawData = chart_data.candleSticks_list // trade_date, open, close, low, high, vol
    var turnovers = chart_data.turnovers_list
    
    var chartDom = chart_dom;
    var myChart = echarts.init(chartDom);
    var option;

    const downColor = '#00da3c';
    const upColor = '#ec0000';
    function splitData(rawData) {
        let categoryData = [];
        let values = [];
        let volumes = [];
        for (let i = 0; i < rawData.length; i++) {
            categoryData.push(rawData[i].splice(0, 1)[0]);
            values.push(rawData[i]);
            volumes.push([i, rawData[i][4], rawData[i][0] > rawData[i][1] ? 1 : -1]);
        }
        return {
            categoryData: categoryData,
            values: values,
            volumes: volumes
        };
    }
    function calculateMA(dayCount, data) {
    var result = [];
    for (var i = 0, len = data.values.length; i < len; i++) {
        if (i < dayCount) {
        result.push('-');
        continue;
        }
        var sum = 0;
        for (var j = 0; j < dayCount; j++) {
        sum += data.values[i - j][1];
        }
        result.push(+(sum / dayCount).toFixed(3));
    }
    return result;
    }
    // $.get(ROOT_PATH + '/data/asset/data/stock-DJI.json', function (rawData) {
    var data = splitData(rawData);
    // myChart.setOption(
    option = {
        animation: false,
        legend: {
            bottom: 10,
            left: 'center',
            data: [ts_name, 'MA5', 'MA10', 'MA20', 'MA30']
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
            type: 'cross'
            },
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            textStyle: {
            color: '#000'
            },
            position: function (pos, params, el, elRect, size) {
            const obj = {
                top: 10
            };
            obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
            return obj;
            }
            // extraCssText: 'width: 170px'
        },
        axisPointer: {
            link: [
            {
                xAxisIndex: 'all'
            }
            ],
            label: {
            backgroundColor: '#777'
            }
        },
        toolbox: {
            feature: {
            dataZoom: {
                yAxisIndex: false
            },
            brush: {
                type: ['lineX', 'clear']
            }
            }
        },
        brush: {
            xAxisIndex: 'all',
            brushLink: 'all',
            outOfBrush: {
            colorAlpha: 0.1
            }
        },
        visualMap: {
            show: false,
            seriesIndex: 5,
            dimension: 2,
            pieces: [
            {
                value: 1,
                color: downColor
            },
            {
                value: -1,
                color: upColor
            }
            ]
        },
        grid: [
            {
            left: '10%',
            right: '8%',
            height: '50%'
            },
            {
            left: '10%',
            right: '8%',
            top: '63%',
            height: '16%'
            }
        ],
        xAxis: [
            {
            type: 'category',
            data: data.categoryData,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            min: 'dataMin',
            max: 'dataMax',
            axisPointer: {
                z: 100
            }
            },
            {
            type: 'category',
            gridIndex: 1,
            data: data.categoryData,
            boundaryGap: false,
            axisLine: { onZero: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            min: 'dataMin',
            max: 'dataMax'
            }
        ],
        yAxis: [
            {
            scale: true,
            splitArea: {
                show: true
            }
            },
            {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
            }
        ],
        dataZoom: [
            {
            type: 'inside',
            xAxisIndex: [0, 1],
            startValue: data.values.length-30
            },
            {
            show: true,
            xAxisIndex: [0, 1],
            type: 'slider',
            top: '85%'
            }
        ],
        series: [
            {
            name: ts_name,
            type: 'candlestick',
            data: data.values,
            itemStyle: {
                color: upColor,
                color0: downColor,
                borderColor: undefined,
                borderColor0: undefined
            },
            tooltip: {
                formatter: function (param) {
                    param = param[0];
                    return [
                        'Date: ' + param.name + '<hr size=1 style="margin: 3px 0">',
                        'Open: ' + param.data[0] + '<br/>',
                        'Close: ' + param.data[1] + '<br/>',
                        'Lowest: ' + param.data[2] + '<br/>',
                        'Highest: ' + param.data[3] + '<br/>'
                    ].join('');
                }
            }
            },
            {
            name: 'MA5',
            type: 'line',
            data: calculateMA(5, data),
            showSymbol: false,
            smooth: true,
            lineStyle: {
                opacity: 0.5
            }
            },
            {
            name: 'MA10',
            type: 'line',
            data: calculateMA(10, data),
            smooth: true,
            showSymbol: false,
            lineStyle: {
                opacity: 0.5
            }
            },
            {
            name: 'MA20',
            type: 'line',
            data: calculateMA(20, data),
            smooth: true,
            showSymbol: false,
            lineStyle: {
                opacity: 0.5
            }
            },
            {
            name: 'MA30',
            type: 'line',
            data: calculateMA(30, data),
            smooth: true,
            showSymbol: false,
            lineStyle: {
                opacity: 0.5
            }
            },
            {
            name: 'Volume',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: data.volumes
            },
            {
            name: 'Turnover Rate',
            type: 'scatter',
            symbolSize: 0,
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: turnovers
            }
        ]
        }
        
    myChart.dispatchAction({
        type: 'brush',
        areas: [
        {
            brushType: 'lineX',
            coordRange: ['2016-06-02', '2016-06-20'],
            xAxisIndex: 0
        }
        ]
    });
    option && myChart.setOption(option);
}

function draw_accountLines(chart_dom, chart_data) {
    option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          top: '5%',
          left: 'center'
        },
        xAxis: [
            {
                type: 'category',
                data: chart_data.trade_dates
            }
        ],
        yAxis:[
            {
                name: '总资产',
                type: 'value',
                position: 'left',
                axisLine: {
                    show: true
                },
                min: Math.min(...chart_data.totals)-2000,
                max: Math.max(...chart_data.totals)+2000,
            },
            {
                name: '仓位',
                type: 'value',
                position: 'right',
                axisLine: {
                    show: true
                }
            }
        ],
        series: [
            {
                name: '总资产',
                type: 'line',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                min: chart_data.totals.min,
                label: {
                    show: false,
                    // position: 'top'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 40,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: true
                },
                data: chart_data.totals
            },
            {
                name: '仓位',
                type: 'bar',
                data: chart_data.positions,
                yAxisIndex: 1
            }
        ]
      };
    charts = echarts.init(chart_dom)
    option && charts.setOption(option)
}

function round(num,digits=2) {
    var digit_times = Math.pow(10,digits)
    tmp = num*digit_times
    return Math.round(tmp)/digit_times
}

function isSt(ts_name){
    return ts_name.search('ST')>=0
}

function get_yAxis_min_max(ts_name, pre_closes) {
    var yGapHalf_ratio
    if(isSt(ts_name)){
        yGapHalf_ratio = 0.06
    }else{
        yGapHalf_ratio = 0.11
    }
    // var yGapHalf = pre_close*yGapHalf_ratio
    // return [round(pre_close-yGapHalf), round(pre_close+yGapHalf)]
    return [
        round(Math.min(...pre_closes)-Math.min(...pre_closes)*yGapHalf_ratio),
        round(Math.max(...pre_closes)+Math.max(...pre_closes)*yGapHalf_ratio)
    ]
}
import datetime
import os
import sys
import time

import execjs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import warnings

warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 8)

detail_url = "http://fund.eastmoney.com/pingzhongdata/"


def get_fund_details(fund):
    url = detail_url + fund + ".js"
    params = {
        'v': time.strftime("%Y%m%d%H%M%S", time.localtime())
    }
    response = requests.get(url, params=params).text
    return response


def getWorth(fscode, filepath):
    f = open(filepath, 'a')
    content = get_fund_details(fscode)
    jsContent = execjs.compile(content)

    # 基金名称及代码
    name = jsContent.eval('fS_name')
    code = jsContent.eval('fS_code')

    # 收益率 应用时需要加百分比
    # 近一年收益率
    syl_1n = jsContent.eval('syl_1n')
    # 近6月收益率
    syl_6y = jsContent.eval('syl_6y')
    # 近三月收益率
    syl_3y = jsContent.eval('syl_3y')
    # 近一月收益率
    syl_1y = jsContent.eval('syl_1y')

    # 单位净值走势（及时的交易价值参考）
    netWorthTrend = jsContent.eval('Data_netWorthTrend')
    # 累计净值走势=单位净值+累计分红
    ACWorthTrend = jsContent.eval('Data_ACWorthTrend')

    netWorth = []
    ACWorth = []

    for dayWorth in netWorthTrend[::-1]:
        netWorth.append([time.strftime("%Y-%m-%d", time.localtime(dayWorth['x']/1000)), dayWorth['y'], dayWorth['equityReturn']])

    for dayACWorth in ACWorthTrend[::-1]:
        ACWorth.append([time.strftime("%Y-%m-%d", time.localtime(dayACWorth[0]/1000)), dayACWorth[1]])
    f.write('-----近期收益率-----\n')
    print('近一月收益率: {} \n'.format(syl_1y))
    f.write('近一月收益率: {} \n'.format(syl_1y))
    print('近三月收益率: {}'.format(syl_3y))
    f.write('近三月收益率: {} \n'.format(syl_3y))
    print('近六月收益率: {}'.format(syl_6y))
    f.write('近六月收益率: {} \n'.format(syl_6y))
    print('近一年收益率: {}'.format(syl_1n))
    f.write('近一年收益率: {} \n'.format(syl_1n))
    return netWorth, ACWorth


def save_images(data_frame, index, fund_code, title):
    base_dir = str(os.path.dirname(os.path.realpath(sys.argv[0]))) + "/{}".format(fund_code)
    if os.path.exists(base_dir) is False:
        os.makedirs(base_dir)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    data_frame.index = pd.to_datetime(data_frame.time)
    df = data_frame.drop(['time'], axis=1)

    plt.plot(df.index, df[index])  # 根据数据绘制原走势图
    plt.title(title)
    plt.savefig(base_dir + "/{}-{}.jpg".format(fund_code, title))
    plt.close()


def getMaxDrawdown(x):
    j = np.argmax((np.maximum.accumulate(x) - x) / x)
    if j == 0:
        return 0
    i = np.argmax(x[:j])
    d = (x[i] - x[j]) / x[i] * 100
    return d


def get_max_drawdown_rate(data_frame, index, filename, filepath):
    """
    计算每个月的最大回撤率
    """
    f = open(filepath, 'a')
    res = []

    data_frame.index = pd.to_datetime(data_frame.time)
    df = data_frame.drop(['time'], axis=1)

    # 先按年分组，再按月分组
    for indexs, groupby_year_month in data_frame.groupby([df.index.year, df.index.month]):
        _ = list(groupby_year_month[index].values)  # 各个月份的y值列表

        rate = getMaxDrawdown(groupby_year_month[index].values)

        t = [groupby_year_month.index[0], rate]
        res.append(t)

    # 转DataFrame
    result = pd.DataFrame(res, columns=["date", "rate"])
    # 只保留年月
    result['date'] = result['date'].apply(lambda x: datetime.datetime.strftime(x, "%Y-%m"))
    # 日期列转为索引
    result.index = pd.to_datetime(result['date'])
    # 删除日期列
    result = result.drop(['date'], axis=1)
    # result.to_csv(filename)
    print('成立以来最大回撤率(每月统计)：{}'.format(result.max().values))
    f.write('-----成立以来最大回撤率(每月统计)-----\n')
    f.write('成立以来最大回撤率(每月统计)：{} \n'.format(result.max().values))
    return result


def main(fund_code):
    base_dir = str(os.path.dirname(os.path.realpath(sys.argv[0])))
    filepath = base_dir + "/{}/{}-infos.txt".format(fund_code, fund_code, fund_code)
    nw, aw = getWorth(fund_code, filepath)
    r = pd.DataFrame(nw, columns=["time", "x", "y"])
    # r.to_csv(shareCode + '.csv', index=True, header=False)
    r1 = pd.DataFrame(aw, columns=["time", "aw"])
    # pd.concat([r, r1], axis=1).to_csv(fund_code + '.csv', index=True, header=False)
    get_max_drawdown_rate(r, 'x', '{}-最大回撤率.csv'.format(fund_code), filepath)
    save_images(r1, 'aw', fund_code, "累计净值走势图")
    save_images(r, 'x', fund_code, "单位净值走势图")
    plt.close()


if __name__ == '__main__':
    shareCode = "519732"
    main(shareCode)
    pass

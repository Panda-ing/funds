import json
import os
import sys
import time
import requests
import pandas as pd
import configparser
import fund_detail_info

GREEN = '\033[32m'
RED = '\033[31m'
WHITE = '\033[37m'
RESET = '\033[0m'
FONT = "| font='Menlo'"


def change_color(num):
    color = RESET
    if num < 0:
        color = GREEN + '▼'
    if num > 0:
        color = RED + '▲'
    colored_change = color + '{:.2f}'.format(num) + '% ' + RESET
    return colored_change


def get_fund_base_info(fund_code):
    """
    获取基金当天净值、估值信息
    :param fund:
    :return:
    """
    base_info_url = "http://fundgz.1234567.com.cn/js/"
    url = '{}{}.js?rt={}'.format(base_info_url, fund_code, time.strftime("%Y%m%d%H%M%S", time.localtime()))
    response = requests.get(url).text[8:][:-2]
    j = json.loads(response)
    rate = float(j['gszzl'])
    print("---")

    colored_change = change_color(rate)

    print('[{}]{}: {}'.format(j['fundcode'], j['name'], colored_change))
    f.write('[{}]{}: {}'.format(j['fundcode'], j['name'], rate) + "\n")
    f.write('-----净值、估值信息-----\n')
    print("--基金名称: %s | color=white" % j['name'])
    f.write("基金名称: %s" % j['name'] + "\n")
    print("--基金代码: %s | color=white" % j['fundcode'])
    f.write("基金代码: %s" % j['fundcode'] + "\n")
    print("--单位净值: %s | color=white" % j['dwjz'])
    f.write("单位净值: %s" % j['dwjz'] + "\n")
    print("--净值日期: %s | color=white" % j['jzrq'])
    f.write("净值日期: %s" % j['jzrq'] + "\n")
    print("--估算净值: %s | color=white" % j['gsz'])
    f.write("估算净值: %s" % j['gsz'] + "\n")
    print("--估算增长率: %s | color=white" % j['gszzl'])
    f.write("估算增长率: %s" % j['gszzl'] + "\n")
    print("--估值日期: %s | color=white" % j['gztime'])
    f.write("估值日期: %s" % j['gztime'] + "\n")


def get_details_info(fund_code):
    """
    获取基金特色指标数据： 标准差、夏普率
    :param fund_code:
    :return:
    """
    url = 'http://fundf10.eastmoney.com/tsdata_{}.html'.format(fund_code)

    r = pd.read_html(url)
    risk_indicators = r[1]
    tracking_index = r[2]
    # print("--" + risk_indicators.head(1).to_string())
    f.write('-----特色指标数据-----\n')
    for index, row in risk_indicators.iterrows():
        ds = row.to_dict()
        print("--" + str(ds).replace("{", "").replace("}", "").replace("'", "").replace(",", ";"))
        f.write(str(ds).replace("{", "").replace("}", "").replace("'", "").replace(",", ";") + "\n")

    for index, row in tracking_index.iterrows():
        ds = row.to_dict()
        print("--" + str(ds).replace("{", "").replace("}", "").replace("'", "").replace(",", ";"))
        f.write(str(ds).replace("{", "").replace("}", "").replace("'", "").replace(",", ";") + "\n")


def get_fund_manager_info(fund_code):
    """
    获取基金经理信息
    :param fund_code:
    :return:
    """
    url = 'http://fundf10.eastmoney.com/jjjl_{}.html'.format(fund_code)
    managers_info = pd.read_html(url)[1].head(1).to_dict('records')
    f.write('-----基金经理信息-----\n')
    for i in managers_info:
        print("--" + str(i).replace("{", "").replace("}", "").replace("'", "").replace(",", ";"))
        f.write(str(i).replace("{", "").replace("}", "").replace("'", "").replace(",", ";") + "\n")


def get_owners_info(fund_code):
    """
    获取基金持有人数据
    :param fund_code:
    :return:
    """
    url = 'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=cyrjg&code={}.html'.format(fund_code)

    owners_info = pd.read_html(url, encoding='utf-8')
    f.write('-----基金持有人数据-----\n')
    print("--" + str(owners_info[0].head(1).to_dict('records')[0]).replace("{", "").replace("}", "").replace("'", "").replace(",", ";"))
    f.write(str(owners_info[0].head(1).to_dict('records')[0]).replace("{", "").replace("}", "").replace("'", "").replace(",", ";") + "\n")


if __name__ == '__main__':
    print("start test~")
    base_dir = str(os.path.dirname(os.path.realpath(sys.argv[0])))

    print(base_dir)
    file_path = base_dir + "/config.ini"
    print(file_path)
    cf = configparser.ConfigParser()
    cf.read(file_path)
    funds = eval(cf.get('fund', 'codes'))
    print(funds)
    for fund in funds:
        if os.path.exists(base_dir + "/{}".format(fund)) is False:
            os.makedirs(base_dir + "/{}".format(fund))
        f = open(base_dir + "/{}/{}-infos.txt".format(fund, fund), 'a')
        get_fund_base_info(fund)
        get_details_info(fund)
        get_fund_manager_info(fund)
        get_owners_info(fund)
        f.flush()
        fund_detail_info.main(fund)


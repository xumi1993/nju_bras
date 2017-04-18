#!/usr/bin/env python
# coding=utf-8
import requests
import json
import sys
import getpass
import os
import ConfigParser
import argparse as ap
import argcomplete

OKGREEN = '\033[92m'
FAIL = '\033[91m'
WARNING = '\033[93m'
ENDC = '\033[0m'

login_url = 'http://p.nju.edu.cn/portal_io/login'
logout_url = 'http://p.nju.edu.cn/portal_io/logout'
volume_url = 'http://p.nju.edu.cn/portal_io/selfservice/volume/getlist'
getinfo_url = 'http://p.nju.edu.cn/portal_io/getinfo'
headers = {'Accept-Encoding': "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            'Host': 'p.nju.edu.cn',
            'Origin': 'http://p.nju.edu.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://p.nju.edu.cn/portal/index.html',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko), Chrome/57.0.2987.133 Safari/537.36"}


description = "This is Python script to login NJU Bras in Shell"
help = "login: Login NJU Bras; " \
       "logout: Logout NJU Bras; "\
       "show: List Account information; "\
       "clear: Clear cache of user info; "


def save_userinfo(username, passwd):
    cf = ConfigParser.ConfigParser()
    cf.add_section('global')
    cf.set('global', 'username', username)
    cf.set('global', 'password', passwd)
    try:
        cf.write(open(os.environ['HOME']+"/.nju_bras.conf", "w"))
        print u'用户信息已保存'
    except:
        print FAIL+u'无法打开 '+os.environ['HOME']+"/.nju_bras.conf"+ENDC
        sys.exit(1)


def input_userinfo():
    cf = ConfigParser.ConfigParser()
    path = os.environ['HOME']+'/.nju_bras.conf'
    if os.path.isfile(path):
        try:
            cf.read(path)
            username = cf.get('global', 'username')
            passwd = cf.get('global', 'password')
            besave = False
            return username, passwd, besave
        except:
            pass
    username = raw_input("Input username:")
    passwd = getpass.getpass()
    besave = True
    return username, passwd, besave


def login(username, passwd):
    iserr = False
    s = requests.Session()
    data = {'username': username, 'password': passwd}
    try:
        res1 = s.post(login_url, data=data, headers=headers, timeout=5)
    except requests.ConnectTimeout:
        print FAIL+u"错误：连接"+headers['Host']+u"超时"+ENDC
        sys.exit(1)
    reply = json.loads(res1.text)['reply_msg']
    if reply == u"已登陆!":
        iserr = True
        print WARNING+u"账户已登录"+ENDC
    elif reply == u"登录成功!":
        print OKGREEN+u"登录成功"+ENDC
    else:
        iserr = True
        print FAIL+u"错误："+reply+ENDC
    return iserr


def logout():
    s = requests.Session()
    try:
        res1 = s.post(logout_url, headers=headers, timeout=5)
    except requests.ConnectTimeout:
        print FAIL+u"错误：登出超时"+ENDC
        sys.exit(1)
    reply = json.loads(res1.text)['reply_msg']
    print OKGREEN+reply+ENDC


def show_msg():
    s = requests.Session()
    try:
        res_volume = s.post(volume_url, headers=headers, timeout=5)
        res_getinfo = s.post(getinfo_url, headers=headers, timeout=5)
    except requests.ConnectTimeout:
        print FAIL+u"错误：连接"+headers['Host']+u"超时"+ENDC
        sys.exit(1)
    use_time = json.loads(res_volume.text)['rows'][0]['total_ipv4_volume']
    use_time_hour = use_time // 3600
    use_time_min = use_time % 3600 // 60
    use_time_str = u"%d小时%d分" % (use_time_hour, use_time_min)
    fullname = json.loads(res_getinfo.text)['userinfo']['fullname']
    service_name = json.loads(res_getinfo.text)['userinfo']['service_name']
    area_name = json.loads(res_getinfo.text)['userinfo']['area_name']
    try:
        balance = float(json.loads(res_getinfo.text)['userinfo']['balance'])/100
    except:
        balance = json.loads(res_getinfo.text)['userinfo']['balance']
    print u'用户名：', fullname
    print u'所在区域：', area_name
    print u'所选服务：', service_name
    print u"账户余额：%s元\n累计时长：%s" % (balance, use_time_str)


if __name__ == '__main__':
    parser = ap.ArgumentParser(description=description)
    parser.add_argument('pos', help=help, choices=['login', 'logout', 'show', 'clear'])
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.pos == 'login':
        (username, passwd, besave) = input_userinfo()
        iserr = login(username, passwd)
        if besave and not iserr:
            issave = raw_input("是否保存用户名与密码？[y/n] ")
            while True:
                if issave.lower() == 'y':
                    save_userinfo(username, passwd)
                    break
                elif issave.lower() == 'n':
                    break
                else:
                    issave = raw_input("跳过，请输入[y/n]")
                    continue
    elif args.pos == 'logout':
        logout()
    elif args.pos == 'show':
        show_msg()
    elif args.pos == 'clear':
        os.remove(os.environ['HOME'] + '/.nju_bras.conf')
    else:
        print FAIL+"Error: Wrong argument"+ENDC
        sys.exit(1)

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
    检测文件中cookie是否有效
    只兼容Python3
'''
import requests
import json
import re


def test():
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    url = 'https://pan.baidu.com/disk/home?#/all?path=%2F&vmode=list'

    with open('baiducookie.json','r') as f:
        cookies = json.load(f)

    session = requests.session()
    for cookie in cookies:
        session.cookies.set(cookie['name'],cookie['value'])

    try:
        r = session.get(url,headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return bool(re.findall('百度网盘-全部文件',r.text))
    except:
        return False


if __name__ == '__main__':
    test()
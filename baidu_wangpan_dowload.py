#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Python附带登录模块,cookie检测模块以及文件列表模块的获取下载链接并调用IDM下载器进行下载
    只兼容Python3
'''
import re
import time
import json
import random
import datetime
import requests
import threading
import tkinter as tk
from subprocess import call
from base64 import b64encode
from testCookie import test
from tkinter import messagebox
from Baidulogin import BaiduLogin
from urllib.parse import urlencode

HEADERS = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                 '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

HEADERS1 = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-AU;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Length': '70',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'pan.baidu.com',
    'Origin': 'https://pan.baidu.com',
    'Referer': 'https://pan.baidu.com/disk/home?',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


class Baidudlink(object):
    def __init__(self, filepath=r'E:\download'):
        """
        初始化窗口
        :param filepath:
        """
        self.window = tk.Tk()
        self.window.title('get the url')
        self.window.geometry('750x600')

        self.var = tk.StringVar()

        tk.Label(self.window, text='输入路径: ' ,width=20).grid(row=0, column=0)
        tk.Label(self.window, text='文件列表: ', width=20).grid(row=1, column=0, sticky=tk.N)
        tk.Label(self.window,text='文件名: ', width=20).grid(row=2, column=0)
        tk.Label(self.window,text='真实地址: ', width=20).grid(row=3, column=0)

        self.text1 = tk.Text(self.window, width=70, height=1)
        self.text1.grid(row=0, column=1)

        self.listbox = tk.Listbox(self.window, listvariable=self.var, width=70, height=20)
        self.listbox.grid(row=1, column=1)

        self.entry2 = tk.Entry(self.window, width=70)
        self.entry2.grid(row=2, column=1)

        self.text = tk.Text(self.window, width=70, height=5)
        self.text.grid(row=3, column=1)

        self.btn = tk.Button(self.window, text='获取列表', width=10, command=self.threadlist)
        self.btn.grid(row=4, column=1)

        self.btn1 = tk.Button(self.window, text='开始下载', command=self.threaddownload)
        self.btn1.grid(row=4, column=2)

        self.headers = HEADERS
        self.filepath = filepath
        self.query1 = urlencode({'dir': '/'})
        self.dict_list = []
        self.session = requests.session()
        self.initCookie()
        self.bdstoken = self.getbdstoken()

        self.window.mainloop()

    def initCookie(self):
        """
        初始化cookie
        :return: None
        """
        with open('baiducookie.json', 'r') as f:
            cookies = json.load(f)

        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])

    def getbdstoken(self):
        """
        获得页面的bdstoken
        :return: bdstoken
        """
        url = 'https://pan.baidu.com/disk/home?#/all?path=%2F&vmode=list'
        try:
            r = self.session.get(url, headers=self.headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return re.findall(r'"bdstoken":"(.*?)",', r.text)[0]
        except:
            print('fail_1')

    def getfilelist(self):
        """
        将网盘中的列表导出来
        :return: None
        """
        if self.text1.get(1.0, tk.END).strip() != '':
            path = self.dict_list[int(self.listbox.get(self.listbox.curselection())[0])]['path']
            self.text1.delete(0.0, tk.END)
            self.text1.insert('end', path)
            self.query1 = urlencode({'dir': path})
        self.text1.insert('end', '/')

        url = 'https://pan.baidu.com/api/list?%s&bdstoken=%s&logid=MTUzNDc0Mjg0MTUyNjAuOTMxMDgxMjYyMTUzOTI2NA==&num=' \
              '100&order=time&desc=0&clienttype=0&showempty=0&web=1&page=1&channel=chunlei&web=1&app_id=250528' % \
              (self.query1, self.bdstoken)
        filelist = []

        try:
            r = self.session.get(url, headers=self.headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            i = 0
            self.dict_list = []
            if not r.json()['list']:
                messagebox.showerror(message='这不是目录')
            else:
                for item in r.json()['list']:
                    dict_item = dict()
                    dict_item['path'] = item['path']
                    dict_item['fs_id'] = item['fs_id']
                    self.dict_list.append(dict_item)
                    filelist.append(str(i) + '.  ' + item['server_filename'])
                    i += 1
                self.var.set(filelist)
        except:
            messagebox.showerror(message='获取列表出现错误')
            self.window.destroy()

    def getpubliclink(self):
        """
        获得公开分享的链接
        :return:
        """
        # get the logid
        f_logid = str(int(time.time() * 1000)) + str(random.random())
        logid = b64encode(f_logid.encode('utf-8')).decode('utf-8')

        url = 'https://pan.baidu.com/share/set?channel=chunlei&clienttype=0&web=1&channel=chunlei&web=1&app_id=250528' \
              '&bdstoken=%s&logid=%s&clienttype=0' % (self.bdstoken, logid)
        id = [self.dict_list[int(self.listbox.get(self.listbox.curselection())[0])]['fs_id']]

        data = {
            'fid_list': id,
            'schannel': 0,
            'channel_list': [],
            'period': 0
        }
        data = urlencode(data)  # data需要编码

        try:
            req = self.session.post(url, headers=HEADERS1, data=data)
            if req.json()['errno'] == 115:
                messagebox.showerror(message='该文件禁止分享')
            return req.json()['link']
        except:
            messagebox.showerror(message='获取公开链接出现错误')
            self.window.destroy()

    def getdlink(self):
        """
        取得网盘资源的真实下载地址,该处调用了机领网的api
        :return:
        """
        # get the today param
        today = '52' + datetime.date.today().strftime('%m%d') + '1'
        query = dict()
        query['jlwzcn'] = today
        query['url'] = self.getpubliclink()
        url = 'https://jlwz.cn/api/baidu.php?' + urlencode(query)  # 调用了机领网的api

        print(url)

        try:
            r = requests.get(url, headers=self.headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            print(r.json())
            if r.json()['errno'] == 0:
                self.text.insert('end', r.json()['list'][0]['dlink'])
                self.useidm(r.json()['list'][0]['dlink'])
                messagebox.showinfo(message='已加入idm下载队列')
            else:
                messagebox.showwarning(message=r.json()['errmsg'])

            self.window.destroy()
        except:
            messagebox.showerror(message='获取真实链接出现错误')
            self.window.destroy()

    def useidm(self, url):
        """
        使用本地idm下载器进行下载
        :param url:
        :return: None
        """
        call(['IDMan.exe', '/d', url, '/p', self.filepath, '/f', self.entry2.get(),'/n', '/a'])

    def threadlist(self):
        """
        防止界面卡死,另开线程执行获取文件列表操作
        :return: None
        """
        t = threading.Thread(target=self.getfilelist, args=())
        t.setDaemon(True)
        t.start()

    def threaddownload(self):
        """
        另开线程执行下载操作
        :return:
        """
        t = threading.Thread(target=self.getdlink, args=())
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    if test():
        Baidudlink()
    else:
        BaiduLogin()

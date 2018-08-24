#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    进行登录操作,对验证码的刷新卡死尚未解决
    需要安装PhantomJS
    只兼容Python3
'''
import time
import json
import threading
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BaiduLogin(object):
    def __init__(self, filepath = 'E://captcha_pic.png'):
        """
        初始化窗口
        :param filepath:
        """
        self.window = tk.Tk()
        self.window.title('登录百度网盘')
        self.window.geometry('450x150')

        tk.Label(self.window, text='username: ').grid(row=0, column=0)
        tk.Label(self.window, text='password: ').grid(row=1, column=0)

        self.label = tk.Label(self.window)
        self.label.grid(row=2, column=2)

        self.entry1 = tk.Entry(self.window, width=30)
        self.entry1.grid(row=0, column=1)

        self.entry2 = tk.Entry(self.window, width=30)
        self.entry2.grid(row=1, column=1)

        self.entry3 = ""
        self.entry4 = ""

        self.btn = tk.Button(self.window, text='login', width=7)
        self.btn.grid(row=4, column=1)

        self.btn.bind("<Button-1>", self.phone_captcha)
        self.window.bind("<Return>", self.phone_captcha)

        self.url = 'https://pan.baidu.com/'

        #chrome_options = Options()
        #chrome_options.add_argument('--headless')
        #chrome_options.add_argument('--disable-gpu')
        #self.browser = webdriver.Chrome(chrome_options=chrome_options)

        self.browser = webdriver.PhantomJS()
        self.wait = WebDriverWait(self.browser, 20)
        self.filepath = filepath

        self.window.mainloop()

    def login(self):
        """
        主要登录函数
        :return: None
        """
        # 取得页面
        self.browser.get(self.url)
        self.browser.maximize_window()
        ctx = self.wait.until(EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_4__footerULoginBtn')))
        ctx.click()
        self.browser.implicitly_wait(10)

        # 获得网页中节点
        name_field = self.browser.find_element_by_id('TANGRAM__PSP_4__userName')
        name_field.send_keys(self.entry1.get())
        password_field = self.browser.find_element_by_id('TANGRAM__PSP_4__password')
        password_field.send_keys(self.entry2.get())
        btn = self.browser.find_element_by_id('TANGRAM__PSP_4__submit')
        btn.click()
        time.sleep(2)
        captcha_holder = self.browser.find_element_by_id('TANGRAM__PSP_4__verifyCodeImgWrapper')
        captcha_input = self.browser.find_element_by_id('TANGRAM__PSP_4__verifyCode')

        if captcha_holder.is_displayed():
            self.entry3 = tk.Entry(self.window, width=30)
            self.entry3.grid(row=2, column=1, sticky=tk.W)

            btn2 = tk.Button(self.window, text='change')
            btn2.grid(row=2, column=3)

            messagebox.showinfo(message='请输入验证码')

            # 等待网页渲染
            time.sleep(5)

            # 网页图片截取验证码
            self.get_captcha()

            # 手动输入验证码
            btn2.bind('<Button-1>', self.chg_captcha)
            while True:
                if len(self.entry3.get()) >= 2:
                    break
            time.sleep(30)
            messagebox.showwarning(message='输入时间到')
            captcha_input.send_keys(self.entry3.get())
            btn.click()
            time.sleep(2)

            # 验证码有误
            if self.browser.title == '百度网盘，让美好永远陪伴':
                while self.browser.find_element_by_id('TANGRAM__PSP_4__error').text == '您输入的验证码有误':
                    self.get_captcha()
                    self.entry3.delete(0, tk.END)
                    btn2.bind('<Button-1>', self.chg_captcha)
                    while True:
                        if self.entry3.get():
                            break
                    time.sleep(30)
                    messagebox.showwarning(message='输入时间到')
                    captcha_input.send_keys(self.entry3.get())
                    btn.click()
                    time.sleep(2)

        # 手机验证码
        if self.browser.title == '百度网盘，让美好永远陪伴':
            tk.Label(self.window, text='phonecap: ').grid(row=3, column=0)

            messagebox.showinfo(message='请输入手机验证码')

            self.entry4 = tk.Entry(self.window, width=30)
            self.entry4.grid(row=3, column=1, sticky=tk.W)

            mobile_captcha = self.browser.find_element_by_id('TANGRAM__27__button_send_mobile')
            mobile_captcha.click()
            mobile_input = self.browser.find_element_by_id('TANGRAM__27__input_vcode')
            while True:
                if len(self.entry4.get()) == 6:
                    break
            mobile_input.send_keys(self.entry4.get())
            mobile_btn = self.browser.find_element_by_id('TANGRAM__27__button_submit')
            mobile_btn.click()
            time.sleep(5)

        if self.browser.title != '百度网盘，让美好永远陪伴':
            messagebox.showinfo(message='登陆成功')

            with open('baiducookie.json', 'w') as f:
                json.dump(self.browser.get_cookies(), f)

            self.window.destroy()

    def chg_captcha(self, event):
        """
        响应按钮修改验证码事件
        :param event:
        :return: None
        """
        change_captcha = self.browser.find_element_by_id('TANGRAM__PSP_4__verifyCodeChange')
        change_captcha.click()
        time.sleep(2)
        self.get_captcha()
        self.entry3.delete(0, tk.END)
        while True:
            if len(self.entry3.get()) >= 2:
                break
        time.sleep(30)
        messagebox.showwarning(message='输入时间到')

    def phone_captcha(self, event):
        """
        另开一线程执行login耗时操作
        :param event:
        :return: None
        """
        t = threading.Thread(target=self.login, args=())
        t.setDaemon(True)
        t.start()

    def get_captcha(self):
        """
        获得验证码图片
        :return:
        """
        pic = self.wait.until(EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_4__verifyCodeImg')))
        self.browser.get_screenshot_as_file(self.filepath)
        img_location = pic.location
        img_size = pic.size
        left = img_location['x']
        top = img_location['y']
        right = img_size['width'] + left
        bottom = img_size['height'] + top
        img = Image.open(self.filepath).crop((left, top, right, bottom))
        img.show()
        #photo = ImageTk.PhotoImage(img)
        #self.label.configure(image=photo)


if __name__ == '__main__':
    filepath = 'E://captcha_pic.png'
    BaiduLogin(filepath)

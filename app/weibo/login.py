#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (c) 2013 Qin Xuye <qin@qinxuye.me>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on 2013-6-8

@author: Chine
'''

import urllib
import base64
import binascii
import re
import json
import time

from cola.core.errors import DependencyNotInstalledError,\
                             LoginFailure

try:
    import rsa
except ImportError:
    raise DependencyNotInstalledError("rsa")

class WeiboLoginFailure(LoginFailure): pass

class WeiboLogin(object):
    def __init__(self, opener, username, passwd):
        self.opener = opener
        
        self.username = username
        self.passwd = passwd
        
    def get_user(self, username):
        username = urllib.quote(username)
        return base64.encodestring(username)[:-1]
    
    def get_passwd(self, passwdOrAuthcode, pubkey, servertime, nonce):
        #old way to encrypt data
        """
        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)
        passwd = rsa.encrypt(message, key)
        return binascii.b2a_hex(passwd)
        """
        #new way to encrypt data
        from rsakey import RSAKey
        str_to_encrypt = '\t'.join([str(servertime), str(nonce)]) + '\n' + str(passwdOrAuthcode)
        instance_RSAKey = RSAKey()
        instance_RSAKey.setPublic(str(pubkey),'10001')
        ret = instance_RSAKey.encrypt(str_to_encrypt)
        return ret
    
    def prelogin(self):
        username = self.get_user(self.username)
        """
        http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTg5OTQwNDczNDc%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1449313390024
        """
        prelogin_url = \
        'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=%s'\
           % (username, int(time.time()*1000))
        data = self.opener.open(prelogin_url)
        regex = re.compile('\((.*)\)')
        try:
            json_data = regex.search(data).group(1)
            data = json.loads(json_data)
            """
            me.setServerTime(a.servertime);
            me.nonce = a.nonce;
            me.rsaPubkey = a.pubkey;
            me.rsakv = a.rsakv;
            """
            rst = str(data['servertime']), data['nonce'], \
                data['pubkey'], data['rsakv'], data['smsurl']
            return rst
        except:
            raise WeiboLoginFailure
        
    def login(self):
        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        try:
            servertime, nonce, pubkey, rsakv ,smsurl = self.prelogin()
            """
            http://login.sina.com.cn/sso/msglogin?entry=weibo&mobile=18994047347&s=df0a18a510db06f79088aec6743bd592&_t=1&callback=STK_144931247434416
            """
            smsurl += "&_t=1&callback=STK_%s1" % int(time.time()*1000)
            print smsurl
            data = self.opener.open(smsurl)
            #receiving sms by your mobile
            print data
            authcode = raw_input('输入接受到的短信验证码:\n')
            #TODO:使用最新的签名方法计算表单数据签名
            postdata = {
              'entry': "weibo",
              'gateway': '1',
              'from': '',
              'savestate': '7',
              'userticket': '1',
              'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F",
              'cfrom' : '1',
              'vsnf': '1',
              'su': self.get_user(self.username),
              'service': 'miniblog',
              'servertime': servertime,
              'nonce': nonce,
              'pwencode': 'rsa2',
              'rsakv': rsakv,
              'sp': self.get_passwd(authcode, pubkey, servertime, nonce),
              'sr': "1440*900",
              'encoding': 'UTF-8',
              'prelt': '99',
              'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
              'returntype': 'META'
            }
            postdata = urllib.urlencode(postdata)
            text = self.opener.open(login_url, postdata)
            print text
            # Fix for new login changed since about 2014-3-28
            ajax_url_regex = re.compile('location\.replace\(\'(.*)\'\)')
            matches = ajax_url_regex.search(text)
            if matches is not None:
                ajax_url = matches.group(1)
                print ajax_url
                text = self.opener.open(ajax_url)
                print text
            
            regex = re.compile('\((.*)\)')
            json_data = json.loads(regex.search(text).group(1))
            result = json_data['result'] == True
            if result is False and 'reason' in json_data:
                return result, json_data['reason']
            return result
            """
              entry:weibo
              gateway:1
              from:
              savestate:7
              useticket:1
              pagerefer:http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F
              cfrom:1
              vsnf:1
              su:MTg5OTQwNDczNDc=
              service:miniblog
              servertime:1449586833
              nonce:HS9K26
              pwencode:rsa2
              rsakv:1330428213
              sp:642e86646dae0ef42e912997a6d666a56a425b55b04dda645fa73a1d5df8247d099f80547738373e96787a1cd8b1a13f400bec9bff6eca95aec704e5d654b8b19b4c2bb44549d58349b584e0325b29d4dcccf14b102f4c93f8be94fcac170d2dab6d5d735bf84abc686ff1bebf22cf510fc628fbe3b4abc1636d53e829541d1b
              sr:1440*900
              encoding:UTF-8
              prelt:99
              url:http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack
              returntype:META
            """
        except WeiboLoginFailure:
            return False
            """
            postdata = {
                'entry': 'weibo',
                'gateway': '1',
                'from': '',
                'savestate': '7',
                'userticket': '1',
                'ssosimplelogin': '1',
                'vsnf': '1',
                'vsnval': '',
                'su': self.get_user(self.username),
                'service': 'miniblog',
                'servertime': servertime,
                'nonce': nonce,
                'pwencode': 'rsa2',
                'sp': self.get_passwd(self.passwd, pubkey, servertime, nonce),
                'encoding': 'UTF-8',
                'prelt': '115',
                'rsakv' : rsakv,
                'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&amp;callback=parent.sinaSSOController.feedBackUrlCallBack',
                'returntype': 'META'
            }
            postdata = urllib.urlencode(postdata)
            text = self.opener.open(login_url, postdata)
            # Fix for new login changed since about 2014-3-28
            ajax_url_regex = re.compile('location\.replace\(\'(.*)\'\)')
            matches = ajax_url_regex.search(text)
            if matches is not None:
                ajax_url = matches.group(1)
                print ajax_url
                text = self.opener.open(ajax_url)
                print text
            
            regex = re.compile('\((.*)\)')
            json_data = json.loads(regex.search(text).group(1))
            result = json_data['result'] == True
            if result is False and 'reason' in json_data:
                return result, json_data['reason']
            return result
        except WeiboLoginFailure:
            return False
            """

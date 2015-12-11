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

Created on 2013-6-7

@author: Chine
'''

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cola.core.opener import MechanizeOpener
from cola.core.urls import Url, UrlPatterns
from cola.job import JobDescription

from login import WeiboLogin
from parsers import MicroBlogParser, ForwardCommentLikeParser,\
                    UserInfoParser, UserFriendParser
from conf import starts, user_config, instances, cookies_filename
from bundle import WeiboUserBundle

def login_hook(opener, **kw):
    username = str(kw['username'])
    passwd = str(kw['password'])
    
    loginer = WeiboLogin(opener, username, passwd)
    return loginer.login()

url_patterns = UrlPatterns(
    Url(r'http://weibo.com/aj/mblog/mbloglist.*', 'micro_blog', MicroBlogParser),
    Url(r'http://weibo.com/aj/.+/big.*', 'forward_comment_like', ForwardCommentLikeParser),
    Url(r'http://weibo.com/\d+/info', 'user_info', UserInfoParser),
    Url(r'http://weibo.com/\d+/follow.*', 'follows', UserFriendParser),
    Url(r'http://weibo.com/\d+/fans.*', 'fans', UserFriendParser)
)

def get_job_desc():
    return JobDescription('sina weibo crawler', url_patterns, MechanizeOpener, user_config, 
                          starts, unit_cls=WeiboUserBundle, login_hook=login_hook)
    
if __name__ == "__main__":

    """
    from cola.context import Context
    ctx = Context(local_mode=True)
    ctx.run_job(os.path.dirname(os.path.abspath(__file__)))
    """
    #新的短信验证方式，不支持多线程同时登陆，会造成发生短信颜值码频率太高的错误，所以先使用单线程的方式实现
    uname = str(user_config['job']['login'][0]['username'])
    passwd = str(user_config['job']['login'][0]['password'])
    
    user_agent = """
    Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36"""
    cookie = """SINAGLOBAL=122.234.236.211_1449673121.694525; Apache=122.234.236.211_1449673121.694527;
    SUB=_2AkMhNM6Vf8NhqwJRmPoUxW_naItzygjEiebDAH_sJxJjHlEO7FBtRgGyzabhoI02ECY9_U0P29jX;
    SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWu0sYw.Q-ey7_1U9OXyjuM; ULOGIN_IMG=gz-fcc5afecc7602110ffffd666df9d024f0051"""

    cookies_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), cookies_filename) 
    opener = MechanizeOpener(user_agent=user_agent, cookie_filename=cookies_filename)
    #opener.browser.addheaders = [('User-agent',user_agent),('Connection','keep-alive'),('Cookie',cookie)]
    opener.browser.addheaders = [('User-agent',user_agent),('Connection','keep-alive')]
    loginer = WeiboLogin(opener,uname,passwd)
    #TODO:尝试直接使用上次的cookie，不重新登录...
    #is_need_login = False
    is_need_login = True
    if not is_need_login or loginer.login() == True:
      msg = """已经成功登录微博，请继续使用opener对象访问微博的其他页面，比如:\n
  response = opener.open('URL地址','要提交的数据，请先用urllib.urlencode进行编码')
      """
      try:
        from IPython import embed
        embed(banner2 = msg)
      except ImportError:
        import code
        code.interact(msg, local=globals())
    else:
      print '登录失败，每天发送验证短信的次数只有4-5次'

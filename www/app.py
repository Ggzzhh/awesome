#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Ggzzhh'

import logging; logging.basicConfig(level=logging.INFO) # 设置日志配置 

import asyncio, os, json, time # josn用于解析或转换为josn格式 josn可在不同平台之间进行数据交换
from datetime import datetime # 导入时间模块

from aiohttp import web # aiohttp 是基于asyncio实现的http框架 
# 因此可以用单线程+coroutine实现多用户的高并发支持。

def index(request):
	return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')

async def init(loops):
	app = web.Application(loop=loop)
	app.router.add_route('GET', '/', index)
	srv = await loops.create_server(app.make_handler(), '127.0.0.1', 9000)
	logging.info('server started at http://127.0.0.1:9000')
	return srv
	
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


























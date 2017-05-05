#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Ggzzhh'

import asyncio, logging

import aiomysql

# 打印SQL语句
def log(sql, args=()):
	logging.info('执行的SQL语句: %s' % sql)


# 创建连接池 连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务：
async def create_pool(loop, **kw):
	logging.info('创建连接池--连接mysql数据库')
	global __pool # 创建全局变量__pool
	__pool = await aiomysql.create_pool(
		# 连接这个函数需要最少传入user password db 三个参数 其余等同于有默认值
		host=kw.get('host', 'localhost'), # 默认本机ip
		port=kw.get('port', 3306), # 网络接口是3306 
		user=kw['user'] ,
		password=kw['password'],
		db=kw['db'],
		charset=kw.get('charset', 'utf8'), 
		autocommit=kw.get('autocommit', True), # 自动提交 True
		maxsize=kw.get('maxsize', 10), # 默认最大连接数为10
		minsize=kw.get('minsize', 1),
		loop=loop # 接收一个消息线程实例
	)
	
# 封装SQL SELECT为 select函数 需要传入sql语句跟sql参数 返回查询结果
async def select(sql, args, size=None):

	'''SQL语句的占位符是?，而MySQL的占位符是%s，select()函数在内部自动替换。
	注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。
	注意到await将调用一个子协程（也就是在一个协程中调用另一个协程）并直接获得子协程的返回结果
	如果传入size参数，就通过fetchmany()获取最多指定数量的记录，
	否则，通过fetchall()获取所有记录。'''
	
	log(sql, args) # 打印sql语句 属性
	global __pool
	with (await __pool) as conn:  # 建立数据库连接
		# 接收数据库返回的数据 用字典的形式 ({xxx：xx}})
		cur = await conn.cursor(aiomysql.DictCursor) 
		# 异步执行sql语句  把？替换为%s
		await cur.execute(sql.replace('?','%s'), args or ())
		if size:
			# 返回size条查询结果
			rs = await cur.fetchmany(size) 
		else:
			rs = await cur.fetchall()
		await cur.close()
		logging.info('返回行数: %s' % len(rs))
		return rs
		
# 要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的execute()函数，
# 因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数：
# execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。
async def execute(sql, args):
	log(sql)
	with (await __pool) as conn:
		try:
			# execute类型的SQL操作返回的结果只有行号，所以不需要用DictCursor
			cur = await conn.cursor()
			await cur.execute(sql.replace('?', '%s'), args)
			affected = cur.rowcount
			await cur.close()
		except BaseException as e:
			raise e
		return affected

# 根据输入的参数生成占位符列表
def create_args_string(num):
	L = []
	for n in range(num):
		L.append('?')
	# 以,为分隔符， 将列表合成字符串
	return (','.join(L))
		
# 定义Field类， 负责保存（数据库）表的字段名和类型
class Field(object):
	# 表的字段包含字段名，字段类型， 是否为主键， 默认值
	def __init__(self, name, column_type, primary_key, default):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default
		
	# 当打印Field类时，返回:类名，字段类型和名字
	def __str__(self):
		return ('<%s, %s: %s>' % (self.__class__.__name__, self.column_type, self.name))

# 字符串类型的默认长度为100
class StringField(Field):
	
	def __init__(self, name=None, primary_key=False, default=None, dd1='varchar(100)'):
		super().__init__(name, dd1, primary_key, default)
		
# 布尔类型的field 类型为布尔
class BooleanField(Field):
	
	def __init__(self, name=None, default=None):
		super().__init__(name, 'boolean', False, default)
		
# 整数类型的默认值为0 类型是长整型
class IntegerField(Field):
	
	def __init__(self, name=None, primary_key=False, default=0):
		super().__init__(name, 'bigint', primary_key, default)

# 文本类型默认为文本
class TextField(Field):
	
	def __init__(self, name=None, default=None):
		super().__init__(name, 'text', False, default)
		
# 浮点类型的默认值为0.0 类型是real
class IntegerField(Field):
	
	def __init__(self, name=None, primary_key=False, default=0.0):
		super().__init__(name, 'real', primary_key, default)



# 定义Model的元类

# 所有的元类都继承自type
# ModelMetaclass元类定义了所有Model基类(继承ModelMetaclass)的子类实现的操作
 
# -*-ModelMetaclass的工作主要是为一个数据库表映射成一个封装的类做准备：
# ***读取具体子类(user)的映射信息
# 创造类的时候，排除对Model类的修改
# 在当前类中查找所有的类属性(attrs)，如果找到Field属性，
# 就将其保存到__mappings__的dict中，同时从类属性中删除Field(防止实例属性遮住类的同名属性)
# 将数据库表名保存到__table__中
 
# 完成这些工作就可以在Model中定义各种数据库的操作方法








# Redistr API 参考文档 #

[API Docs](API.md)

## BaseStructure 类 ##

此类是所有数据结构类的亲本类，构建时需要两个参数，第二个参数(token)不是必要的。

头: `BaseStructure(redis, token = None)`

```python
from redistr import BaseStructure
from redis import Redis
import pickle

# 如果token未提供，一个16字节bytes会自动生成
base = BaseStructure(Redis())
# 使用.token属性来访问生成的token
token = base.token 

# 这个token可被用作多线程环境中的访问token
base_other = BaseStructure(Redis(), token)

# redis贮存的数据结构类型可用`type`属性访问
data_type = base_other.type # a `bytes` object

# `serialize`属性可被用于访问序列器
ser = base.serialize
# 序列器也可被此属性更改
base.serialize = pickle


# `delete`方法用于从redis中删除数据
base.delete() # True|False return
base.clear() # alias for `delete`
base.flush() # alias for `delete`

# 私有方法，用于改变键值类型
conv_key = base._convert(1) # b'1'
conv_key = base._convert('test') # b'test'

# 私有方法，用于初始化数据结构
#   it will check the redis data type for the key
#   if type doesn't match it will delete it
base._initialize()

# 两个私有方法，用于访问内部序列器
base._loads(base._dumps({'test': 'case'})) # {'test': 'case'}
```

## Dict 类 ##

该类是dict到redis hash的界面类，和python `dict`相兼容，详情请参考[Python Docs: Dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries).

请注意：`Dict`不会做dirty check,所有对该实例存储的可变（mutable）数据的操作都应该参照`shelve`数据库的操作方式。

```python
from redistr import Dict
from redis import Redis

rem_dict = Dict(Redis(), 'dict_key')

rem_dict['test'] = 'case'

# 数据长度属性
length = rem_dict.length # 1

# popitem pops the key in sequence instead of randomly
rem_dict.popitem() # ('test', 'case')

rem_dict.update(test = 'case')

# additional feature, dynamic attributes
#   only works if no methods or properties have the same name
value = rem_dict.test # 'case'
rem_dict.test = {'test': 'case'}
rem_dict.case = value
rem_dict.test # {'test': 'case'}
rem_dict.case # 'case;


# how to modify mutable data, refer to `shelve` docs
rem_dict['doc'] = {'test': 'case'}
value = rem_dict['doc']
value['case'] = 'test'
rem_dict['doc'] = value
rem_dict['doc'] # {'test': 'case', 'case': 'test'}
```


## HyperLogLog 类 ##

该类对应redis的HyperLogLog数据结构，可被用来以最少的内存估计一个集合的大小。详情请参照[Redis Docs: HyperLogLog](https://redis.io/commands#hyperloglog)和[Redis author's blog on the subject](http://antirez.com/news/75)。

```python
from redistr import HyperLogLog
from redis import Redis

hll = HyperLogLog(Redis(), 'hll_key')

# register an action to the structure
hll.register({'test': 'case'})
# plus sign overridden as alias for register method
hll + b'another action or item'
100 + hll

# get the estimate count for unique items
count = hll.cardinal() # 3
count = hll.count() # 3, alias for `cardinal` method

# `log` property for quicker action
hll.log = {'another': 'item'}
hll.log = ['yet', 'another', 'action']
count = hll.log # 5, get the unique item count
```

## List | Set 类 ##

Python `list`和`set`的Redistr接口类被命名为`List`和`Set`。他们和Python中的`list`和`set`相兼容，详情请参照[Python Docs: List](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)和[Python Docs: Set](https://docs.python.org/3/tutorial/datastructures.html#sets)。

这两个接口类都提供了`_content`属性用来访问redis中存储的原始数据,`content`属性用来访问处理过的数据。

```python
from redistr import List
from redis import Redis

rem_list = List(Redis())
rem_set = List(Redis())

rem_list.append('item')
rem_list.extend('item')

# access the content
rem_list.content # ['item', 'i', 't', 'e', 'm']
# access the length
rem_list.length # 5

# circulate one item to the same/different list
#   using RPOPLPUSH operation on redis structure
# Signature: rem_list.circulate(token = None)
value = rem_list.circulate() # 'm'
rem_list.content # ['m', 'item', 'i', 't', 'e']
value = rem_list.circulate('another_list_key')
rem_list.content # ['m', 'item', 'i', 't']
# get `bytes`, the serialized  representation for 'e'
Redis().rpop('another_list_key') # `bytes` object


## additional features, methods and properties
# prepend an item to the left of the list
rem_list.prepend('item')
rem_list.unshift('item')
# popleft method and aliases for getting an item left
rem_list.popleft() # 'item'
rem_list.shift() # 'item'
```

```python
from redistr import Set
from redis import Redis

rem_set = Set(Redis())

# behaves exactly like python `set`
rem_set.add(1)
rem_set.content # {1}
rem_set.length # 1
rem_set.add(2)

rem_set_1 = Set(Redis())
rem_set_1.add(2)
rem_set_1.add(3)

rem_set.union(rem_set_1) # {1, 2, 3}
rem_set | rem_set_1 # {1, 2, 3}

rem_set.difference({2,3,4,5}) # {1}
rem_set - {2,3,4,5} # {1}

# etc...
```

## Queue 类 ##

`Queue`类实际上是`List`的子类别，所以`List`中已存在的方法可被立即调用，而且他的实例可以使用和`List`实例一样的token。该类提供了阻塞和非阻塞的队列方法。

```python
from redistr import Queue
from redis import Redis

queue = Queue(Redis, 'a_list_key')
# always hungery for more data
queue.full() # False, always False
# empty method for checking if empty
queue.empty() # True

# put an item to the left
queue.put('item')
queue.set('item2') # alias for put
queue.send('item 3') # alias for put

# put an item to the right
# have queue.set_right(), queue.send_right() aliases
queue.put_right('it 0')

# share the same methods with `List` class
queue.content # ['item 3', 'item2', 'item', 'it 0']
queue.length # 4
queue.pop() # 'it 0'

# blocking operations
#   Signature: `get(block = True, timeout = 0)`
#     Alias: `recv(block = True, timeout = 0)`
#   Signature: `get_left(block = True, timeout = 0)`
#     Alias: `recv_left(block = True, timeout = 0)`
#   Signature: `circulate(token = None, block = True, timeout = 0)
queue.push('right')
queue.get() # 'right'
queue.get_left() # 'item 3'
queue.circulate() # 'item'
queue.content # ['item', 'item2']

# additional feature: `msg` property for quick accessing
queue.msg # 'item2'
queue.msg = 2000
queue.content # [2000, 'item']
queue.msg # 'item'
queue.msg = 1000
queue.content = [1000, 2000]
```

## SeCo 类 ##

`SeCo`库被用于序列化和压缩住居，详情请参考[SeCo GitHub Repo](https://github.com/copyrighthero/SeCo)。

头: `SeCo(serialize = None, compress = None, **kwards)`

可以使用('json', 'msgpack', 'pickle')和('zlib', 'bz2')之间任一组合进行实例化。

> 推荐使用'msgpack'和'zlib'组合来达到最大时间-空间效率；可以使用'pickle'来达到最大的序列化覆盖面；可以使用'bz2'来达到最大的压缩效率，不过'bz2'压缩很费时间。

请使用下列方法来更改序列器。

```python
from redistr import Queue
from redis import Redis
from seco import SeCo
import json, msgpack, pickle


queue = Queue(Redis())
# default serializer uses `msgpack` and `zlib`
queue.serialize # get the default serializer

# create new serializers
ser_json_bz2 = SeCo('json', 'bz2')
ser_pickle_zlib = SeCo('pickle')

# flush all stale data from redis
queue.flush() # or .delete(), or .clear()

## change the serializer
# use the `Serialize` instances
queue.serialize = ser_json_bz2
queue.serialize = ser_pickle_zlib
# or others with `loads` and`dumps` methods
#   use this to avoid compression, etc.
queue.serialize = json
queue.serialize = msgpack
queue.serialize = pickle
```

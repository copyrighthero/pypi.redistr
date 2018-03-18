# Redistr API References #

## BaseStructure Class ##

This is the base structure or the base class for the other data structure classes. It takes two arguments with the second being optional.

Signature: `BaseStructure(redis, token = None)`

```python
from redistr import BaseStructure
from redis import Redis
import pickle

# if no token provided, a random 16 bytes will be generated
base = BaseStructure(Redis())
# generated or provided token can be accessed using `token` property
token = base.token 

# the token will be used for data sharing between processes
base_other = BaseStructure(Redis(), token)

# the type for the redis data structure can be accessed
data_type = base_other.type # a `bytes` object

# the serializer can be acquired at `serialize` property
ser = base.serialize
# and can be changed using the same property
base.serialize = pickle


# `delete` method for deleting key from redis
base.delete() # True|False return
base.clear() # alias for `delete`
base.flush() # alias for `delete`

# a private static method for converting keys
conv_key = base._convert(1) # b'1'
conv_key = base._convert('test') # b'test'

# a private method for initializing
#   it will check the redis data type for the key
#   if type doesn't match it will delete it
base._initialize()

# two private methods for accessing serializer
base._loads(base._dumps({'test': 'case'})) # {'test': 'case'}
```

## Dict Class ##

The dict <-> redis hash interface class, compatible with python `dict`, refer to [Python Docs: Dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries).

Remember that the `Dict` instance do not do dirty check, so modifications on mutable data should be done the same way when operating on a `shelve` database.

```python
from redistr import Dict
from redis import Redis

rem_dict = Dict(Redis(), 'dict_key')

rem_dict['test'] = 'case'

# length property for getting the length
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


## HyperLogLog ##

The redis HyperLogLog data structure, used to estimate how many items are in a collection using a very small memory footprint. Refer to [Redis Docs: HyperLogLog](https://redis.io/commands#hyperloglog) and [Redis author's blog on the subject](http://antirez.com/news/75) for more information.

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

## List | Set Classes ##

The interface for `list` and `set` are called `List` and `Set`. They behave the same as python `list` and `set`, refer to [Python Docs: List](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists) and [Python Docs: Set](https://docs.python.org/3/tutorial/datastructures.html#sets) for more information.

Both structure provides `_content` property for accessing raw content, and `content` property for accessing parsed content.

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

## Queue Class ##

`Queue` class is a subclass of `List`, thus it has all the methods available to `List` ready to be used. And since it is built on `List` it can actually share the same redis key with a `List` instance. It provides methods for both blocking and non-blocking use.

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

## Serialize Class ##

The `Serialize` class is an add-on class for serializing and compressing data.

Signature: `Serialize(ser = None, com = None, **kwards)`

It can be initialized to use any combinations between ('json', 'msgpack', 'pickle') and ('zlib', 'bz2').

Recommend to use 'msgpack' and 'zlib' for the optimal speed and space efficiency; use 'pickle' for broadest Python type support; use 'bz2' for maximum space efficiency at the cost of time.

Change any of the structure's serializer using the following procedures.

```python
from redistr import Queue, Serialize
from redis import Redis
import json, msgpack, pickle


queue = Queue(Redis())
# default serializer uses `msgpack` and `zlib`
queue.serialize # get the default serializer

# create new serializers
ser_json_bz2 = Serialize('json', 'bz2')
ser_pickle_zlib = Serialize('pickle')

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

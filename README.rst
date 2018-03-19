###############
Redistr Project
###############

`API Docs`_ | `Python Docs <https://docs.python.org>`_ | `Redis Docs <https://redis.io/commands>`_ | | `README中文说明 <https://github.com/copyrighthero/Redistr/blob/master/README.zh-CN.md>`_ | `API中文文档 <https://github.com/copyrighthero/Redistr/blob/master/API.zh-CN.md>`_

1. About Redistr Project
========================

The Redistr project is written to provide users with redis backed Python data structures. By using Redistr, Python programs running on different locations or platforms can share data between them.

The project currently provides `Dict`, `HyperLogLog`, `List`, `Queue` and `Set`.

For extensive details on how to use, please refer to `API Docs`_.

2. Why Choose Redistr
=====================

Python's `multiprocessing` and `threading` modules provide some shared data structures, and can be used for communications between processes. However, these data structures are usually limited to Python languages because the internal use of pickle module, and sometimes requires explicit setups which might be time consuming. Redistr on the other hand, can be configured to use `json`, `msgpack`, `pickle` or any other serializers for broader compatibility. And since information is stored in redis, the data structures can potentially be re-used in other languages.

The project currently defaults to use the `SeCo` module for the serialization and compression functionality, which defaults to use `msgpack` for serialization and `zlib` for compression. But the defaults can easily be changed to `json`, `msgpack` or `pickle` in combination with `zlib` or `bz2`. Please read on for more information.

3. Using Redistr
================

After installing Redistr with `pip install redistr`, all the data structures are available within the `redistr` module. For detailed usage and documentation, please refer to `API Docs`_.

 **0. REMINDERS**

 1. The first parameter `redis` is going to be redis instance, the optional second parameter `token` is the redis key for the structure. If data exists at the key and data type does not match, the key will be deleted from redis server first. To avoid data loss, use different tokens for different data structures.

 2. If the `token` parameter is not provided, a random sequence will be generated, this way one can avoid data loss. To get the generated token and use in cross-process/platform environment, one can simply access the `instance.token` property. ie: `l_0 = List(Redis()); token = l_0.token; l_1 = List(Redis(), token);`. This way, both `l_0` and `l_1` have access to the same list saved on redis.

 3. The slicing functionality for `List` is NOT (YET) FULLY COMPATIBLE with Python's `list`!!! Simple slicing with only `[start:stop]` works as expected, but `[start:stop:step]` may not behave the same way under certain circumstances, avoid using `step` when slicing.

 4. The `Dict` data structure behaves like `shelve` module, it DOES NOT do dirty checks (yet), thus it won't update the saved data when the saved data is mutable and changed. ie: `d_0 = Dict(Redis(), 'dict'); d_0['test'] = [1,2,3,4]; d_0['test'].append(5); d_0.content; # -> [1,2,3,4]`, you'll have to acquire the data first, modify, and save back, just like the vanilla `shelve` package.

 5. All serializers have their weaknesses, JSON can't serialize binary data like `bytes`, `msgpack` can't serialize `set`, `frozenset`, etc. The most capable one for Python is pickle, but it bloats the data quite a bit. Thus using `pickle` with `zlib` should give you the most capable serializer at a reasonable cost in space. The default serializer uses `msgpack` with `zlib` for the speed and size, refer refer to `SeCo's GitHub Repo <https://github.com/copyrighthero/SeCo>`_ for more info.

 6. Some of the operations/methods added for compatibility are `O(N)` operations thus will take time when invoked on large amount of data, please refer to the source codes for details. Methods and properties like `push`, `unshift`, `shift` and `length` were added to the structures for convenience, explore source code or refer to document for more details.

 **1. Simple Usage**

 Once again, for detailed usage please refer to `API Docs`_ or source.

 .. code-block:: python

   from redis import Redis
   import redistr

   # create a redis instance
   redis = Redis(host='localhost', port=6379)

   ## initialize data structures ##
   # list compatible data structure
   rem_list = redistr.List(redis, 'list_key')
   # queue, a subclass of `List` class
   rem_queue = redistr.Queue(redis, 'list_key')
   # set compatible data structure
   rem_set = redistr.Set(redis, 'set_key')
   # dict compatible data structure
   rem_dict = redistr.Dict(redis, 'hash_key')
   # hyperloglog data structure
   rem_hll = redistr.HyperLogLog(redis)

   # regular list operations
   rem_list.append('test')
   rem_list.append({'case': 'file'})
   rem_list.extend('str')
   # access list content
   rem_list.content # ['test', {'case': 'file'}, 's', 't', 'r']

   # block get operation
   rem_queue.get() # 'r'
   # block get from left
   rem_queue.get_left() # 'test'
   # regular non-block put item
   rem_queue.put(100)
   # put an item to the right of the list
   rem_queue.put_right({'job_type': 'flush'})
   # get and item and push to another list
   rem_queue.circulate() # {'job_type': 'flush'}
   # [{'job_type': 'flush'}, 100, {'case': 'file'}, 's', 't']
   rem_list.content
   # ...

   # register an action to HLL
   rem_hll.register(10000)
   rem_hll.cardinal() # ~= 1, action count
   # if token not provided as the second parameter,
   #   all structures will generate a sequence as key
   #   use this key for cross-process/platform comms
   rem_hll.token # <bytes>, random bytes as key

 **2. Change Serializers**

 .. code-block:: python

   from redis import Redis
   from redistr import List
   from seco import SeCo
   import json, pickle

   # `msgpack` and `zlib` are the recommended, default values
   #   `msgpack` supports `bytes` encoding
   #   `pickle` supports (almost) all objects
   #   `zlib` is much faster than `bz2`
   #   `bz2` has a better compression rate
   ser = SeCo(serialize='json', compress='zlib')

   redis = Redis()
   rem_list = List(redis, 'list_key')
   # use the token for cross-process communications
   rem_list.token # b'list_key'

   # remove stale data first, may not be required
   rem_list.delete()
   # change the serializer
   rem_list.serialize = ser
   # any instance with `dumps` and `loads` methods
   #   can be used as the serializer, ie: json, pickle
   #   user can change to these to avoid data compressions
   rem_list.serialize = json
   rem_list.serialize = pickle
   #  ...

4. Licenses
===========

This project is licensed under two permissive licenses, please chose one or both of the licenses to your like. Although not necessary, bug reports or feature improvements, attributes to the author(s), information on how this program is used are welcome and appreciated :-) Happy coding

[BSD-2-Clause License]

Copyright 2018 Hansheng Zhao

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[MIT License]

Copyright 2018 Hansheng Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. _API Docs: https://github.com/copyrighthero/Redistr/blob/master/API.md

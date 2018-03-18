# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

from .BaseStructure import BaseStructure


__all__ = ('Dict', )


class Dict(BaseStructure):
  """
  Dict interface for redis hashes

  !! NO AUTO WRITE-BACK SUPPORT !!
  !! BEHAVES LIKE SHELVE MODULE !!
  """

  __slots__ = ()

  def __init__(self, redis, token = None):
    """
    Dict interface constructor
    :param redis: redis, the instance
    :param token: mixed, the token
    """
    super(Dict, self).__init__(redis, token)
    # set the default data type
    self._type = b'hash'
    self._initiate()

  def __contains__(self, key):
    """
    Check if a field exists in the store
    :param key: mixed, serializable items
    :return: bool, whether item exists
    """
    return self._redis.hexists(
      self._token, self._convert(key)
    )

  def __delattr__(self, key):
    """
    Attempt to remove the attribute
    :param key: str, the attribute
    :return: None
    """
    try:
      # attempt to remote attribute first
      super(Dict, self).__delattr__(key)
    except AttributeError:
      # delete from database
      self.__delitem__(key)

  def __delitem__(self, key):
    """
    Remove a field from the storage
    :param key: mixed, the key field
    :return: bool, whether removed
    """
    return self._redis.hdel(
      self._token, self._convert(key)
    )

  def __eq__(self, other):
    """
    Check if items are the same
    :param other: dict|Dict, dict-like
    :return: bool, equal or not
    """
    if len(self) == len(other):
      return dict(self) == (
        dict(other)
        if isinstance(other, Dict)
        else other
      )
    else:
      return False

  def __getattr__(self, key):
    """
    Acquire an item from database
    :param key: mixed, the key field
    :return: mixed, the stored value
    """
    return self.__getitem__(key)

  def __getitem__(self, key):
    """
    Acquire an item from database
    :param key: mixed, the key field
    :return: mixed, the stored value
    """
    # acquire stored value
    result = self._redis.hget(
      self._token, self._convert(key)
    )
    # deserialize result
    if result is not None:
      result = self._loads(result)
    return result

  def __iter__(self):
    """
    Iterator to get keys in store
    :return: generator, the iterator
    """
    yield from self._redis.hkeys(self._token)

  def __len__(self):
    """
    Acquire key fields count
    :return: int, the count
    """
    return self._redis.hlen(self._token)

  def __ne__(self, other):
    """
    Check if two instances are same
    :param other: other instance
    :return: bool, whether not equal
    """
    return not self.__eq__(other)

  def __setattr__(self, key, value):
    """
    Attempt to set an attribute
    :param key: str, the attribute
    :param value: mixed, attribute
    :return: None
    """
    try:
      super(Dict, self).__setattr__(key, value)
    except AttributeError:
      self.__setitem__(key, value)

  def __setitem__(self, key, value):
    """
    Store a key-value pair to store
    :param key: mixed, the key field
    :param value: mixed, serializable
    :return: bool, whether new field
    """
    return self._redis.hset(
      self._token,
      self._convert(key),
      self._dumps(value)
    ) == 1

  # alias for set item
  set = __setitem__

  @property
  def length(self):
    """
    Property for key count
    :return: int, the count
    """
    return self.__len__()

  def copy(self):
    """
    Return a new instance
    :return: instance
    """
    instance = Dict(self._redis, self._token)
    instance.serialize = self._serialize
    return instance

  @staticmethod
  def fromkeys(*args, **kwargs):
    """
    Method for dict compatibility
    :param args: mixed, arguments
    :param kwargs: keyword arguments
    :return: dict, the built dict
    """
    return dict.fromkeys(*args, **kwargs)

  def get(self, key, default = None):
    """
    Acquire an item from store
    :param key: mixed, the key
    :param default: mixed, default
    :return: mixed, value/default
    """
    return self.__getitem__(key) \
      if key in self else default

  def items(self):
    """
    Acquire all items from data store
    :return: tuple<tuple>, the k-v pairs
    """
    yield from map(
      lambda _: (_[0], self._loads(_[1])),
      self._redis.hgetall(self._token).items()
    )

  def keys(self):
    """
    Acquire all keys in the dictionary
    :return: generator, the keys
    """
    yield from self._redis.hkeys(self._token)

  def pop(self, key):
    """
    Acquire item and delete key
    :param key: mixed, the key
    :return: mixed, stored value
    """
    # acquire item delete key
    result = self.__getitem__(key)
    self.__delitem__(key)
    return result

  def popitem(self):
    """
    Pop a pair of key & value
    :return: tuple, k-v pair
    """
    key = next(self.keys())
    value = self.pop(key)
    return key, value

  def setdefault(self, key, default = None):
    """
    Get or set the default into store
    :param key: mixed, the key
    :param default: mixed, default
    :return: mixed, default/actual
    """
    if key in self:
      # return stored if key exists
      return self.__getitem__(key)
    else:
      # set and return default if not
      self.__setitem__(key, default)
      return default

  def update(self, item = None, **kwargs):
    """
    Update self from dict/iterable

    Compatible with dict's update

    :param item: the dict/iterable
    :param kwargs: keyword arguments
    :return: None
    """
    # check if item is present
    if item is not None:
      # check if item has keys attribute
      if hasattr(item, 'keys'):
        for key in item.keys():
          self.__setitem__(key, item[key])
      else:
        # assumes item to be pairs
        for key, value in item:
          self.__setitem__(key, value)
    # always update self with kwargs
    for key, value in kwargs.items():
      self.__setitem__(key, value)

  def values(self):
    """
    Acquire all values in dictionary
    :return: generator, the values
    """
    yield from map(
      lambda _: self._loads(_),
      self._redis.hvals(self._token)
    )

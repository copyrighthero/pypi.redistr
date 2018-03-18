# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

from .BaseStructure import BaseStructure


__all__ = ('List', )


class List(BaseStructure):
  """ Redis list structure interface """

  __slots__ = ()

  def __init__(self, redis, token = None):
    """
    List structure interface constructor
    :param redis: redis, the redis instance
    :param token: mixed, the access token
    """
    # invoke parent constructor
    super(List, self).__init__(redis, token)
    # set the default data type
    self._type = b'list'
    self._initiate()

  def __add__(self, other):
    """
    Perform addition operation
    :param other: list|tuple|range, sequences
    :return: list, the added list
    """
    return self.content + (other if not isinstance(
      other, (list, tuple, range)
    ) else list(other))

  def __contains__(self, value):
    """
    Check if value exists in list

    O(N) operation, not encouraged

    :param value: mixed, value
    :return: bool, if value exists
    """
    # serialize value
    value = self._dumps(value)
    return value in self._content

  def __delitem__(self, index):
    """
    Delete value at index from redis

    O(N) operation, not encouraged

    :param index: int, index
    :return: None
    """
    # acquire resources
    redis = self._redis
    token = self._token
    transform = self._transform
    # acquire list lengths
    length = self.length
    half_length = length // 2
    # check if index provided
    if isinstance(index, int):
      # trim off the first element
      if index == 0: redis.ltrim(token, 1, -1)
      # trim off the last element
      elif index == -1: redis.ltrim(token, 0, -2)
      else:
        # transform negative index
        index = transform(index)
        # index is on the left side
        if 0 < index <= half_length:
          # acquire left side segment
          segment = redis.lrange(token, 0, index - 1)
          # trim to the rest of the list
          redis.ltrim(token, index + 1, -1)
          # prepend the left side segment
          redis.lpush(token, *reversed(segment))
        # index is on the right side
        elif half_length < index < length :
          # acquire right side segment
          segment = redis.lrange(token, index + 1, -1)
          # trim the rest of the list
          redis.ltrim(token, 0, index - 1)
          # append the right side segment
          redis.rpush(token, *segment)
    # check if slice provided
    elif isinstance(index, slice):
      # warning: slow operation
      if index.step:
        # acquire list of indices
        indices = tuple(range(
          index.start, index.stop, index.step
        ))
        # remove one by one
        while indices:
          # acquire index
          index = indices[0]
          # shift indices by one
          indices = tuple(map(
            lambda _: _ - 1, indices[1:]
          )) if indices else []
          # delete current item
          self.__delitem__(index)
      else:
        # transform negative index
        start = transform(index.start)
        stop = transform(index.stop)
        # trim off left
        if start == 0: redis.ltrim(token, stop, -1)
        # trim off right
        elif stop == length: redis.ltrim(token, 0, start - 1)
        # check if slice range is valid
        elif 0 < start <= stop <= length:
          # trim from the left side
          if start + 1 <= length - stop:
            segment = redis.lrange(token, 0, start - 1)
            redis.ltrim(token, stop, -1)
            redis.lpush(token, *reversed(segment))
          # trim from the right side
          else:
            segment = redis.lrange(token, stop, -1)
            redis.ltrim(token, 0, start - 1)
            redis.rpush(token, *segment)

  def __eq__(self, other):
    """
    Check if two sequences are the same
    :param other: sequence
    :return: bool, the same
    """
    if len(self) == len(other):
      return list(self) == (
        list(other)
        if isinstance(other, (List, tuple, range))
        else other
      )
    else:
      return False

  def __getitem__(self, index):
    """
    Get value from redis list
    :param index: int|slice, the index
    :return: mixed|list, the value(s)
    """
    # acquire resources
    redis = self._redis
    token = self._token
    # default result
    result = None
    # check if index provided
    if isinstance(index, int):
      # use index to acquire item
      result = redis.lindex(token, index)
    # check if slice provided
    elif isinstance(index, slice):
      # acquire a range of items
      result = redis.lrange(
        token, index.start, index.stop - 1
      )
      # TODO: IMPLEMENT RIGHT STEPPING
      # WARNING: INCOMPATIBLE STEPPING
      if index.step:
        result = result[::index.step]
    # deserialize result
    if isinstance(result, bytes):
      result = self._loads(result)
    elif isinstance(result, list):
      result = list(map(
        lambda _: self._loads(_), result
      ))
    return result

  def __ge__(self, other):
    """
    Check greater or equal to other
    :param other: sequence
    :return: bool, comparison
    """
    return not self.__lt__(other)

  def __gt__(self, other):
    """
    Check greater than other
    :param other: sequence
    :return: bool, comparison
    """
    return not (self.__lt__(other) or self.__eq__(other))

  def __iadd__(self, other):
    """
    Append items to the list
    :param other: list|tuple|range, sequence
    :return: self, this instance
    """
    if isinstance(other, (list, tuple, range)):
      self._redis.rpush(self._token, *map(
        lambda _: self._dumps(_), other
      ))
    return self

  def __imul__(self, other):
    """
    Append a multiplication of items
    :param other: int, the multiplier
    :return: self, this instance
    """
    # check if multiplier is valid
    if isinstance(other, int):
      # acquire resources
      redis = self._redis
      token = self._token
      # append new items or flush
      redis.rpush(
        token, *(self._content * (other - 1))
      ) if other >= 1 else self.clear()
    return self

  def __iter__(self):
    """
    Parsed content iterator
    :return: generator
    """
    yield from map(
      lambda _: self._loads(_),
      self._redis.lrange(self._token, 0, -1)
    )

  def __len__(self):
    """
    Acquire list length
    :return: int, the length
    """
    return self._redis.llen(self._token)

  def __le__(self, other):
    """
    Check less than or equal to other
    :param other: sequence
    :return: bool, comparison
    """
    return self.__lt__(other) or self.__eq__(other)

  def __lt__(self, other):
    """
    Check if less than other
    :param other: sequence
    :return: bool, comparison
    """
    if len(self) == len(other):
      pass
    elif isinstance(other, (List, list, tuple, range)):
      return len(self) < len(other)
    else:
      raise TypeError('Invalid comparison types.')

  def __mul__(self, other):
    """
    Perform multiplication operation
    :param other: int, the multiplier
    :return: list, the result list
    """
    return self.content * other

  # alias for multiply
  __rmul__ = __mul__

  def __ne__(self, other):
    """
    Check if not equal to other
    :param other: sequence
    :return: bool, comparison
    """
    return not self.__eq__(other)

  def __radd__(self, other):
    """
    Perform addition operation
    :param other: list|tuple|range, sequences
    :return: list, the added list
    """
    return (other if not isinstance(
      other, (list, tuple, range)
    ) else list(other)) + self.content

  def __reversed__(self):
    """
    Acquire reversed generator
    :return: generator, the reversed
    """
    yield from reversed(self.content)

  def __setitem__(self, index, value):
    """
    Set value to index in redis list
    :param index: int, index
    :param value: mixed, value
    :return: None
    """
    # serialize value
    value = self._dumps(value)
    self._redis.lset(self._token, index, value)

  @property
  def _content(self):
    """
    Acquire raw list content
    :return: list, the content
    """
    return self._redis.lrange(self._token, 0, -1)

  @property
  def length(self):
    """
    Length property getter
    :return: int, the length
    """
    return self.__len__()

  @property
  def content(self):
    """
    Acquire deserialized list content
    :return: list, the content
    """
    return list(map(
      lambda _: self._loads(_), self._content
    ))

  def _transform(self, index):
    """
    Transform negative index
    :param index: int, index
    :return: int, index
    """
    # check if index is integer
    if isinstance(index, int):
      # acquire length
      length = self.length
      # return positive if valid
      return length + index \
        if -length < index < 0 else index
    else:
      # do nothing
      return index

  def append(self, value):
    """
    Append value to the end
    :param value: mixed, value
    :return: None
    """
    # serialize value
    value = self._dumps(value)
    self._redis.rpush(self._token, value)

  push = append

  def circulate(self, token = None):
    """
    Circulate an item (RPOPLPUSH)
    :param token: None|mixed, the target
    :return: mixed, the item
    """
    # convert token to bytes
    token = self._convert(token) \
      if token is not None else self._token
    # acquire and circulate an item
    result = self._redis.rpoplpush(self._token, token)
    # deserialize result
    if result is not None: result = self._loads(result)
    return result

  def copy(self):
    """
    Acquire a new instance
    :return: instance, the instance
    """
    instance = List(self._redis, self._token)
    instance.serialize = self.serialize
    return instance

  def count(self, value):
    """
    Count the value in list
    :return: int, the count
    """
    # serialize value
    value = self._dumps(value)
    return self._content.count(value)

  def extend(self, iterable):
    """
    Extend list with iterable
    :param iterable: iterable
    :return: None
    """
    self._redis.rpush(self._token, *map(
      lambda _: self._dumps(_), iterable
    ))

  def index(self, value, start = None, stop = None):
    """
    Acquire value's index
    :param value: mixed, the value
    :param start: the start index
    :param stop: the stop index
    :return: int, the index
    """
    # serialize value
    value = self._dumps(value)
    return self._content.index(value, start, stop)

  def insert(self, index, value):
    """
    Insert an item to index
    :param index: int, the index
    :param value: mixed, the value
    :return: None
    """
    # serialize value
    value = self._dumps(value)
    self._redis.lset(self._token, index, value)

  def pop(self, index = None, flag = True):
    """
    Return and delete an item
    :param index: int|None, the index
    :param flag: bool, from right or not
    :return: mixed|None, the item
    """
    # acquire resources
    redis = self._redis
    token = self._token
    # acquire list length
    length = self.length
    # default result
    result = None
    # check if index provided
    if index is None:
      # regular pop from list
      result = redis.rpop(token) \
        if flag else redis.lpop(token)
    # check if index is integer
    elif isinstance(index, int):
      # transform negative index
      index = self._transform(index)
      # regular left pop operation
      if index == 0:
        result = redis.lpop(token)
      # regular right pop operation
      elif index == length - 1:
        result = redis.rpop(token)
      elif 0 < index < length - 1:
        # acquire and remove item
        result = self.__getitem__(index)
        self.__delitem__(index)
    # check if slice provided
    elif isinstance(index, slice):
      # acquire and remove item
      result = self.__getitem__(index)
      self.__delitem__(index)
    # deserialize result
    if isinstance(result, bytes):
      result = self._loads(result)
    elif isinstance(result, list):
      result = list(map(
        lambda _: self._loads(_), result
      ))
    return result

  def popleft(self):
    """
    Pop an item from left
    :return: mixed|None, the item
    """
    result = self._redis.lpop(self._token)
    return self._loads(result) if result else result

  # aliases for popleft
  shift = popleft

  def prepend(self, value):
    """
    Prepend value to the start
    :param value: mixed, value
    :return: None
    """
    # serialize value
    value = self._dumps(value)
    self._redis.lpush(self._token, value)

  # aliases for prepend
  unshift = prepend

  def remove(self, value):
    """
    Remove all value from list
    :param value: mixed, value
    :return: int, actual count
    """
    # serialize value
    value = self._dumps(value)
    return self._redis.lrem(self._token, value)

  # aliases for remove
  discard = purge = remove

  def reverse(self):
    """
    Reverse the list from redis
    :return: None
    """
    # acquire raw content
    content = self._content
    # clear and reset list
    self.clear()
    self._redis.rpush(
      self._token, *reversed(content)
    )

  def sort(self, *args, **kwargs):
    """
    Sort the list from redis
    :param args: the arguments
    :param kwargs: keyword args
    :return: None
    """
    # acquire and sort content
    content = self.content
    content.sort(*args, **kwargs)
    # clear and reset list
    self.clear()
    self._redis.rpush(self._token, *map(
      lambda _: self._dumps(_), content
    ))

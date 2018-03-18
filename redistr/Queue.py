# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

from .List import List


__all__ = ('Queue', )


class Queue(List):
  """ Blocking queue based on redis list """

  __slots__ = ()

  def __init__(self, redis, token = None):
    """
    Queue interface constructor
    :param redis: redis, the instance
    :param token: str|bytes, the token
    """
    super(Queue, self).__init__(redis, token)

  @staticmethod
  def _timeout(timeout):
    """
    Lint blocking timeout parameter
    :param timeout: int|float|mixed, the timeout
    :return: int, the linted timeout
    """
    # check if timeout is numeric
    timeout = int(timeout) \
      if isinstance(timeout, (int, float)) else 0
    # check if timeout is positive
    timeout = timeout if timeout >= 0 else 0
    return timeout

  @staticmethod
  def full():
    """
    Check if queue is full
    :return: False, always hungry
    """
    return False

  def empty(self):
    """
    Check if queue is empty
    :return: bool, whether empty
    """
    return self.length == 0

  def _get_from_multi(
    self,
    token=None, block=True, timeout=0, flag = True
  ):
    """
    Blocking get an item from the queue
    :param token: mixed, the queue token(s)
    :param block: bool, whether to block
    :param timeout: int, block length
    :param flag: bool, whether get right
    :return: mixed, an item
    """
    # acquire resources
    redis = self._redis
    convert = self._convert
    # sanitize token parameter
    token = tuple(map(lambda _: convert(_), token)) \
      if isinstance(
        token, (list, tuple, range, set, frozenset)
      ) else (
        None if token is None else (convert(token), )
      )
    token = (self._token, ) \
      if token is None else (self._token, *token)
    # lint timeout parameter
    timeout = self._timeout(timeout) if block else 0
    # check flag
    if block:
      # acquire from a list of lists
      result = redis.brpop(token, timeout) \
        if flag else redis.blpop(token, timeout)
      # deserialize result
      if result is not None:
        result = self._loads(result[1])
    else:
      result = None
      # acquire from a list of lists
      for item in token:
        result = redis.rpop(item) \
          if flag else redis.lpop(item)
        # deserialize result
        if result is not None:
          result = self._loads(result)
          break
    return result

  def _get(
    self, block = True, timeout = 0, flag = True
  ):
    """
    Blocking get an item from the queue
    :param block: bool, whether to block
    :param timeout: int, block length
    :param flag: bool, whether get right
    :return: mixed, an item
    """
    # acquire resources
    redis = self._redis
    token = self._token
    # sanitize timeout value
    timeout = self._timeout(timeout) if block else 0
    # check block flag
    if block:
      # acquire a result from queue
      result = redis.brpop((token, ), timeout) \
        if flag else redis.blpop((token, ), timeout)
      # deserialize result
      if result is not None:
        result = self._loads(result[1])
    else:
      # acquire non-blocking
      result = redis.rpop(token) \
        if flag else redis.lpop(token)
      # deserialize result
      if result is not None:
        result = self._loads(result)
    return result

  def _put(self, value, flag = True):
    """
    Non-blocking put an item to redis queue
    :param value: mixed, an item or message
    :param flag: bool, whether to put left
    :return: None
    """
    self.prepend(value) if flag else self.append(value)

  def get(self, block = True, timeout = 0):
    """
    Blocking get an item from the tail
    :param block: bool, whether to block
    :param timeout: int, block length
    :return: mixed, an item
    """
    return self._get(block, timeout, True)

  # aliases for get
  recv = get

  def get_left(self, block = True, timeout = 0):
    """
    Blocking get an item from the head
    :param block: bool, whether to block
    :param timeout: int, block length
    :return: mixed, an item
    """
    return self._get(block, timeout, False)

  # aliases for get_left
  recv_left = get_left

  def put(self, value):
    """
    Non-blocking put an item to redis queue
    :param value: mixed, an item or message
    :return: None
    """
    self._put(value, True)

  # aliases for put
  set = send = put

  def put_right(self, value):
    """
    Non-blocking put an item to redis queue
    :param value: mixed, an item or message
    :return: None
    """
    self._put(value, False)

  # aliases for put_right
  set_right = send_right = put_right

  def circulate(
    self, token = None, block = True, timeout = 0
  ):
    """
    Blocking circulate an item (BRPOPLPUSH)
    :param token: None|mixed, the target
    :param block: bool, whether block or not
    :param timeout: int, timeout length
    :return: mixed, the item
    """
    # acquire resources
    redis = self._redis
    # convert token to bytes
    token = self._convert(token) \
      if token is not None else self._token
    # lint timeout parameter
    timeout = self._timeout(timeout) if block else 0
    # acquire and circulate an item
    result = redis.brpoplpush(
      self._token, token, timeout
    ) if block else redis.rpoplpush(self._token, token)
    # deserialize result
    if result is not None: result = self._loads(result)
    return result

  # alias for get & pur message
  msg = property(get, put)

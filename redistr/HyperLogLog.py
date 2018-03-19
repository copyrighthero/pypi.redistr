# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

from .BaseStructure import BaseStructure


__all__ = ('HyperLogLog', )


class HyperLogLog(BaseStructure):

  __slots__ = ()

  def __init__(self, redis, token = None):
    """
    HyperLogLog interface constructor
    :param redis: redis, the instance
    :param token: mixed, access token
    """
    # import redis ResponseError
    from redis import ResponseError
    super(HyperLogLog, self).__init__(redis, token)
    # set the default data type
    self._type = b'string'
    self._initiate()
    # check if HLL string is valid
    try:
      self._redis.pfcount(self._token)
    except ResponseError:
      self._redis.delete(self._token)

  def __iadd__(self, value):
    """
    Augmented addition operation
    :param value: mixed, the value
    :return: self, the instance
    """
    self.register(self._dumps(value))
    return self

  def register(self, *args):
    """
    Register a new value into log
    :param args: mixed, the value(s)
    :return: None
    """
    self._redis.pfadd(
      self._token, *map(lambda _: self._dumps(_), args)
    )

  # aliases for register
  __add__ = __radd__ = register

  def cardinal(self):
    """
    Acquire count from log
    :return: int, the count
    """
    return self._redis.pfcount(self._token)

  # aliases for cardinal
  count = cardinal

  # log property for add and count
  log = property(cardinal, register)

# Author: Hansheng Zhao <zhaohans@msu.edu> (https://www.zhs.me)

from os import urandom


class BaseStructure(object):
  """ Redis interfaces base structure """

  __slots__ = (
    '_type', '_redis', '_token', '_serialize'
  )

  TOKEN_LENGTH = 16

  def __init__(self, redis, token = None):
    """
    BaseStructure class constructor
    :param redis: redis, the redis instance
    :param token: mixed, the access token
    """
    # import SeCo serializer
    from seco import SeCo
    # set the default type
    self._type = b'none'
    # preserve redis instance
    self._redis = redis
    # assign remote access token
    self._token = urandom(self.TOKEN_LENGTH) \
      if token is None else self._convert(token)
    # set default serializer
    self._serialize = SeCo(
      serialize = 'msgpack', compress = 'zlib'
    )

  @property
  def token(self):
    """
    Token property getter
    :return: bytes, the token
    """
    return self._token

  @property
  def type(self):
    """
    Acquire token's redis type
    :return: bytes, the data type
    """
    return self._redis.type(self._token)

  @property
  def serialize(self):
    """
    Acquire instance serializer
    :return: instance, serializer
    """
    return self._serialize

  @serialize.setter
  def serialize(self, serialize):
    """
    Set instance serializer
    :param serialize: serializer
    :return: None
    """
    self._serialize = serialize

  @staticmethod
  def _convert(key):
    """
    Convert key to supported format
    :param key: mixed, any hashable object
    :return: bytes, bytes representation of key
    """
    # check if key is supported or hashable
    # support bytes by default
    if isinstance(key, bytes):
      return key
    # encode string type to bytes
    elif isinstance(key, str):
      return key.encode(encoding = 'UTF8')
    # change byte-array into bytes
    elif isinstance(key, bytearray):
      return bytes(key)
    # convert numeric into string
    elif isinstance(key, (int, float, complex)):
      return str(key).encode(encoding = 'UTF8')
    # convert hashable collections into string
    elif isinstance(key, (range, tuple, frozenset)):
      return str(key).encode(encoding = 'UTF8')
    # other types not supported
    else:
      raise TypeError('Unsupported type.')

  def _initiate(self):
    """
    Initiate the redis storage
    :return: None
    """
    # check if token exists in redis server
    if self.type not in (b'none', self._type):
      # remove token of different types
      self._redis.delete(self._token)

  def _dumps(self, payload):
    """
    Serialize value using serializer
    :param payload: mixed, value
    :return: bytes, the result
    """
    return self._serialize.dumps(payload)

  def _loads(self, payload):
    """
    Un-serialize value using serializer
    :param payload: bytes|string, payload
    :return: mixed, the object
    """
    return self._serialize.loads(payload)

  def delete(self):
    """
    Delete token from redis
    :return: bool, successful or not
    """
    return self._redis.delete(self._token) != 0

  # aliases for delete
  clear = flush = delete

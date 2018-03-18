# Author: Hansheng Zhao <zhaohans@msu.edu> (https://www.zhs.me)

import bz2
import zlib
import json
import pickle

try:
  # attempts to import msgpack
  import msgpack
except ModuleNotFoundError:
  # use pickle if not available
  msgpack = pickle


__all__ = ('Serialize', )


class Serialize(object):
  """ Serialize class for data processing """

  __slots__ = (
    '_serialize', '_compress',
    '_serializer','_compressor'
  )

  def __init__(self, ser = None, com = None, **kwargs):
    """
    Initialize method for building object
    :param ser: str|dict|None, the serialize config
    :param com: str|None, the compress config
    :param kwargs: dict, the stray keyword args
    """
    # default configurations
    self._serialize = 'json'
    self._compress = 'zlib'
    self._serializer = None
    self._compressor = None
    # acquire serialize (and compress) config
    if ser is not None:
      if isinstance(ser, str):
        self._serialize = ser.lower()
      else:
        if 'serialize' in ser:
          self._serialize = ser['serialize']
        if 'compress' in ser:
          self._compress = ser['compress']
    elif 'serialize' in kwargs:
      self._serialize = kwargs['serialize']
    # acquire compress config
    if com is not None and isinstance(com, str):
      self._compress = com.lower()
    elif 'compress' in kwargs:
      self._compress = kwargs['compress']

  def __call__(self, payload, switch = True):
    """
    Alias for serialize/de-serialize methods
    :param payload: mixed, various objects
    :param switch: bool, whether to serialize
    :return: mixed, objects
    """
    return self.dumps(payload) \
      if switch else self.loads(payload)

  def _instantiate(self):
    """
    Instantiate serializer and compressor
    :return: None
    """
    # setup appropriate serializer
    if self._serializer is None:
      self._serializer = json
      if self._serialize == 'pickle':
        self._serializer = pickle
      elif self._serialize == 'msgpack':
        self._serializer = msgpack
    # setup appropriate compressor
    if self._compressor is None:
      self._compressor = zlib
      if self._compress == 'bz2':
        self._compressor = bz2

  # dumps method for python convention
  def dumps(self, payload):
    """
    Serialize and compress the payload
    :param payload: mixed, serializable object
    :return: byte, the serialized and compressed object
    """
    # instantiate serializer and compressor
    self._instantiate()
    # serialize payload
    payload = self._serializer.dumps(payload)
    # encode payload if payload is string
    if isinstance(payload, (str,)): payload = payload.encode()
    # compress and return payload
    return self._compressor.compress(payload)

  def dump(self, payload, file):
    """
    Serialize, compress and save
    :param payload: mixed, serializable object
    :param file: file descriptor
    :return: None
    """
    file.write(self.dumps(payload))
    file.flush()

  # alias for dump
  pack = dump

  # loads method for python convention
  def loads(self, payload):
    """
    Decompress and deserialize the payload
    :param payload: bytes, serialized byte string
    :return: object, the decompressed and deserialized object
    """
    # instantiate serializer and compressor
    self._instantiate()
    # decompress payload
    payload = self._compressor.decompress(payload)
    # deserialize and return payload
    return self._serializer.loads(payload, encoding='UTF8')

  def load(self, file):
    """
    Decompress and deserialize the file
    :param file: file descriptor, or BytesIO instance
    :return: object, the decompressed and deserialized object
    """
    # decompress, deserialize and return payload
    return self.loads(file.read())

  # alias for load
  unpack = load

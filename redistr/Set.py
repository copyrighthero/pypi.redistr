# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

from .BaseStructure import BaseStructure


__all__ = ('Set', )


class Set(BaseStructure):

  __slots__ = ()

  def __init__(self, redis, token = None):
    """
    Set interface constructor
    :param redis: redis, the instance
    :param token: mixed, access token
    """
    super(Set, self).__init__(redis, token)
    # set the default data type
    self._type = b'set'
    self._initiate()

  def __contains__(self, item):
    """
    Check if item exists in set
    :param item: mixed, item
    :return: bool, whether exists
    """
    return self._redis.sismember(
      self._token, self._dumps(item)
    )

  def __eq__(self, other):
    """
    Check if two sets are the same
    :param other: mixed, sequence
    :return: bool, whether equals
    """
    if isinstance(other, Set):
      return self._content == other._content \
        if self.length == other.length else False
    else:
      return self.content == other

  def __gt__(self, other):
    """
    Check if is strict superset
    :param other: mixed, sequence
    :return: bool, whether true
    """
    return self.__ne__(other) and self.__ge__(other)

  def __iter__(self):
    """
    Content iterator
    :return: generator
    """
    yield from map(
      lambda _: self._loads(_),
      self._redis.smembers(self._token)
    )

  def __len__(self):
    """
    Acquire current set length
    :return: int, the set length
    """
    return self._redis.scard(self._token)

  def __lt__(self, other):
    """
    Check if is strict subset of other
    :param other: mixed, sequence
    :return: bool, whether true
    """
    return self.__ne__(other) and self.__le__(other)

  def __ne__(self, other):
    """
    Check if not equal to other
    :param other: mixed, sequence
    :return: bool, whether true
    """
    return not self.__eq__(other)

  def __hash__(self):
    """
    Return the hash of the content
    :return: int, the hash
    """
    return self._content.__hash__()

  @property
  def _content(self):
    """
    Acquire raw contents in set
    :return: set, the raw content
    """
    return set(self._redis.smembers(self._token))

  @property
  def content(self):
    """
    Acquire parsed contents
    :return: set, the parsed content
    """
    return set(map(
      lambda _: self._loads(_),
      self._redis.smembers(self._token)
    ))

  @property
  def length(self):
    """
    Acquire current set length
    :return: int, set length
    """
    return self.__len__()

  @staticmethod
  def _filter(iterable):
    """
    Filter out tokens and other instances
    :param iterable: tuple, the arguments
    :return: tuple<map, map>, the results
    """
    # filter out tokens and other instances
    return (map(lambda _: _.token, filter(
      lambda _: isinstance(_, Set), iterable
    )), filter(
      lambda _: not isinstance(_, Set), iterable
    ))

  def add(self, *args):
    """
    Add a member to the set
    :param args: mixed, stray args
    :return: int, unique item added
    """
    return self._redis.sadd(
      self._token,
      *map(lambda _: self._dumps(_), args)
    )

  def copy(self):
    """
    Create a new instance
    :return: instance
    """
    instance = Set(self._redis, self._token)
    instance.serialize = self._serialize
    return instance

  def difference(self, *args):
    """
    Get the difference between sequences
    :param args: other sequences
    :return: set, the difference
    """
    tokens, others = self._filter(args)
    # return the differences
    return set(map(
      lambda _: self._loads(_),
      self._redis.sdiff(self._token, *tokens)
    )).difference(*others)

  # aliases for differences
  __sub__ = __rsub__ = difference

  def difference_update(self, *args):
    """
    Acquire difference and update self
    :param args: other sequences
    :return: None
    """
    tokens, others = self._filter(args)
    # update differences using tokens
    self._redis.sdiffstore(
      self._token, self._token, *tokens
    )
    # discard any common items from set
    self.discard(
      *self.content.intersection(*others)
    )

  # aliases for difference update
  __isub__ = difference_update

  def discard(self, *args):
    """
    Discard members from set
    :param args: mixed, stray values
    :return: int, removed count
    """
    return self._redis.srem(
      self._token,
      *map(lambda _: self._dumps(_), args)
    )

  # aliases for discard
  remove = discard

  def intersection(self, *args):
    """
    Get intersection of sequences
    :param args: other sequences
    :return: set, the intersection
    """
    tokens, others = self._filter(args)
    # redis intersect using tokens
    intersect = set(map(
      lambda _: self._loads(_),
      self._redis.sinter(self._token, *tokens)
    ))
    # return the intersection of all items
    return intersect.intersection(*others)

  # aliases for intersection
  __and__ = __rand__ = intersection

  def intersection_update(self, *args):
    """
    Get intersection and update self
    :param args: other sequences
    :return: None
    """
    tokens, others = self._filter(args)
    # update intersections using tokens
    self._redis.sinterstore(
      self._token, self._token, *tokens
    )
    # discard any stray items from set
    self.discard(
      *self.content.difference(*others)
    )

  # aliases for intersection update
  __iand__ = intersection_update

  def isdisjoint(self, other):
    """
    Check if self and other is disjoint
    :param other: other sequence
    :return: bool, whether is disjoint
    """
    if isinstance(other, Set):
      return len(self._redis.sinter(
        self._token, other._token
      )) == 0
    else:
      return self.content.isdisjoint(other)

  def issubset(self, other):
    """
    Check if self is a subset of other
    :param other: mixed, sequence
    :return: bool, whether is subset
    """
    if isinstance(other, Set):
      return self._redis.sunion(
        self._token, other._token
      ) == other._content
    else:
      return self.content.issubset(other)

  # aliases for issubset
  __le__ = issubset

  def issuperset(self, other):
    """
    Check if self is a superset of other
    :param other: mixed, sequence
    :return: bool, whether is superset
    """
    if isinstance(other, Set):
      return self._redis.sunion(
        self._token, other._token
      ) == self._content
    else:
      return self.content.issuperset(other)

  # aliases for issuperset
  __ge__ = issubset

  def pop(self):
    """
    Return an arbitrary element
    :return: mixed, an item
    """
    return self._loads(self._redis.spop(self._token))

  def symmetric_difference(self, other):
    """
    Get symmetric diff of sequences
    :param other: mixed, sequence
    :return: set, the intersection
    """
    return self.union(other) - self.intersection(other)

  # aliases for symmetric difference
  __xor__ = __rxor__ = symmetric_difference

  def symmetric_difference_update(self, other):
    """
    Get symmetric diff and update self
    :param other: mixed, sequence
    :return: None
    """
    intersect = self.intersection(other)
    self.union_update(other)
    self.discard(*intersect)

  # aliases for symmetric difference update
  __ixor__ = symmetric_difference_update

  def union(self, *args):
    """
    Get the union of sequences
    :param args: other sequences
    :return: set, the intersection
    """
    tokens, others = self._filter(args)
    # redis union using tokens
    union = set(map(
      lambda _: self._loads(_),
      self._redis.sunion(self._token, *tokens)
    ))
    # return the intersection of all items
    return union.union(*others)

  # aliases for union
  __or__ = __ror__ = union

  def union_update(self, *args):
    """
    Get the union and update self
    :param args: other sequences
    :return: None
    """
    tokens, others = self._filter(args)
    # update union using tokens
    self._redis.sunionstore(
      self._token, self._token, *tokens
    )
    # add any stray items to set
    self.update(*others)

  # aliases for union update
  __ior__ = union_update

  def update(self, *args):
    """
    Update the set with members
    :param args: other iterable
    :return: None
    """
    for item in args: self.add(*item)

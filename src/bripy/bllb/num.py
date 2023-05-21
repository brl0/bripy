"""Silly experiment with a number class that can be iterated over."""

import math
from collections.abc import Iterable
from functools import total_ordering
from itertools import islice

import toolz


def key_func(*args, **kwargs):
    args = args[0]
    _args = [hash(args[0])]
    for arg in args[1:]:
        if isinstance(arg, list):
            _args.append(tuple(arg))
        elif isinstance(arg, slice):
            _args.append((arg.start, arg.stop, arg.step))
        else:
            _args.append(arg)
    key = tuple(_args)
    if kwargs:
        key = key + tuple(sorted(kwargs.items()))
    return key


@total_ordering
class Num:
    def __init__(self, num) -> None:
        self.num = num
        self.size = abs(num)
        self.sign = 1 if num >= 0 else -1
        self.range = range(0, self.num, self.sign)
        self.reset()

    def reset(self):
        self.iter = self._get_iter()

    def _get_iter(self):
        return iter(map(type(self), self.range))

    def __iter__(self):
        return self._get_iter()

    def __next__(self):
        try:
            out = next(self.iter)
            if out == self.num - self.sign:
                self.reset()
            return out
        except StopIteration:
            self.reset()
            raise

    def __repr__(self) -> str:
        return f"Num({self.num})"

    def __str__(self) -> str:
        return str(self.num)

    def __len__(self) -> int:
        return self.size

    def __hash__(self) -> int:
        return hash(self.num) + hash(type(self))

    def _other(self, other):
        if hasattr(other, "num"):
            other = other.num
        return other

    def __eq__(self, other):
        return self.num == self._other(other)

    def __lt__(self, other):
        return self.num < self._other(other)

    def __contains__(self, item):
        return item in self.range

    def __bool__(self):
        return bool(self.num)

    @toolz.functoolz.memoize(key=key_func)
    def __getitem__(self, index):
        """Get item, items, or slice of items, accepts int, list, or slice."""
        if isinstance(index, int):
            if index < 0:
                index = self.size + index
            if index >= self.size or index < 0:
                return None
            return toolz.nth(index, self._get_iter())
        elif isinstance(index, Iterable):
            return type(index)(toolz.pluck(index, (self,)))
        elif isinstance(index, slice):
            return tuple(islice(self, index.start, index.stop, index.step))
        else:
            raise TypeError(f"Invalid index type: {type(index)}")

    def _convert(self, result):
        if isinstance(result, (type(self), Iterable)):
            return result
        try:
            _result = int(result)
            if _result == result:
                result = _result
        except TypeError:
            pass
        try:
            return type(self)(result)
        except TypeError:
            return result

    def __add__(self, other):
        return self._convert(self.num + self._other(other))

    def __sub__(self, other):
        return self._convert(self.num - self._other(other))

    def __mul__(self, other):
        return self._convert(self.num * self._other(other))

    def __floordiv__(self, other):
        return self._convert(self.num // self._other(other))

    def __truediv__(self, other):
        return self._convert(self.num / self._other(other))

    def __mod__(self, other):
        return self._convert(self.num % self._other(other))

    def __pow__(self, other):
        return self._convert(self.num ** self._other(other))

    def __lshift__(self, other):
        return self._convert(self.num << self._other(other))

    def __rshift__(self, other):
        return self._convert(self.num >> self._other(other))

    def __and__(self, other):
        return self._convert(self.num & self._other(other))

    def __xor__(self, other):
        return self._convert(self.num ^ self._other(other))

    def __or__(self, other):
        return self._convert(self.num | self._other(other))

    def __radd__(self, other):
        return type(other)(self._other(other) + self.num)

    def __rsub__(self, other):
        return type(other)(self._other(other) - self.num)

    def __rmul__(self, other):
        return type(other)(self._other(other) * self.num)

    def __rfloordiv__(self, other):
        return type(other)(self._other(other) // self.num)

    def __rtruediv__(self, other):
        return type(other)(self._other(other) / self.num)

    def __rmod__(self, other):
        return type(other)(self._other(other) % self.num)

    def __rpow__(self, other):
        return type(other)(self._other(other) ** self.num)

    def __rlshift__(self, other):
        return type(other)(self._other(other) << self.num)

    def __rrshift__(self, other):
        return type(other)(self._other(other) >> self.num)

    def __rand__(self, other):
        return type(other)(self._other(other) & self.num)

    def __rxor__(self, other):
        return type(other)(self._other(other) ^ self.num)

    def __ror__(self, other):
        return type(other)(self._other(other) | self.num)

    def __iadd__(self, other):
        self.num += self._other(other)
        return self

    def __isub__(self, other):
        self.num -= self._other(other)
        return self

    def __imul__(self, other):
        self.num *= self._other(other)
        return self

    def __ifloordiv__(self, other):
        self.num //= self._other(other)
        return self

    def __itruediv__(self, other):
        self.num /= self._other(other)
        return self

    def __imod__(self, other):
        self.num %= self._other(other)
        return self

    def __ipow__(self, other):
        self.num **= self._other(other)
        return self

    def __ilshift__(self, other):
        self.num <<= self._other(other)
        return self

    def __irshift__(self, other):
        self.num >>= self._other(other)
        return self

    def __iand__(self, other):
        self.num &= self._other(other)
        return self

    def __ixor__(self, other):
        self.num ^= self._other(other)
        return self

    def __ior__(self, other):
        self.num |= self._other(other)
        return self

    def __neg__(self):
        return self._convert(-self.num)

    def __pos__(self):
        return self._convert(+self.num)

    def __abs__(self):
        return self._convert(self.size)

    def __invert__(self):
        return self._convert(~self.num)

    def __int__(self):
        return int(self.num)

    def __float__(self):
        return float(self.num)

    def __complex__(self):
        return complex(self.num)

    def __round__(self, n=None):
        return self._convert(round(self.num, n))

    def __floor__(self):
        return self._convert(math.floor(self.num))

    def __ceil__(self):
        return self._convert(math.ceil(self.num))

    def __trunc__(self):
        return self._convert(math.trunc(self.num))

    def __index__(self):
        return int(self)

    def __matmul__(self, other):
        return [list(self)] * self._other(other)

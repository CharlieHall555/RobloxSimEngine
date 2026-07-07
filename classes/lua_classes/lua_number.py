import math

class LuaNumber:
    __slots__ = ("value",)

    def __init__(self, value):
        try:
            self.value = float(value)
        except (TypeError, ValueError):
            raise TypeError(f"cannot convert {value!r} to a LuaNumber")

    def __add__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(self.value + v2)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(self.value - v2)

    def __rsub__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(v2 - self.value)

    def __mul__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(self.value * v2)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(self.value / v2)

    def __rtruediv__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(v2 / self.value)

    def __mod__(self, other):
        v2 = _coerce_to_float(other)
        if v2 == 0.0:
            return LuaNumber(self.value - math.floor(self.value / v2) * v2)
        return LuaNumber(self.value - math.floor(self.value / v2) * v2)

    def __rmod__(self, other):
        v2 = _coerce_to_float(other)
        if self.value == 0.0:
            return LuaNumber(v2 - math.floor(v2 / self.value) * self.value)
        return LuaNumber(v2 - math.floor(v2 / self.value) * self.value)

    def __pow__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(self.value ** v2)

    def __rpow__(self, other):
        v2 = _coerce_to_float(other)
        return LuaNumber(v2 ** self.value)

    def __neg__(self):
        return LuaNumber(-self.value)

    def __eq__(self, other):
        if isinstance(other, LuaNumber):
            return self.value == other.value
        if isinstance(other, (int, float)):
            return self.value == float(other)
        return NotImplemented

    def __gt__(self, other):

        if isinstance(other, LuaNumber):
            return self.value > other.value
        if isinstance(other, (int, float)):
            return self.value > float(other)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, LuaNumber):
            return self.value >= other.value
        if isinstance(other, (int, float)):
            return self.value >= float(other)
        return NotImplemented

    def __lt__(self, other):

        if isinstance(other, LuaNumber):
            return self.value < other.value
        if isinstance(other, (int, float)):
            return self.value < float(other)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, LuaNumber):
            return self.value <= other.value
        if isinstance(other, (int, float)):
            return self.value <= float(other)
        return NotImplemented

    def __float__(self):
        return self.value

    def __int__(self):
        return int(self.value)

    def __bool__(self):
        return True

    def __str__(self):
        return format(self.value, ".14g")

    def __repr__(self):
        return f"LuaNumber({format(self.value, '.14g')})"

    def __hash__(self):
        return hash(self.value)
    
    def to_number(self):
        """Return an int if this number has no fractional part, otherwise a float."""
        if self.value.is_integer():
            return int(self.value)
        return float(self.value)
    
def _coerce_to_float(x):
    if isinstance(x, LuaNumber):
        return x.value
    if isinstance(x, (int, float)):
        return float(x)
    raise TypeError(f"unsupported operand type(s) for LuaNumber operation: '{type(x).__name__}'")    
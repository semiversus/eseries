from bisect import bisect_right, bisect_left
from typing import Tuple, Generator
from math import log10, floor


class ESeries:
    _instances = []

    def __init__(self, name: str, tolerance: float, base_exponent: int, base_values: Tuple[int, ...]):
        self._name = name
        self._tolerance = tolerance
        self._base_exponent = base_exponent
        self._base_values = base_values
        ESeries._instances.append(self)
    
    @classmethod
    def get_instances(cls) -> Tuple['ESeries']:
        """ Get a tuple with all the ESeries instances.

        >>> ESeries.get_instances()
        (E3, E6, E12, E24, E48, E96, E192)
        """
        return tuple(cls._instances)
    
    def __repr__(self) -> str:
        return self._name
    
    def iterate_up(self, value: float) -> Generator[float, None, None]:
        exponent_offset = floor(log10(value) - self._base_exponent)
        index = bisect_left(self._base_values, value / (10 ** exponent_offset))
            
        while True:
            if index >= len(self._base_values):
                index = 0
                exponent_offset += 1

            if exponent_offset < 0:
                # improving floating point result by doing division or multiplication depending on exponent_offset
                yield self._base_values[index] / (10 ** -exponent_offset)
            else:    
                yield self._base_values[index] * (10 ** exponent_offset)

            index += 1
    
    def iterate_down(self, value: float) -> Generator[float, None, None]:
        exponent_offset = floor(log10(value) - self._base_exponent)
        index = bisect_right(self._base_values, value / (10 ** exponent_offset)) - 1
            
        while True:
            if index < 0:
                index = len(self._base_values) - 1
                exponent_offset -= 1

            if exponent_offset < 0:
                # improving floating point result by doing division or multiplication depending on exponent_offset
                yield self._base_values[index] / (10 ** -exponent_offset)
            else:    
                yield self._base_values[index] * (10 ** exponent_offset)

            index -= 1

    def range(self, start: float, stop: float, include_stop: bool = False) -> Generator[float, None, None]:
        """Generate E values in a range inclusive of the start and stop values.

        :param start: The beginning of the range. The yielded values may include this value.
        :param stop: The end of the range. The yielded values may include this value.
        :param include_stop: If True, the yielded values may include the stop value.

        :yields:
            Values from the specified range which lie between the start and stop
            values, and in order from lowest to highest.
        """
        for value in self.iterate_up(start):
            if (include_stop and value > stop) or (not include_stop and value >= stop):
                return
            yield value

    def __iter__(self):
        return self.range(1, 10).__iter__()
    
    def __len__(self):
        return len(self._base_values)
    
    def find_nearest(self, value: float) -> float:
        """Find the nearest value.

        :param value: The value for which the nearest value is to be found.

        :returns:
            The value in the specified E-series closest to value.
        """
        v1 = self.find_greater_than_or_equal(value)
        v2 = self.find_less_than_or_equal(value)
        return v1 if abs(v1 / value - 1) < abs(v2 / value - 1) else v2

    def __getitem__(self, key):
        """ Find the nearest value or return a tuple when a slice is used.

        >>> E12[31]
        33
        >>> E12[31:680]
        (33, 39, 47, 56, 68, 82, 100, 120, 150, 180, 220, 270, 330, 390, 470, 560)
        """
        if isinstance(key, slice):
            values = tuple(self.range(key.start, key.stop))
            if key.step is not None:
                return values[::key.step]
            return values
        
        return self.find_nearest(key)
    
    def find_greater_than_or_equal(self, value: float) -> float:
        """Find the smallest value greater-than or equal-to the given value.

        :param value: The query value.

        :returns:
            The smallest value from the specified series which is greater-than
            or equal-to the query value.
        """
        return next(self.iterate_up(value))

    def find_greater_than(self, value: float) -> float:
        """Find the smallest value greater-than or equal-to the given value.

        :param value: The query value.

        :returns:
            The smallest value from the specified series which is greater-than
            the query value.
        """
        return next(v for v in self.iterate_up(value) if v != value)

    def find_less_than_or_equal(self, value: float) -> float:
        """Find the largest value less-than or equal-to the given value.

        :param value: The query value.

        :returns:
            The largest value from the specified series which is less-than
            or equal-to the query value.
        """
        return next(self.iterate_down(value))

    def find_less_than(self, value):
        """Find the largest value less-than or equal-to the given value.

        :param value: The query value.
        
        :returns:
            The largest value from the specified series which is less-than
            the query value.
        """
        return next(v for v in self.iterate_down(value) if v != value)

    def __lt__(self, other: float) -> float:
        return self.find_less_than(other)
    
    def __le__(self, other: float) -> float:
        return self.find_less_than_or_equal(other)

    def __gt__(self, other: float) -> float:
        return self.find_greater_than(other)
    
    def __ge__(self, other: float) -> float:
        return self.find_greater_than_or_equal(other)

    @property
    def tolerance(self) -> float:
        return self._tolerance
    
    def lower_tolerance_limit(self, value: float) -> float:
        """The lower limit for a nominal value of a series.

        :param value: A nominal value. This value need not be an member of
                the specified E-series.

        :returns:
            The lower tolerance limit for the nominal value based on the
            E-series tolerance.
        """
        return value - value * self._tolerance

    def upper_tolerance_limit(self, value: float) -> float:
        """The upper limit for a nominal value of a series.

        :param value: A nominal value. This value need not be an member of
                      the specified E-series.

        :returns:
            The upper tolerance limit for the nominal value based on the
            E-series tolerance.
        """
        return value + value * self._tolerance


    def tolerance_limits(self, value: float) -> Tuple[float, float]:
        """The lower and upper tolerance limits for a nominal value of a series.

        :param value: A nominal value. This value need not be an member of
                      the specified E-series.

        :returns:
            A 2-tuple containing the lower and upper tolerance limits for the
            nominal value based on the E-series tolerance.
        """
        return (value - value * self._tolerance, value + value * self._tolerance)


E3 = ESeries('E3', 0.4, 1, (10, 22, 47) )
E6 = ESeries('E6', 0.2, 1, (10, 15, 22, 33, 47, 68) )
E12 = ESeries('E12', 0.1, 1, (10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82) )
E24 = ESeries('E24', 0.05, 1, (10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75,
                               82, 91) )
E48 = ESeries('E48', 0.02, 2, (100, 105, 110, 115, 121, 127, 133, 140, 147, 154, 162, 169, 178, 187, 196, 205, 215,
                               226, 237, 249, 261, 274, 287, 301, 316, 332, 348, 365, 383, 402, 422, 442, 464, 487,
                               511, 536, 562, 590, 619, 649, 681, 715, 750, 787, 825, 866, 909, 953) )
E96 = ESeries('E96', 0.01, 2, (100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147,
                               150, 154, 158, 162, 165, 169, 174, 178, 182, 187, 191, 196, 200, 205, 210, 215, 221,
                               226, 232, 237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309, 316, 324, 332,
                               340, 348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442, 453, 464, 475, 487, 499,
                               511, 523, 536, 549, 562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732, 750,
                               768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976) )
E192 = ESeries('E192', 0.005, 2, (100, 101, 102, 104, 105, 106, 107, 109, 110, 111, 113, 114, 115, 117, 118, 120, 121,
                                  123, 124, 126, 127, 129, 130, 132, 133, 135, 137, 138, 140, 142, 143, 145, 147, 149,
                                  150, 152, 154, 156, 158, 160, 162, 164, 165, 167, 169, 172, 174, 176, 178, 180, 182,
                                  184, 187, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213, 215, 218, 221, 223,
                                  226, 229, 232, 234, 237, 240, 243, 246, 249, 252, 255, 258, 261, 264, 267, 271, 274,
                                  277, 280, 284, 287, 291, 294, 298, 301, 305, 309, 312, 316, 320, 324, 328, 332, 336,
                                  340, 344, 348, 352, 357, 361, 365, 370, 374, 379, 383, 388, 392, 397, 402, 407, 412,
                                  417, 422, 427, 432, 437, 442, 448, 453, 459, 464, 470, 475, 481, 487, 493, 499, 505,
                                  511, 517, 523, 530, 536, 542, 549, 556, 562, 569, 576, 583, 590, 597, 604, 612, 619,
                                  626, 634, 642, 649, 657, 665, 673, 681, 690, 698, 706, 715, 723, 732, 741, 750, 759,
                                  768, 777, 787, 796, 806, 816, 825, 835, 845, 856, 866, 876, 887, 898, 909, 920, 931,
                                  942, 953, 965, 976, 988) )


def series_from_name(name: str) -> ESeries:
    """Get an ESeries from its name.

    Args:
        name: The series name as a string, for example 'E24'

    Returns:
        An ESeries object which can be uses as a series_key.

    Raises:
        ValueError: If not such series exists.
    """
    instances = ESeries.get_instances()
    try:
        return next(series for series in instances if str(series) == name)
    except StopIteration:
        raise ValueError(f"E-series with name {name} not found. Available E-series keys are "
                         f"{', '.join(str(series) for series in instances)}")

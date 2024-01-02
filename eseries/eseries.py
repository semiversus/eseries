from bisect import bisect_right, bisect_left
from typing import Tuple, Generator
from math import log10, floor


_BASE_LOG = 2


class ESeries:
    _instances = []

    def __init__(self, name: str, tolerance: float, base_values: Tuple[int, ...]):
        self.name = name
        self.tolerance = tolerance
        self.base_values = base_values
        ESeries._instances.append(self)
    
    @classmethod
    def get_instances(cls) -> Tuple['ESeries']:
        return tuple(cls._instances)
    
    def __str__(self) -> str:
        return self.name

    def _iterate_from(self, value: float, upwards: bool = True) -> Generator[float, None, None]:
        exponent_offset = floor(log10(value) - _BASE_LOG)
        mantissa = value / (10 ** exponent_offset)
        
        if upwards:
            index = bisect_left(self.base_values, mantissa)
        else:
            index = bisect_right(self.base_values, mantissa) - 1
            
        while True:
            if index >= len(self.base_values):
                index = 0
                exponent_offset += 1 if upwards else -1

            if exponent_offset < 0:
                # improving floating point result by doing division or multiplication depending on exponent_offset
                yield self.base_values[index] / (10 ** -exponent_offset)
            else:    
                yield self.base_values[index] * (10 ** exponent_offset)
            index += 1 if upwards else -1

    def find_greater_than_or_equal(self, value: float) -> float:
        """Find the smallest value greater-than or equal-to the given value.

        :param value: The query value.

        :returns:
            The smallest value from the specified series which is greater-than
            or equal-to the query value.
        """
        return next(self._iterate_from(value))

    def find_greater_than(self, value: float) -> float:
        """Find the smallest value greater-than or equal-to the given value.

        :param value: The query value.

        :returns:
            The smallest value from the specified series which is greater-than
            the query value.
        """
        return next(v for v in self._iterate_from(value) if v != value)

    def find_less_than_or_equal(self, value: float) -> float:
        """Find the largest value less-than or equal-to the given value.

        :param value: The query value.

        :returns:
            The largest value from the specified series which is less-than
            or equal-to the query value.
        """
        return next(self._iterate_from(value, upwards=False))

    def find_less_than(self, value):
        """Find the largest value less-than or equal-to the given value.

        :param value: The query value.
        
        :returns:
            The largest value from the specified series which is less-than
            the query value.
        """
        return next(v for v in self._iterate_from(value, upwards=False) if v != value)

    def __lt__(self, other: float) -> float:
        return self.find_less_than(other)
    
    def __le__(self, other: float) -> float:
        return self.find_less_than_or_equal(other)

    def __gt__(self, other: float) -> float:
        return self.find_greater_than(other)
    
    def __ge__(self, other: float) -> float:
        return self.find_greater_than_or_equal(other)

    def find_nearest(self, value: float) -> float:
        """Find the nearest value.

        :param value: The value for which the nearest value is to be found.

        :returns:
            The value in the specified E-series closest to value.
        """
        v1 = self.find_greater_than_or_equal(value)
        v2 = self.find_less_than_or_equal(value)
        return v1 if abs(v1 / value - 1) < abs(v2 / value - 1) else v2

    def __eq__(self, value: float) -> float:
        return self.find_nearest(value)
        
    def range(self, start: float, stop: float, open: bool = True):
        """Generate E values in a range inclusive of the start and stop values.

        :param start: The beginning of the range. The yielded values may include this value.
        :param stop: The end of the range. The yielded values may include this value.

        :yields:
            Values from the specified range which lie between the start and stop
            values inclusively, and in order from lowest to highest.
        """
        g = self._iterate_from(start)
        
        while True:
            value = next(g)
            if (open and value >= stop) or (not open and value > stop):
                return
            yield value
    
    def lower_tolerance_limit(self, value: float) -> float:
        """The lower limit for a nominal value of a series.

        :param value: A nominal value. This value need not be an member of
                the specified E-series.

        :returns:
            The lower tolerance limit for the nominal value based on the
            E-series tolerance.
        """
        return value - value * self.tolerance

    def upper_tolerance_limit(self, value: float) -> float:
        """The upper limit for a nominal value of a series.

        :param value: A nominal value. This value need not be an member of
                      the specified E-series.

        :returns:
            The upper tolerance limit for the nominal value based on the
            E-series tolerance.
        """
        return value + value * self.tolerance


    def tolerance_limits(self, value: float) -> Tuple[float, float]:
        """The lower and upper tolerance limits for a nominal value of a series.

        :param value: A nominal value. This value need not be an member of
                      the specified E-series.

        :returns:
            A 2-tuple containing the lower and upper tolerance limits for the
            nominal value based on the E-series tolerance.
        """
        return (value - value * self.tolerance, value + value * self.tolerance)


E3 = ESeries( 'E3', 0.4, (100, 220, 470) )
E6 = ESeries( 'E6', 0.2, (100, 150, 220, 330, 470, 680) )
E12 = ESeries( 'E12', 0.1, (100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820) )
E24 = ESeries( 'E24', 0.05, (100, 110, 120, 130, 150, 160, 180, 200, 220, 240, 270, 300, 330, 360, 390, 430, 470, 510,
                             560, 620, 680, 750, 820, 910) )
E48 = ESeries( 'E48', 0.02, (100, 105, 110, 115, 121, 127, 133, 140, 147, 154, 162, 169, 178, 187, 196, 205, 215, 226,
                             237, 249, 261, 274, 287, 301, 316, 332, 348, 365, 383, 402, 422, 442, 464, 487, 511, 536,
                             562, 590, 619, 649, 681, 715, 750, 787, 825, 866, 909, 953) )
E96 = ESeries( 'E96', 0.01, (100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150,
                             154, 158, 162, 165, 169, 174, 178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232,
                             237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309, 316, 324, 332, 340, 348, 357,
                             365, 374, 383, 392, 402, 412, 422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549,
                             562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732, 750, 768, 787, 806, 825, 845,
                             866, 887, 909, 931, 953, 976) )
E192 = ESeries( 'E192', 0.005, (100, 101, 102, 104, 105, 106, 107, 109, 110, 111, 113, 114, 115, 117, 118, 120, 121,
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


def series_from_name(name) -> ESeries:
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
        return next(series for series in instances if series.name == name)
    except StopIteration:
        raise ValueError("E-series with name {!r} not found. Available E-series keys are {}"
                         .format(name, ', '.join(str(series) for series in instances)))

import math

from .eseries import EBase, series_from_name

_MINIMUM_E_VALUE = 1e-200

ESeries = EBase.get_instances()


def series(series_key):
    """The base values for the given E-series.

    Args:
        series_key: An E-Series key such as E24.

    Returns:
        A tuple of base value for the series. For example, for
        E3 the tuple (10, 22, 47) will be returned.

    Raises:
        ValueError: If not such series exists.
    """
    try:
        return tuple(series_key)
    except TypeError:
        raise ValueError("E-series {} not found. Available E-series keys are {}"
                         .format(series_key,
                                 ', '.join(str(key) for key in series_keys())))


def series_keys():
    """The available series keys.

    Note:
        The series keys returned will be members of the ESeries enumeration.
        These are useful for programmatic use. For constant values consider
        using the module aliases E3, E6, E12, etc.

    Returns:
        A set-like object containing the series-keys.
    """
    return tuple(str(s) for s in EBase.get_instances())


def series_key_from_name(name):
    """Get an ESeries from its name.

    Args:
        name: The series name as a string, for example 'E24'

    Returns:
        An ESeries object which can be uses as a series_key.

    Raises:
        ValueError: If not such series exists.
    """
    try:
        return series_from_name(name)
    except KeyError:
        raise ValueError("E-series with name {!r} not found. Available E-series keys are {}"
                         .format(name,
                                 ', '.join(str(key.name) for key in series_keys())))

def tolerance(series_key):
    """The nominal tolerance of an E Series.

    Args:
        series_key: An E-Series key such as E24.

    Returns:
        A float between zero and one. For example 0.1 indicates a 10% tolerance.

    Raises:
        ValueError: For an unknown E-Series.
    """
    try:
        return series_key.tolerance
    except AttributeError:
        raise ValueError("E-series {} not found. Available E-series keys are {}"
                         .format(series_key,
                                 ', '.join(str(key) for key in series_keys())))


def find_greater_than_or_equal(series_key, value):
    """Find the smallest value greater-than or equal-to the given value.

    Args:
        series_key: An E-Series key such as E24.
        value: The query value.

    Returns:
        The smallest value from the specified series which is greater-than
        or equal-to the query value.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If value is not finite.
        ValueError: If value is out of range.
    """
    return series_key.find_greater_than_or_equal(value)


def find_greater_than(series_key, value):
    """Find the smallest value greater-than or equal-to the given value.

    Args:
        series_key: An E-Series key such as E24.
        value: The query value.

    Returns:
        The smallest value from the specified series which is greater-than
        the query value.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If value is not finite.
        ValueError: If value is out of range.
    """
    return series_key.find_greater_than(value)



def find_less_than_or_equal(series_key, value):
    """Find the largest value less-than or equal-to the given value.

    Args:
        series_key: An E-Series key such as E24.
        value: The query value.

    Returns:
        The largest value from the specified series which is less-than
        or equal-to the query value.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If value is not finite.
        ValueError: If value is out of range.
    """
    return series_key.find_less_than_or_equal(value)



def find_less_than(series_key, value):
    """Find the largest value less-than or equal-to the given value.

    Args:
        series_key: An E-Series key such as E24.
        value: The query value.

    Returns:
        The largest value from the specified series which is less-than
        the query value.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If value is not finite.
        ValueError: If value is out of range.
    """
    return series_key.find_less_than(value)


def find_nearest(series_key, value):
    """Find the nearest value.

    Args:
        series_key: The ESeries to use.
        value: The value for which the nearest value is to be found.

    Returns:
        The value in the specified E-series closest to value.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If value is not finite.
        ValueError: If value is out of range.
    """
    return series_key.find_nearest(value)


def find_nearest_few(series_key, value, num=3):
    """Find the nearest values.

    Args:
        series_key: The ESeries to use.
        value: The value for which the nearest values are to be found.
        num: The number of nearby values to find: 1, 2 or 3.

    Returns:
        A tuple containing num values. With num == 3 it is guaranteed
        that  at least one item less than value, and one item greater
        than value.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If num is not 1, 2 or 3.
        ValueError: If value is not finite.
        ValueError: If value is out of range.
    """
    if num not in {1, 2, 3}:
        raise ValueError("num {} is not 1, 2 or 3".format(num))
    g_down = series_key.iterate_down(value)
    nearest = next(g_down)
    if num == 1:
        return (nearest,)
    lower = next(g_down)
    if num == 2:
        return (lower, nearest,)
    g_up = series_key.iterate_up(value)
    bigger = next(g_up)
    if bigger == nearest:
        bigger = next(g_up)
    return (lower, nearest, bigger)
        

def erange(series_key, start, stop):
    """Generate  E values in a range inclusive of the start and stop values.

    Args:
        series_key: The ESeries to use.
        start: The beginning of the range. The yielded values may include this value.
        stop: The end of the range. The yielded values may include this value.

    Yields:
        Values from the specified range which lie between the start and stop
        values inclusively, and in order from lowest to highest.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If start is not less-than or equal-to stop.
        ValueError: If start or stop are not both finite.
        ValueError: If start or stop are out of range.
    """
    if math.isinf(start):
        raise ValueError("Start value {} is not finite".format(start))
    if math.isinf(stop):
        raise ValueError("Stop value {} is not finite".format(stop))
    if start < _MINIMUM_E_VALUE:
        raise ValueError("{} is too small. The start value must greater than or equal to {}".format(stop, _MINIMUM_E_VALUE))
    if stop < _MINIMUM_E_VALUE:
        raise ValueError("{} is too small. The stop value must greater than or equal to {}".format(stop, _MINIMUM_E_VALUE))
    if not start <= stop:
        raise ValueError("Start value {} must be less than stop value {}".format(start, stop))

    return series_key.range(start, stop, include_stop=True)


def open_erange(series_key, start, stop):
    """Generate E values in a half-open range inclusive of start, but exclusive of stop.

    Args:
        series_key: The ESeries to use.
        start: The beginning of the range. The yielded values may include this value.
        stop: The end of the range. The yielded values will not include this value.

    Yields:
        Values from the specified range which lie in the half-open range defined by
        the start and stop values, from lowest to highest.

    Raises:
        ValueError: If series_key is not known.
        ValueError: If start is not less-than or equal-to stop.
        ValueError: If start or stop are not both finite.
        ValueError: If start or stop are out of range.
    """
    if math.isinf(start):
        raise ValueError("Start value {} is not finite".format(start))
    if math.isinf(stop):
        raise ValueError("Stop value {} is not finite".format(stop))
    if start < _MINIMUM_E_VALUE:
        raise ValueError("{} is too small. The start value must greater than or equal to {}".format(stop, _MINIMUM_E_VALUE))
    if stop < _MINIMUM_E_VALUE:
        raise ValueError("{} is too small. The stop value must greater than or equal to {}".format(stop, _MINIMUM_E_VALUE))
    if not start <= stop:
        raise ValueError("Start value {} must be less than stop value {}".format(start, stop))

    return series_key.range(start, stop, include_stop=False)



def lower_tolerance_limit(series_key, value):
    """The lower limit for a nominal value of a series.

    Args:
        series_key: The ESeries to use.
        value: A nominal value. This value need not be an member of
            the specified E-series.

    Returns:
        The lower tolerance limit for the nominal value based on the
        E-series tolerance.

    Raises:
        ValueError: If series_key is not known.
    """
    return series_key.lower_tolerance_limit(value)


def upper_tolerance_limit(series_key, value):
    """The upper limit for a nominal value of a series.

    Args:
        series_key: The ESeries to use.
        value: A nominal value. This value need not be an member of
            the specified E-series.

    Returns:
        The upper tolerance limit for the nominal value based on the
        E-series tolerance.

    Raises:
        ValueError: If series_key is not known.
    """
    return series_key.upper_tolerance_limit(value)


def tolerance_limits(series_key, value):
    """The lower and upper tolerance limits for a nominal value of a series.

    Args:
        series_key: The ESeries to use.
        value: A nominal value. This value need not be an member of
            the specified E-series.

    Returns:
        A 2-tuple containing the lower and upper tolerance limits for the
        nominal value based on the E-series tolerance.

    Raises:
        ValueError: If series_key is not known.
    """
    return series_key.tolerance_limits(value)


def _round_sig(x, figures=6):
    return 0 if x == 0 else round(x, int(figures - math.floor(math.log10(abs(x))) - 1))


def _decade_mantissa(value):
    f_decade, mantissa = divmod(value, 1)
    return int(f_decade), mantissa

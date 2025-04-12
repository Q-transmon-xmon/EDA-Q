#########################################################################
# File Name: _utility.py
# Description: Provides a series of mathematical and string manipulation utility functions.
#              Includes polynomial operations, numerical formatting, vectorized function parameter handling, etc.
#########################################################################

from math import floor
import numpy as np
import functools
from warnings import warn
import sys
from scipy.optimize import root_scalar
from numpy.polynomial.polynomial import Polynomial as npPoly

exponent_to_letter = {
    -18: 'a',
    -15: 'f',
    -12: 'p',
    -9: 'n',
    -6: 'u',
    -3: 'm',
    0: '',
    3: 'k',
    6: 'M',
    9: 'G',
    12: 'T'
}
exponent_to_letter_unicode = {
    -18: 'a',
    -15: 'f',
    -12: 'p',
    -9: 'n',
    -6: u'\u03bc',
    -3: 'm',
    0: '',
    3: 'k',
    6: 'M',
    9: 'G',
    12: 'T'
}


def polish_roots(p, roots, maxiter, rtol):
    """
    Refines the roots of a polynomial.

    Input:
        p: Polynomial object.
        roots: List of polynomial roots.
        maxiter: Maximum number of iterations.
        rtol: Relative tolerance.

    Output:
        roots_refined: Refined array of polynomial roots.
    """
    roots_refined = []
    for r0 in roots:
        r = root_scalar(
            f=p,
            x0=r0,
            fprime=p.deriv(),
            fprime2=p.deriv(2),
            method='halley',
            maxiter=int(maxiter),
            rtol=rtol).root
        if np.absolute(np.imag(r)) < np.absolute(rtol * np.real(r)):
            r = np.real(r)
        if not True in np.isclose(r, roots_refined, rtol=rtol):
            roots_refined.append(r)
    return np.array(roots_refined)


def remove_multiplicity(p):
    """
    Removes multiple roots from a polynomial.

    Input:
        p: Polynomial object.

    Output:
        Resulting polynomial with multiple roots removed.
    """
    g = gcd(p, p.deriv())
    if g.degree() >= 1:
        return p // g
    else:
        # No multiple roots, use the original polynomial.
        return p


def gcd(u, v):
    """
    Computes the greatest common divisor of two integers or polynomials.

    Input:
        u: First integer or polynomial.
        v: Second integer or polynomial.

    Output:
        Greatest common divisor.
    """
    iterations = 0
    max_iterations = 1000
    while v != npPoly(0):
        u, v = v, u % v
        iterations += 1
        if iterations >= max_iterations:
            raise ValueError('gcd(u,v) failed to converge')

    return u


def refuse_vectorize_kwargs(func_to_evaluate=None, *, exclude=[]):
    """
    Decorator to refuse vectorization of function arguments.

    Input:
        func_to_evaluate: Function to decorate.
        exclude: List of parameters to exclude from vectorization.

    Output:
        Decorated function.
    """

    # Only works for functions which return a list

    def _decorate(func):
        @functools.wraps(func)
        def wrapper_vectorize(self, *args, **kwargs):
            non_iterables = {}
            iterables = {}
            for kw, arg in kwargs.items():
                if kw not in exclude:
                    try:
                        iter(arg)
                        raise ValueError("No iterables are allowed, use a single value for %s" % kw)
                    except TypeError:
                        # not an iterable
                        pass

            return func(self, *args, **kwargs)

        return wrapper_vectorize

    if func_to_evaluate:
        return _decorate(func_to_evaluate)
    return _decorate


def vectorize_kwargs(func_to_evaluate=None, *, exclude=[]):
    """
    Decorator to vectorize function arguments.

    Input:
        func_to_evaluate: Function to decorate.
        exclude: List of parameters to exclude from vectorization.

    Output:
        Decorated function.
    """

    # Only works for functions which return a list

    def _decorate(func):
        @functools.wraps(func)
        def wrapper_vectorize(self, *args, **kwargs):
            non_iterables = {}
            iterables = {}
            for kw, arg in kwargs.items():
                if kw in exclude:
                    non_iterables[kw] = arg
                else:
                    if np.any(np.array([arg]) == 0):
                        raise ValueError("Cannot set value of element %s to zero" % kw)
                    try:
                        iter(arg)
                    except TypeError:
                        # not an iterable
                        non_iterables[kw] = arg
                    else:
                        # is an iterable
                        # Make sure it has the same shape as other iterables
                        if len(iterables) > 0:
                            first_iterable = iterables[list(iterables)[0]]
                            if np.array(arg).shape != first_iterable.shape:
                                raise ValueError("Keyword arguments have incompatible shapes: %s %s and %s %s" % (
                                    list(iterables)[0],
                                    first_iterable.shape,
                                    kw,
                                    np.array(arg).shape
                                ))
                        iterables[kw] = np.array(arg)

            if len(iterables) == 0:
                return func(self, *args, **kwargs)
            else:
                first_iterable = iterables[list(iterables)[0]]
                kwargs_single = non_iterables
                i = 0
                for index, _ in np.ndenumerate(first_iterable):

                    for kw, arg in iterables.items():
                        kwargs_single[kw] = arg[index]

                    to_return_single = func(self, *args, **kwargs_single)

                    if i == 0:
                        try:
                            iter(to_return_single)
                            to_return = np.empty((*first_iterable.shape, *to_return_single.shape), dtype=np.complex128)
                        except TypeError:
                            # not an iterable
                            to_return = np.empty(first_iterable.shape, dtype=np.complex128)
                        i += 1

                    to_return[index] = to_return_single
                for i in range(len(first_iterable.shape)):
                    to_return = np.moveaxis(to_return, 0, -1)
                return to_return

        return wrapper_vectorize

    if func_to_evaluate:
        return _decorate(func_to_evaluate)
    return _decorate


def get_exponent_3(value):
    """
    Computes the exponent part of a value, making it a multiple of 3.

    Input:
        value: Numeric value.

    Output:
        exponent_3: Exponent part.
    """
    value = np.absolute(value)
    exponent = floor(np.log10(value))
    exponent_3 = exponent - (exponent % 3)
    return exponent_3


def exponent_3_to_string(value, exponent_3, use_power_10, use_unicode):
    """
    Converts the exponent part to a string.

    Input:
        value: Numeric value.
        exponent_3: Exponent part.
        use_power_10: Whether to use power of 10 notation.
        use_unicode: Whether to use Unicode characters.

    Output:
        exponent_part: String representation of the exponent part.
    """
    value = np.absolute(value)
    if use_power_10 or value >= 1e15 or value < 1e-18:
        if exponent_3 == 0:
            exponent_part = ''
        else:
            exponent_part = r'e%d' % exponent_3
    else:
        if use_unicode:
            exponent_part = ' ' + exponent_to_letter_unicode[exponent_3]
        else:
            exponent_part = ' ' + exponent_to_letter[exponent_3]
    return exponent_part


def get_float_part(v, exponent_3, maximum_info):
    """
    Gets the fractional part of a value.

    Input:
        v: Numeric value.
        exponent_3: Exponent part.
        maximum_info: Whether to display maximum information.

    Output:
        sign: Sign of the value.
        float_part: Fractional part of the value.
    """
    if v == 0:
        return '', '0'
    if v < 0:
        sign = '-'
        v *= -1
    elif v > 0:
        sign = ''
    float_part = v / (10 ** exponent_3)

    if maximum_info == False:
        if float_part >= 100.:
            float_part = "%2.0f." % (float_part)
        elif float_part >= 10.:
            float_part = "%1.1f" % (float_part)
        else:
            float_part = "%0.2f" % (float_part)
        # remove trailing 0s or .
        while float_part[-1] == "0":
            float_part = float_part[:-1]
        if float_part[-1] == ".":
            float_part = float_part[:-1]

    else:
        if (v - float("%2.6e" % v) != 0 and float_part >= 100.) \
                or (v - float("%1.6e" % v) != 0 and 100 > float_part >= 10.) \
                or (v - float("%.6e" % v) != 0 and float_part < 10.):
            # if there is a digit beyond digit 6
            float_part = "%2.6f.." % float_part
        else:
            float_part = "%.6f" % float_part
            while float_part[-1] == "0":
                float_part = float_part[:-1]
            if float_part[-1] == ".":
                float_part = float_part[:-1]
    return [sign, float_part]


def pretty_value(v, is_complex=True, use_power_10=False, use_unicode=True, maximum_info=False):
    """
    Formats a numeric value into a human-readable string, supporting complex and real numbers.

    Input:
        v: Numeric value.
        is_complex: Whether the value is complex, default is True.
        use_power_10: Whether to use power of 10 notation, default is False.
        use_unicode: Whether to use Unicode characters, default is True.
        maximum_info: Whether to display maximum information, default is False.

    Output:
        Formatted string representation of the numeric value.
    """
    if v == 0:
        return '0'

    if is_complex:
        exp3 = get_exponent_3(max(np.absolute(np.real(v)), np.absolute(np.imag(v))))
        exponent = exponent_3_to_string(max(np.absolute(np.real(v)), np.absolute(np.imag(v))), exp3, use_power_10,
                                        use_unicode)

        sign_r, numbers_r = get_float_part(np.real(v), exp3, maximum_info)
        sign_i, numbers_i = get_float_part(np.imag(v), exp3, maximum_info)

        to_return = ''
        if numbers_r.replace('0', '').replace('.', '') != '':
            to_return += sign_r + numbers_r
            if numbers_i.replace('0', '').replace('.', '') != '':
                if sign_i == '':
                    to_return += '+'
        if numbers_i.replace('0', '').replace('.', '') != '':
            to_return += sign_i + numbers_i + 'i'

        return to_return + exponent
    else:
        v = np.real(v)
        exp3 = get_exponent_3(v)
        exponent = exponent_3_to_string(v, exp3, use_power_10, use_unicode)
        sign, numbers = get_float_part(v, exp3, maximum_info)
        return sign + numbers + exponent


def shift(to_shift, shift):
    """
    Shifts each element in a list by a given amount.

    Input:
        to_shift: List to shift.
        shift: Shift amount.

    Output:
        Shifted list.
    """
    for i, _ in enumerate(to_shift):
        to_shift[i] += shift
    return to_shift


def to_string(unit, label, value, use_unicode=True, maximum_info=False):
    """
    Converts a numeric value to a string with unit and label.

    Input:
        unit: Unit string.
        label: Label string.
        value: Numeric value.
        use_unicode: Whether to use Unicode characters, default is True.
        maximum_info: Whether to display maximum information, default is False.

    Output:
        String representation of the numeric value with unit and label.
    """
    if unit is not None:
        if not use_unicode:
            unit = unit.replace(u"\u03A9", 'Ohm')
            unit = unit.replace(u'\u03bc', 'u')

    if label is None:
        s = ''
    else:
        s = label
        if value is not None:
            s += '='

    if value is not None:
        s += pretty_value(value, use_unicode=use_unicode, maximum_info=maximum_info)

        if unit is not None:
            s += unit
    return s
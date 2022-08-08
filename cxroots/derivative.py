from __future__ import division

import logging
import math

import numdifftools.fornberg as ndf
import numpy as np
from numpy import pi

from .contours.circle import Circle


@np.vectorize
def cx_derivative(f, z0, n=1, contour=None, integration_abs_tol=1e-10):
    r"""
    Compute the derivaive of an analytic function using Cauchy's
    Integral Formula for Derivatives.

    .. math::

        f^{(n)}(z_0) = \frac{n!}{2\pi i} \oint_C \frac{f(z)}{(z-z_0)^{n+1}} dz

    Parameters
    ----------
    f : function
        Function of a single variable f(x).
    z0 : complex
        Point to evaluate the derivative at.
    n : int
        The order of the derivative to evaluate.
    contour : :class:`Contour <cxroots.Contour.Contour>`, optional
        The contour, C, in the complex plane which encloses the point z0.
        By default the contour is the circle |z-z_0|=1e-3.
    integration_abs_tol : float, optional
        The absolute tolerance required of the integration routine.

    Returns
    -------
    f^{(n)}(z0) : complex
        The nth derivative of f evaluated at z0
    """
    if contour is None:
        contour = Circle(z0, 1e-3)

    def integrand(z):
        return f(z) / (z - z0) ** (n + 1)

    integral = contour.integrate(integrand, abs_tol=integration_abs_tol)
    return integral * math.factorial(n) / (2j * pi)


def find_multiplicity(root, f, df=None, root_err_tol=1e-10):
    """
    Find the multiplicity of a given root of f by computing the
    derivatives of f, f^{(1)}, f^{(2)}, ... until
    |f^{(n)}(root)|>root_err_tol.  The multiplicity of the root is then
    equal to n.  The derivative is calculated with `numdifftools.fornberg.ndf`
    which employs a method due to Fornberg.

    Parameters
    ----------
    root : complex
        A root of f, f(root)=0.
    f : function
        An analytic function of a single complex variable such that f(root)=0.
    df : function, optional
        The first derivative of f.  If not known then df=None.
    contour : Contour, optional
        The integration contour used to evaluate the derivatives.
    root_err_tol : float, optional
        It will be assumed that f(z)=0 if numerically |f(z)|<root_err_tol.

    Returns
    -------
    multiplicity : int
        The multiplicity of the given root.
    """
    logger = logging.getLogger(__name__)
    if abs(f(root)) > root_err_tol:
        raise ValueError(
            "The provided 'root' is not a root of the given function f."
            "Specifically, %f = abs(f(root)) > root_err_tol = %f"
            % (abs(f(root)), root_err_tol)
        )

    n = 1
    while True:
        if df is not None:
            if n == 1:
                err = abs(df(root))
            else:
                # ndf.derivative returns an array [f, f', f'', ...]
                err = abs(ndf.derivative(df, root, n - 1)[n - 1])
        else:
            err = abs(ndf.derivative(f, root, n)[n])

        logger.debug("n=%i |df^(n)|=%f", n, err)

        if err > root_err_tol:
            break

        n += 1

    return n
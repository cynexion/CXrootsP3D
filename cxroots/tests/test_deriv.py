import unittest
import numpy as np
from scipy import cos, sin

from cxroots import Circle, Rectangle
from cxroots import CxDerivative

class TestDerivative1(unittest.TestCase):
	def setUp(self):
		self.f  = lambda z: z**10 - 2*z**5 + sin(z)*cos(z/2)
		self.df = lambda z: 10*(z**9 - z**4) + cos(z)*cos(z/2) - 0.5*sin(z)*sin(z/2)

	def test_circle(self):
		C = Circle(0, 2)
		z = np.array([-1.234, 0.3+1j, 0.1j, -0.9-0.5j])

		df_approx = CxDerivative(self.f, n=1, contour=C)
		np.testing.assert_almost_equal(df_approx(z), self.df(z), decimal=1e-12)

	def test_rect(self):
		C = Rectangle([-1.5,1.5],[-2,2])
		z = np.array([-1.234, 0.3+1j, 0.1j, -0.9-0.5j])

		df_approx = CxDerivative(self.f, n=1, contour=C)
		np.testing.assert_almost_equal(df_approx(z), self.df(z), decimal=1e-12)

	def test_defaultCircle(self):
		z = 0.3+1j

		df_approx = CxDerivative(self.f, n=1)
		np.testing.assert_almost_equal(df_approx(z), self.df(z), decimal=1e-12)

class TestDerivativeCluster(unittest.TestCase):
	# What if there are roots on the default integration contour?
	def setUp(self):
		self.f  = lambda z: z*(z-1e-3)*(z-1e-3j)
		self.df = lambda z: (z-1e-3)*(z-1e-3j) + z*(z-1e-3j) + z*(z-1e-3)

	def test_derivative_cluster1(self):
		z = 0
		df_approx = CxDerivative(self.f, n=1)
		np.testing.assert_almost_equal(df_approx(z), self.df(z), decimal=1e-12)

	def test_derivative_cluster2(self):
		z = 1e-3j
		df_approx = CxDerivative(self.f, n=1)
		np.testing.assert_almost_equal(df_approx(z), self.df(z), decimal=1e-12)


if __name__ == '__main__':
	unittest.main()

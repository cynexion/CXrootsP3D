from __future__ import division
import numpy as np
import cmath
from scipy import pi, exp, sin
import scipy
from numpy.random import uniform
import itertools
from collections import deque
import logging

from .Contours import NonIntegerError
from .IterativeMethods import iterateToRoot

def subdivide(boxDeque, boxToSubdivide, boxToSubdivide_numberOfEnclosedZeros, func, dfunc, integerTol, rombergDivMax, reqEqualZeros):
	for subBoxes in boxToSubdivide.subdivisions():
		try:
			numberOfEnclosedZeros = [box.enclosed_zeros(func,dfunc,integerTol,rombergDivMax,reqEqualZeros) for box in np.array(subBoxes)]
			if boxToSubdivide_numberOfEnclosedZeros == sum(numberOfEnclosedZeros):
				break
		except (NonIntegerError, RuntimeError):
			# If the number of zeros within either of the new contours is not an integer then it is
			# likely that the introduced line which subdivides 'boxToSubdivide' lies on a zero.
			# To avoid this we will try to place the subdividing line at a different point along 
			# the division axis
			continue

	if boxToSubdivide_numberOfEnclosedZeros != sum(numberOfEnclosedZeros):
		# The list of subdivisions has been exhaused and still the number of enclosed zeros does not add up 
		raise RuntimeError("""Unable to subdivide box:
			\t%s
			If f and df have been given then try increasing rombergDivMax and decreasing the integerTol. 
			If only f has been provided then try increasing the reqEqualZeros.""" % boxToSubdivide)

	boxDeque.extend([(box, numberOfEnclosedZeros[i]) for i, box in enumerate(subBoxes) if numberOfEnclosedZeros[i] != 0])
		
def addRoot(root, roots, originalContour, f, df, guessRootSymmetry, newtonStepTol, rootErrTol, newtonMaxIter):
	# check that the root we have found is distinct from the ones we already have
	if not roots or np.all(abs(np.array(roots) - root) > newtonStepTol):
		# add the root to the list if it is within the original box
		if originalContour.contains(root):
			roots.append(root)

		# check to see if there are any other roots implied by the given symmetry
		if guessRootSymmetry is not None:
			for x0 in guessRootSymmetry(root):
				root = iterateToRoot(x0, f, df, newtonStepTol, rootErrTol, newtonMaxIter)
				if root is not None:
					addRoot(root, roots, originalContour, f, df, guessRootSymmetry, newtonStepTol, rootErrTol, newtonMaxIter)


def findRootsGen(originalContour, f, df=None, guessRoot=[], guessRootSymmetry=None, 
	newtonStepTol=1e-8, newtonMaxIter=20, rootErrTol=1e-10, iterativeTries=20,
	integerTol=0.1, rombergDivMax=10, reqEqualZeros=3):
	"""
	A generator which at each step takes a contour and either finds 
	all the zeros of f within it or subdivides it further.

	The method used to compute the number of zeros depends on whether
	the derivative, df, is provided.  See  

	Parameters
	----------
	originalContour : subclass of Contour
		The contour C which bounds the region in which all the 
		roots of f(z) are sought
	f : function
		A function of a single complex variable f(z) which is 
		analytic within C and has no poles or roots on C.
		NOTE: Currently required that the function f(z) has only 
		simple roots in C
	df : function, optional
		Function of a single complex variable.
		The derivative of the function f(z).  If given then the 
		number of zeros within a contour will be computed as the 
		integral of df(z)/(2j*pi*f(z)) around the contour.
		If df is not given then the integral will instead be 
		computed using the diffrence in the argument of f(z) 
		continued around the contour.
	guessRoot : list, optional
		A list of suspected roots of the function f which lie 
		within the initial contour C.  Each element of the list 
		will be used as the initial point of an iterative 
		root-finding method so they need not be entirely 
		accurate.
	guessRootSymmetry : function, optional
		A function of a single complex variable, z, which returns 
		a list of all points which are expected to be roots of f, 
		given that z is a root of f.
	newtonStepTol : float, optional
		The iterative method used to give a final value for each
		root will exit if the step size, dx, between sucessive 
		iterations satisfied abs(dx) < newtonStepTol
	newtonMaxIter : int, optional
		The iterative method used to give a final value for each
		root will exit if the number of iterations exceeds newtonMaxIter
	rootErrTol : float, optional
		For a point, x, to be confirmed as a root abs(f(x)) < rootErrTol
	iterativeTries : int, optinal
		The number of times an iterative method with a random start point
		should be used to find the root within a contour containing a single
		root before the contour is subdivided again.
	integerTol : float, optional
		How close the result of the Romberg integration has to be to an 
		integer for it to be accepted (only used if df is given).  The 
		absolute tolerance of the Romberg integration will be integerTol/2.
	rombergDivMax : int, optional
		The maximum order of extrapolation of the Romberg integration routine 
		(only used if df is given)
	reqEqualZeros : int, optional
		If the Cauchy integral is computed by continuing the argument around the 
		contour (ie. if df is None) then the routine requires that the last 
		reqEqualZeros evaluations of the number of enclosed zeros are equal and 
		non-negative.  Default is 3.

	Yields
	------
	tuple
		All currently known roots of f(z) within the contour C
	tuple
		All the contours which still contain roots
	int
		Remaining number of roots to be found within the contour
	"""
	try:
		totNumberOfRoots = originalContour.enclosed_zeros(f,df,integerTol,rombergDivMax,reqEqualZeros)
	except (NonIntegerError, RuntimeError):
		raise RuntimeError("""Integration along the intial contour failed.  There is likely a root on or close to the initial contour
			If f and df have been given then try decreasing the integerTol or increasing rombergDivMax. 
			If only f has been provided then try increasing the reqEqualZeros.""")

	loggedIterativeWarning = False
	roots = []

	# check to see if the guesses we were passed are roots
	for root in guessRoot:
		addRoot(root, roots, originalContour, f, df, guessRootSymmetry, newtonStepTol, rootErrTol, newtonMaxIter)

	boxes = deque()
	boxes.append((originalContour,totNumberOfRoots))
	while len(roots) < totNumberOfRoots:
		box, numberOfEnclosedRoots = boxes.pop()

		# check we do not already have the correct number of known roots in this box
		knownRootsInBox = [root for root in roots if box.contains(root)]
		if len(knownRootsInBox) == numberOfEnclosedRoots:
			continue

		if numberOfEnclosedRoots > 1:
			# subdivide box further
			subdivide(boxes, box, numberOfEnclosedRoots, f, df, integerTol,rombergDivMax, reqEqualZeros)

		elif numberOfEnclosedRoots == 1:
			# try to find the root in the box
			for iteration in range(iterativeTries):
				x0 = box.randomPoint()
				root = iterateToRoot(x0, f, df, newtonStepTol, rootErrTol, newtonMaxIter)

				if root is not None:
					addRoot(root, roots, originalContour, f, df, guessRootSymmetry, newtonStepTol, rootErrTol, newtonMaxIter)

					if box.contains(root):
						break

			if root is None or not box.contains(root):
				# if the box is already very small then simply return the centerPoint coordinate of the box
				if box.area < newtonStepTol:
					root = box.centerPoint
					if not loggedIterativeWarning:
						logging.warning("""
							The Newton/secant method is failing to converge towards a root.  
							The center point of contours bounding an area < newtonStepTol and containing a single root will be added without confirmation that f < rootErrTol at these points.
							""")
						loggedIterativeWarning = True
					logging.info('The point %s will be treated as a root since it is the center point of a contour with area %s containing a single root'%(root, box.area))
					addRoot(root, roots, originalContour, f, df, guessRootSymmetry, newtonStepTol, rootErrTol, newtonMaxIter)

				else:
					# subdivide box again if we failed to find the root and the box is still too big
					subdivide(boxes, box, numberOfEnclosedRoots, f, df, integerTol, rombergDivMax, reqEqualZeros)

		yield tuple(roots), tuple(boxes), totNumberOfRoots - len(roots)

	if totNumberOfRoots == 0:
		yield [], deque(), 0

def findRoots(originalContour, f, df=None, **kwargs):
	"""
	Return a list of all roots of a given function f within a given originalContour.  
	Shares key word arguments with :func:`cxroots.RootFinder.findRootsGen`.
	"""
	rootFinder = findRootsGen(originalContour, f, df, **kwargs)
	for roots, boxes, numberOfRemainingRoots in rootFinder:
		pass
	return roots

def demo_findRoots(originalContour, f, df=None, automaticAnimation=False, returnAnim=False, **kwargs):
	"""
	An interactive demonstration of the processess used to find all the roots
	of a given function f within a given originalContour.
	Shares key word arguments with :func:`cxroots.RootFinder.findRootsGen`. 

	If automaticAnimation is False (default) then press the SPACE key 
	to step the animation forward.

	If automaticAnimation is True then the animation will play automatically
	until all the roots have been found.

	If returnAnim is true the animating object returned by matplotlib's animation.FuncAnimation
	will be returned, rather than the animation be shown.
	"""
	import matplotlib.pyplot as plt
	from matplotlib import animation
	rootFinder = findRootsGen(originalContour, f, df, **kwargs)

	originalContour.plot(linecolor='k', linestyle='--')

	fig = plt.gcf()
	ax = plt.gca()

	def update_frame(args):
		roots, boxes, numberOfRemainingRoots = args
		# print(args)

		plt.cla() # clear axis
		originalContour.plot(linecolor='k', linestyle='--')
		originalContour.sizePlot()
		for box, numberOfEnclosedRoots in boxes:
			if not hasattr(box, '_color'):
				cmap = plt.get_cmap('jet')
				box._color = cmap(np.random.random())
			
			plt.text(box.centerPoint.real, box.centerPoint.imag, numberOfEnclosedRoots)
			box.plot(linecolor=box._color)

		plt.scatter(np.real(roots), np.imag(roots))

		rootsLabel = ax.text(0.02, 0.95, 'Zeros remaining: %i'%numberOfRemainingRoots, transform=ax.transAxes)

		fig.canvas.draw()


	if returnAnim:
		return animation.FuncAnimation(fig, update_frame, frames=list(rootFinder), interval=500, repeat_delay=2000)

	elif automaticAnimation:
		ani = animation.FuncAnimation(fig, update_frame, frames=rootFinder, interval=500)

	else:
		def draw_next(event):
			if event.key == ' ':
				update_frame(next(rootFinder))

		fig.canvas.mpl_connect('key_press_event', draw_next)

	plt.show()

def showRoots(originalContour, f, df, **kwargs):
	"""
	Plots all roots of a given function f within a given originalContour.  
	Shares key word arguments with :func:`cxroots.RootFinder.findRootsGen`.
	"""
	import matplotlib.pyplot as plt
	originalContour.plot(linecolor='k', linestyle='--')
	roots = findRoots(originalContour, f, df, **kwargs)
	plt.scatter(np.real(roots), np.imag(roots), color='k', marker='x')
	plt.show()


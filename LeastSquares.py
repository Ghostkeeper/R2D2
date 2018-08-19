#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

class LeastSquares:
	"""
	Implementation of the least squares linear regression algorithm.

	This algorithm is used to fit a curve to data. This curve will be
	polynomial, even though the approximation algorithm is linear. This fitter
	will return a polynomial with the specified highest exponent. For instance,
	filling in `2` for the highest exponent will result in a quadratic
	polynomial of the form `Ax^2 + Bx + C`. The curve that is fit will be the
	one with the least squared error, summed for each training sample.

	This data can have any number of dimensions, but once the number of
	dimensions times the highest exponent starts to become big-ish (>2000),
	this training method will start to take very long to compute. The bulk of
	the computation time lies in inverting a matrix of `N` by `N`, where
	`N = len(predictors) * (highest_exponent + 1)`. This is a cubic operation.

	The Least Squares learner works by solving the following formula:

	`B = (X^T * X)^-1 * X^T * Y`

	Here X are the predictors, the variables that can be controlled for. Y are
	the responses, the variables that cannot be controlled for and must be
	computed. B is a vector of the polynomial multipliers (`A`, `B` and `C` in
	the quadratic formula above). The operation `^T` is matrix transpose. The
	operation `^-1` is matrix inverse. The operation `*` is matrix
	multiplication.
	"""

	def __init__(self, predictors, responses, highest_exponent=4):
		"""
		Create a Least Squares curve fitter.
		:param predictors: A two-dimensional table of the predictors.
		:param responses:
		:param highest_exponent:
		"""
		self._predictors = predictors
		self._responses = responses
		self._highest_exponent = highest_exponent

	def train(self):
		"""
		Fit a polynomial to the currently loaded data.
		:return: A list containing the multipliers of each exponent.
		"""
		#TODO.
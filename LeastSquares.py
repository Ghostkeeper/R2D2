#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

class LeastSquares:
	"""
	Implementation of the least squares linear regression algorithm.

	This algorithm is used to fit a curve to data. This curve will be
	polynomial, even though the approximation algorithm is linear.
	"""

	@staticmethod
	def train(predictors, responses, highest_exponent = 4):
		"""
		Fit a polynomial to the specified data.

		This data can have any number of dimensions, but once the number of
		dimensions times the highest exponent starts to exceed around ~2000,
		this training method is not very efficient any more.
		:param predictors: A two-dimensional table of the predictors. In the
		major coordinates are the individual measurements. In the minor
		coordinates are the dimensions of data, each field of the measurement.
		:param responses: A one-dimensional list of the responses for each of
		the measurements.
		:return: A list containing the multipliers of each exponent.
		"""
		#TODO.
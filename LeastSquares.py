#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

class LeastSquares:
	"""
	Implementation of the least squares linear regression algorithm.

	This algorithm is used to fit a curve to data. This curve will be
	polynomial, even though the approximation algorithm is linear.
	"""

	def train(self, data, highest_exponent = 4):
		"""
		Fit a polynomial to the specified data.

		This data can have any number of dimensions, but once the number of
		dimensions times the highest exponent starts to exceed around ~2000,
		this training method is not very efficient any more.
		:param data: A two-dimensional table. In the major coordinates are
		each dimension of the data (each field). In the minor coordinates are
		the individual measurements.
		:return: A list containing the multipliers of each exponent.
		"""
		#TODO.
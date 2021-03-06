#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

import numpy
import UM.Logger

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

		This also transforms the input data to Numpy arrays that the learner
		can use.
		:param predictors: A list of dictionaries of evaluations, one for each
		print.
		:param responses: A list of setting values, one for each print.
		:param highest_exponent: How complex of a polynomial should be fit to
		this data.
		"""
		#Have to translate the evaluations to a Numpy array.
		self._predictors = numpy.zeros((len(predictors), len(predictors[0])))
		all_keys = set()
		for prt in predictors:
			all_keys = all_keys.union(prt.keys())
		all_keys = list(sorted(all_keys))
		for print_index in range(len(predictors)):
			for key_index in range(len(all_keys)):
				if all_keys[key_index] in predictors[print_index]:
					self._predictors[print_index][key_index] = predictors[print_index][all_keys[key_index]]

		self._responses = numpy.array(responses)
		self._highest_exponent = highest_exponent

	def train(self):
		"""
		Fit a polynomial to the currently loaded data.
		:return: A list containing the multipliers of each exponent.
		"""
		all_responses = []
		for train_pred, train_resp, test_pred, test_resp in self._subdivide():
			coefficients, _, _, _ = numpy.linalg.lstsq(train_pred, train_resp, rcond=None)
			all_responses.append(coefficients)

			#TODO: Measure efficiacy using test set.

		#Create weighted average of all trainings.
		average = numpy.ndarray(all_responses[0].shape)
		for response in all_responses:
			average += response #TODO: Weight averages using efficiacy.
		average /= len(all_responses)

		return average

	def _subdivide(self, num_bags=5, ratio_train=0.8):
		"""
		Subdivide the training data into bags that we can train on separately.
		Each bag is selected randomly from the original sample set. There is
		no dependency between the bags. There may be overlap.
		:param num_bags: How many divisions to make.
		:param ratio_train: The fraction of the training data that must end up
		in the training set.
		:return: A sequence of tuples of four. The first entry is the
		predictors that are selected. The second entry is the responses that
		are selected. The third entry is the predictors that were not
		selected. The fourth entry is the responses that were not selected.
		"""
		num_samples = len(self._responses)
		train_samples = int(num_samples * ratio_train)
		test_samples = num_samples - train_samples
		if train_samples == 0 or test_samples == 0:
			UM.Logger.Logger.log("e", "Too few samples! Training samples: {train_samples}. Testing samples: {test_samples}.".format(train_samples=train_samples, test_samples=test_samples))
			return

		for bag in range(num_bags):
			permutation = numpy.random.permutation(num_samples)
			yield self._predictors[permutation[0:train_samples]], self._responses[permutation[0:train_samples]], self._predictors[permutation[train_samples:]], self._responses[permutation[train_samples:]]
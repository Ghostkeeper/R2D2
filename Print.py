#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper
#This plug-in is free software: you can distribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this library. If not, see <https://gnu.org/licenses/>.

import PyQt5.QtCore #This object's fields are accessible from QML.

class Print(PyQt5.QtCore.QObject):
	"""
	Represents a previously made print.
	"""

	def __init__(self, parent=None):
		"""
		Initialises the fields of this print.
		:param parent: The parent QObject.
		"""
		super().__init__(parent)

		self._name = "unknown"
		self._time_date = "0000-0-0/0:00:00"
		self._printer_type = "unknown"
		self._evaluated_extruder = 0
		self._model_hash = 0
		self._extruders = [] #For each extruder, a dictionary containing "nozzle", "material", and all settings for that extruder (including global settings).
		self._evaluation = {} #All known evaluation entries. Evaluation entries that are unknown are left out.

	def set_name(self, new_name):
		self._name = new_name

	@PyQt5.QtCore.pyqtProperty(str, fset=set_name)
	def name(self):
		"""
		The print job name.
		:return: The print job name.
		"""
		return self._name

	def set_time_date(self, new_time_date):
		self._time_date = new_time_date

	@PyQt5.QtCore.pyqtProperty(str, fset=set_time_date)
	def time_date(self):
		"""
		The time and date that the print was made at.
		:return: The time and date that the print was made at.
		"""
		return self._time_date

	def set_printer_type(self, new_printer_type):
		self._printer_type = new_printer_type

	@PyQt5.QtCore.pyqtProperty(str, fset=set_printer_type)
	def printer_type(self):
		"""
		The type of printer that was used (definition ID).
		:return: The type of printer that was used.
		"""
		return self._printer_type

	def set_model_hash(self, new_model_hash):
		self._model_hash = new_model_hash

	@PyQt5.QtCore.pyqtProperty(str, fset=set_model_hash)
	def model_hash(self):
		"""
		A hash of all models in the scene (after transformation).

		This way the print time can be minimised as long as we have multiple
		prints with exactly the same build plate.
		:return: A hash of all models in the scene.
		"""
		return self._model_hash

	def set_evaluated_extruder(self, new_evaluated_extruder):
		self._evaluated_extruder = new_evaluated_extruder

	@PyQt5.QtCore.pyqtProperty(int, fset=set_evaluated_extruder)
	def evaluated_extruder(self):
		"""
		The extruder that the evaluation is about.
		:return: An extruder.
		"""
		return self._evaluated_extruder

	def add_extruder(self, extruder_nr, new_extruder):
		while len(self._extruders) <= extruder_nr:
			self._extruders.append({})
		self._extruders[extruder_nr] = new_extruder

	@PyQt5.QtCore.pyqtSlot(int, result="QVariantMap")
	def extruder(self, extruder):
		"""
		Get the settings that were used for a particular extruder.

		This contains all settings, per-extruder or global. In addition, it
		contains two extra "settings": nozzle and material, indicating
		respectively which nozzle was used and which material was used.
		:param extruder: The extruder to get the settings of.
		:return: A dictionary containing all settings used for that extruder.
		"""
		return self._extruders[extruder]

	@PyQt5.QtCore.pyqtSlot("QVariantMap")
	def evaluation(self):
		"""
		The evaluation that was filled in for the print.
		:return: A dictionary containing the evaluation entries that were
		submitted for the print, if any.
		"""
		return self._evaluation
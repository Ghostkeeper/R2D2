#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

import datetime #To get the current time and date when creating a new print.
import json #To serialise this print to JSON.
import os.path #To find a place to save the print to file.
import PyQt5.QtCore #This object's fields are accessible from QML.
import UM.Resources #To save this print to file.

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
		self._time_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self._printer_type = "unknown"
		self._evaluated_extruder = 0
		self._model_hash = 0
		self._extruders = [] #For each extruder, a dictionary containing "nozzle", "material", and all settings for that extruder (including global settings).
		self._evaluation = {} #All known evaluation entries. Evaluation entries that are unknown are left out.

	@staticmethod
	def load(file_path):
		result = Print()
		with open(file_path) as f:
			json_document = json.load(f)
		#Careful not to use the setters for these because that will trigger a save, which might overwrite the file.
		result._name = json_document["name"]
		result._time_date = json_document["time_date"]
		result._printer_type = json_document["printer_type"]
		result._evaluated_extruder = json_document["evaluated_extruder"]
		result._model_hash = json_document["model_hash"]
		result._extruders = json_document["extruders"]
		result._evaluation = json_document["evaluation"]

		return result

	name_changed = PyQt5.QtCore.pyqtSignal()

	def set_name(self, new_name):
		"""
		Sets the print job name.
		:param new_name: The new print job name.
		"""
		old_file_path = self.file_path()
		self._name = new_name
		self.save()
		if os.path.exists(old_file_path):
			os.remove(old_file_path) #Changing the name causes the file name to change as well. We must move it.
		self.name_changed.emit()

	@PyQt5.QtCore.pyqtProperty(str, fset=set_name, notify=name_changed)
	def name(self):
		"""
		The print job name.
		:return: The print job name.
		"""
		return self._name

	time_date_changed = PyQt5.QtCore.pyqtSignal()

	def set_time_date(self, new_time_date):
		"""
		Sets the time and date that the print was made at.
		:param new_time_date: The new time and date to remember.
		"""
		old_file_path = self.file_path()
		self._time_date = new_time_date
		self.save()
		if os.path.exists(old_file_path):
			os.remove(old_file_path) #Changing the time and date causes the file name to change as well. We must move it.

	@PyQt5.QtCore.pyqtProperty(str, fset=set_time_date, notify=time_date_changed)
	def time_date(self):
		"""
		The time and date that the print was made at.
		:return: The time and date that the print was made at.
		"""
		return self._time_date

	def set_printer_type(self, new_printer_type):
		"""
		Sets the printer type that was used (definition ID).
		:param new_printer_type: The type of printer that was used.
		"""
		self._printer_type = new_printer_type
		self.save()

	@PyQt5.QtCore.pyqtProperty(str, fset=set_printer_type)
	def printer_type(self):
		"""
		The type of printer that was used (definition ID).
		:return: The type of printer that was used.
		"""
		return self._printer_type

	def set_model_hash(self, new_model_hash):
		"""
		Sets the hash of the scene.
		:param new_model_hash: The alleged hash of the scene that was printed.
		"""
		self._model_hash = new_model_hash
		self.save()

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
		"""
		Sets the extruder to evaluate.
		:param new_evaluated_extruder: The extruder to evaluate.
		"""
		self._evaluated_extruder = new_evaluated_extruder
		self.save()

	@PyQt5.QtCore.pyqtProperty(int, fset=set_evaluated_extruder)
	def evaluated_extruder(self):
		"""
		The extruder that the evaluation is about.
		:return: An extruder.
		"""
		return self._evaluated_extruder

	def add_extruder(self, extruder_nr, new_extruder):
		"""
		Adds an extruder to the print.
		:param extruder_nr: The position of this extruder.
		:param new_extruder: A dictionary containing all settings for that
		extruder in addition to "nozzle" and "material, specifying the nozzle
		and material type that were used for the print in that extruder.
		"""
		while len(self._extruders) <= extruder_nr:
			self._extruders.append({})
		self._extruders[extruder_nr] = new_extruder
		self.save()

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

	def evaluated_extruder_settings(self):
		"""
		Short-hand to get the settings that were used for the evaluated
		extruder.
		:return: A dictionary containing all settings used for the extruder
		that was evaluated.
		"""
		return self.extruder(self.evaluated_extruder())

	@PyQt5.QtCore.pyqtSlot("QVariantMap")
	def evaluation(self):
		"""
		The evaluation that was filled in for the print.
		:return: A dictionary containing the evaluation entries that were
		submitted for the print, if any.
		"""
		return self._evaluation

	def file_path(self):
		"""
		Generates the current file path if this were to be saved to disk.
		:return: The current file path of this print on disk.
		"""
		return os.path.join(UM.Resources.Resources.getDataStoragePath(), "print_evaluations", self._time_date + "_" + self._name + ".json")

	def save(self):
		"""
		Saves this print to disk.

		This needs to be called whenever the print is modified.
		"""
		json_document = {
			"name": self._name,
			"time_date": self._time_date,
			"printer_type": self._printer_type,
			"evaluated_extruder": self._evaluated_extruder,
			"model_hash": self._model_hash,
			"extruders": self._extruders,
			"evaluation": self._evaluation
		}

		file_path = self.file_path()
		with open(file_path, "w") as f:
			json.dump(json_document, f, indent="\t")
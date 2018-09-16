#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

import cura.CuraApplication #Various hooks into Cura.
import cura.Settings.ExtruderManager #To get the currently active extruder.
import cura.Settings.MachineManager #To get the currently active material and nozzle.
import os #To find the previously saved prints on the disk.
import PyQt5.QtCore
import UM.Qt.ListModel #To expose a list to QML.
import UM.Logger
import UM.Resources #To find previously saved prints in the data directory.

from . import LeastSquares #To train a polynomial model.
from . import Print

class Prints(UM.Qt.ListModel.ListModel):
	"""
	Displays a list of the prints that this system has previously made.
	"""

	PrintRole = PyQt5.QtCore.Qt.UserRole + 1

	inst = None

	def __init__(self, parent=None):
		"""
		Adds the role names to itself.
		"""
		super().__init__(parent)
		self.addRoleName(self.PrintRole, "print")

		self.prints = [] #A list of all prints.

		self._selected_print = None #The print that is currently selected.

		#Link some signals to update the view at appropriate times.
		application = cura.CuraApplication.CuraApplication.getInstance()
		application.globalContainerStackChanged.connect(self._update)
		application.getMachineManager().activeVariantChanged.connect(self._update)
		application.getMachineManager().activeMaterialChanged.connect(self._update)
		self._update()

		#Load all prints that were saved in previous sessions.
		store_directory = os.path.join(UM.Resources.Resources.getDataStoragePath(), "print_evaluations")
		if not os.path.exists(store_directory):
			os.mkdir(store_directory) #Create if it didn't exist yet.
		for file_name in os.listdir(os.path.join(UM.Resources.Resources.getDataStoragePath(), "print_evaluations")):
			file_path = os.path.join(store_directory, file_name)
			self.add_print(Print.Print.load(file_path))

	def add_print(self, print):
		"""
		Adds a print to the database and updates the model.
		:param print: The print to add to the database.
		"""
		self.prints.append(print)
		application = cura.CuraApplication.CuraApplication.getInstance()
		if application.getGlobalContainerStack().definition.getId() == print.printer_type: #Only need to update if the print would currently be displayed.
			active_extruder = cura.Settings.ExtruderManager.ExtruderManager.getInstance().getActiveExtruderStack()
			evaluated_extruder = print.extruder(print.evaluated_extruder)
			if active_extruder.variant.getId() == evaluated_extruder["nozzle"] and active_extruder.material.getId() == evaluated_extruder["material"]:
				self._update()

	@staticmethod
	def get_instance(*args, **kwargs):
		"""
		Get an instance of this class.

		This implements the singleton pattern.

		The function accepts parameters because it is called from PyQt as well
		but those parameters are ignored because we don't need the QML engine
		or anything like that.
		:return: An instance of this class.
		"""
		if Prints.inst is None:
			Prints.inst = Prints()
		return Prints.inst

	selected_print_changed = PyQt5.QtCore.pyqtSignal()

	def set_selected_print(self, selected_print):
		"""
		Changes the selection for the currently evaluating print.
		:param selected_print: The newly selected print.
		"""
		self._selected_print = selected_print
		self.selected_print_changed.emit()

	@PyQt5.QtCore.pyqtProperty(Print.Print, fset=set_selected_print, notify=selected_print_changed)
	def selected_print(self):
		"""
		Gets the print that is currently being evaluated.
		:return: The print that is currently being evaluated.
		"""
		return self._selected_print

	@PyQt5.QtCore.pyqtSlot()
	def train(self):
		"""
		Train a machine learner to be able to generate profiles from the
		user's intentions.
		"""
		if not self.prints:
			UM.Logger.Logger.log("e", "Can't train before there is any training data.")

		UM.Logger.Logger.log("i", "Starting training based on evaluation data.")

		#TODO: Implement an ensemble system here once we have more than one training method.

		#Train Least Squares individually per setting.
		for setting in sorted(self.prints[0].evaluated_extruder_settings()):
			uniques = set() #For enum and string settings, group all of them by uniques so that we can enumerate over them.
			for prt in self.prints:
				value = prt.evaluated_extruder_settings()[setting]
				if type(value) is str:
					uniques.add(value)
			uniques = list(sorted(uniques))
			all_values = [] #Responses.
			evaluations = [] #Predictors.
			for prt in self.prints:
				value = prt.evaluated_extruder_settings()[setting]
				if type(value) is bool:
					value = 1 if value else 0
					all_values.append(value)
					evaluations.append(prt.evaluation())
				if type(value) is str:
					#Create a hyperdimension for this setting with each option in a separate dimension.
					#The learner will rate each option with a real number and we'll choose the one with the highest rating.
					for option in uniques:
						all_values.append(1 if value == option else 0)
						evaluations.append(prt.evaluation())
				if type(value) is list:
					continue #Skip. We always fill in list settings as an empty list.
				else: #Numeric settings.
					all_values.append(value)
					evaluations.append(prt.evaluation())
			predictor = LeastSquares.LeastSquares(predictors=evaluations, responses=all_values)
			multipliers = predictor.train()

			#TODO: Store the function represented by these multipliers in some way until the profiles are generated.
			print(setting, ":=", multipliers) #DEBUG!

	def _update(self):
		"""
		Updates the list of prints exposed to QML.
		"""
		current_printer = cura.CuraApplication.CuraApplication.getInstance().getGlobalContainerStack().definition.getId()
		active_extruder = cura.Settings.ExtruderManager.ExtruderManager.getInstance().getActiveExtruderStack()
		current_nozzle = active_extruder.variant.getId()
		current_material = active_extruder.material.getId()
		items = []
		for prt in reversed(sorted(self.prints, key=lambda prnt: prnt.time_date)):
			extruder = prt.extruder(prt.evaluated_extruder)
			#Only show prints relevant to the current set-up.
			if current_printer == prt.printer_type and current_nozzle == extruder["nozzle"] and current_material == extruder["material"]:
				items.append({
					"print": prt
				})
		self.setItems(items)
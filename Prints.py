#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

import cura.CuraApplication #Various hooks into Cura.
import cura.Settings.ExtruderManager #To get the currently active extruder.
import cura.Settings.MachineManager #To get the currently active material and nozzle.
import PyQt5.QtCore
import UM.Qt.ListModel #To expose a list to QML.

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

	def set_selected_print(self, selected_print):
		"""
		Changes the selection for the currently evaluating print.
		:param selected_print: The newly selected print.
		"""
		self._selected_print = selected_print

	@PyQt5.QtCore.pyqtProperty(Print.Print, fset=set_selected_print)
	def selected_print(self):
		"""
		Gets the print that is currently being evaluated.
		:return: The print that is currently being evaluated.
		"""
		return self._selected_print

	def _update(self):
		"""
		Updates the list of prints exposed to QML.
		"""
		current_printer = cura.CuraApplication.CuraApplication.getInstance().getGlobalContainerStack().definition.getId()
		active_extruder = cura.Settings.ExtruderManager.ExtruderManager.getInstance().getActiveExtruderStack()
		current_nozzle = active_extruder.variant.getId()
		current_material = active_extruder.material.getId()
		items = []
		for prt in self.prints:
			extruder = prt.extruder(prt.evaluated_extruder)
			#Only show prints relevant to the current set-up.
			if current_printer == prt.printer_type and current_nozzle == extruder["nozzle"] and current_material == extruder["material"]:
				items.append({
					"print": prt
				})
		self.setItems(items)
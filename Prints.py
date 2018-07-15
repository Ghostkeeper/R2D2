#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper
#This plug-in is free software: you can distribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this library. If not, see <https://gnu.org/licenses/>.

import cura.CuraApplication #Various hooks into Cura.
import cura.Settings.ExtruderManager #To get the currently active extruder.
import cura.Settings.MachineManager #To get the currently active material and nozzle.
import PyQt5.QtCore
import UM.Qt.ListModel #To expose a list to QML.

class Prints(UM.Qt.ListModel.ListModel):
	"""
	Displays a list of the prints that this system has previously made.
	"""

	NameRole = PyQt5.QtCore.Qt.UserRole + 1
	TimeDateRole = PyQt5.QtCore.Qt.UserRole + 2

	inst = None

	def __init__(self, parent=None):
		"""
		Adds the role names to itself.
		"""
		super().__init__(parent)
		self.addRoleName(self.NameRole, "name")
		self.addRoleName(self.TimeDateRole, "time_date")

		self.prints = [] #A list of all prints.

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
	def get_instance():
		"""
		Get an instance of this class.

		This implements the singleton pattern.
		:return: An instance of this class.
		"""
		if Prints.inst is None:
			Prints.inst = Prints()
		return Prints.inst

	def _update(self):
		"""
		Updates the list of prints exposed to QML.
		"""
		current_printer = cura.CuraApplication.CuraApplication.getInstance().getGlobalContainerStack().definition.getId()
		active_extruder = cura.Settings.ExtruderManager.ExtruderManager.getInstance().getActiveExtruderStack()
		current_nozzle = active_extruder.variant.getId()
		current_material = active_extruder.material.getId()
		items = []
		for print in self.prints:
			extruder = print.extruder(print.evaluated_extruder)
			#Only show prints relevant to the current set-up.
			if current_printer == print.printer_type and current_nozzle == extruder["nozzle"] and current_material == extruder["material"]:
				items.append({
					"name": print.name,
					"time_date": print.time_date
				})
		self.setItems(items)
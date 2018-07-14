#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper
#This plug-in is free software: you can distribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this library. If not, see <https://gnu.org/licenses/>.

import PyQt5.QtCore
import UM.Qt.ListModel #To expose a list to QML.

class Prints(UM.Qt.ListModel.ListModel):
	"""
	Displays a list of the prints that this system has previously made.
	"""

	NameRole = PyQt5.QtCore.Qt.UserRole + 1
	TimeDateRole = PyQt5.QtCore.Qt.UserRole + 2

	def __init__(self, parent=None):
		"""
		Adds the role names to itself.
		"""
		super().__init__(parent)
		self.addRoleName(self.NameRole, "name")
		self.addRoleName(self.TimeDateRole, "time_date")

		self.prints = [] #A list of all prints.

		self.current_printer = ""
		self.current_nozzle = ""
		self.current_material = ""

	def add_print(self, print):
		"""
		Adds a print to the database and updates the model.
		:param print: The print to add to the database.
		"""
		self.prints.append(print)
		if self.current_printer == print.printer_type:
			extruder = print.extruder(print.evaluated_extruder)
			if self.current_nozzle == extruder["nozzle"] and self.current_material == extruder["material"]:
				self._update()

	def _update(self):
		pass #TODO
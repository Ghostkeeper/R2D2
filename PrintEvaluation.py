#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper
#This plug-in is free software: you can distribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this library. If not, see <https://gnu.org/licenses/>.

import cura.CuraApplication #Various hooks into Cura.
import cura.Settings.ExtruderManager #To get the currently active extruder.
import cura.Stages.CuraStage #We're implementing a Cura stage.
import os.path #To find the QML components.
import PyQt5.QtQml #To register QML components with the QML engine.
import UM.PluginRegistry #To find resources in the plug-in folder.
import UM.Scene.Iterator.DepthFirstIterator #To get the scene nodes for the scene hash.

from . import Print #To create a new entry in the prints database.
from . import Prints #To add prints to the database.

class PrintEvaluation(cura.Stages.CuraStage.CuraStage):
	"""
	A plug-in object that adds an additional stage to the top bar of Cura where
	the user can enter an evaluation of how good the print result is.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		application = cura.CuraApplication.CuraApplication.getInstance()
		application.engineCreatedSignal.connect(self._add_sidebar_panel)
		application.engineCreatedSignal.connect(self._register_qml_types)
		application.getOutputDeviceManager().writeStarted.connect(self.save_print)

	def save_print(self, output_device):
		"""
		Save the settings of a print persistently.

		This saves the print job name, time and date, the estimated print time
		and material usage, and all the settings used for every extruder. This
		doesn't save the per-object settings at the moment.
		:param output_device: The output device that was used to print the
		print. This is not used, since we only need the metadata of the print.
		"""
		this_print = Print.Print()

		application = cura.CuraApplication.CuraApplication.getInstance()
		print_info = application.getPrintInformation()
		this_print.set_name(print_info.jobName)
		this_print.set_printer_type(application.getGlobalContainerStack().definition.getId())
		this_print.evaluation()["duration"] = sum((int(d) for d in print_info.printTimes().values())) #We already fill this information in beforehand from the estimate that Cura gives.
		scene_hash = ""
		for node in UM.Scene.Iterator.DepthFirstIterator.DepthFirstIterator(application.getController().getScene().getRoot()):
			if node.getMeshData():
				scene_hash += node.getMeshData().getHash()
		this_print.set_model_hash(scene_hash)
		this_print.set_evaluated_extruder(cura.Settings.ExtruderManager.ExtruderManager.getInstance().activeExtruderIndex)
		for extruder_index in application.getGlobalContainerStack().extruders:
			extruder_train = application.getGlobalContainerStack().extruders[extruder_index]
			extruder_index = int(extruder_index)
			settings = {}
			for setting_key in extruder_train.getAllKeys():
				settings[setting_key] = extruder_train.getProperty(setting_key, "value")
			settings["nozzle"] = extruder_train.variant.getId()
			settings["material"] = extruder_train.material.getId()
			this_print.add_extruder(extruder_index, settings)
		Prints.Prints.get_instance().add_print(this_print)

	def _add_sidebar_panel(self):
		"""
		Registers the evaluation sidebar panel as a QML component.
		"""
		panel = os.path.join(UM.PluginRegistry.PluginRegistry.getInstance().getPluginPath("R2D2"), "EvaluationSidebar.qml")
		self.addDisplayComponent("sidebar", panel)

	def _register_qml_types(self):
		"""
		Registers QML objects that must be exposed to QML.
		"""
		PyQt5.QtQml.qmlRegisterSingletonType(Prints.Prints, "R2D2", 1, 0, "Prints", Prints.Prints.get_instance)
		PyQt5.QtQml.qmlRegisterType(Print.Print, "R2D2", 1, 0, "Print")
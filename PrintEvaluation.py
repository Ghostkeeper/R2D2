#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

import cura.CuraApplication #Various hooks into Cura.
import cura.Settings.ExtruderManager #To get the currently active extruder.
import cura.Stages.CuraStage #We're implementing a Cura stage.
import os.path #To find the QML components.
import PyQt5.QtQml #To register QML components with the QML engine.
import UM.PluginRegistry #To find resources in the plug-in folder.
import UM.Scene.Iterator.DepthFirstIterator #To get the scene nodes for the scene hash.
import UM.Settings.ContainerRegistry #To register the list of intents as setting definitions.
import UM.Settings.ContainerStack #To load the list of intents as settings.
import UM.Settings.DefinitionContainer #To load the list of intents as setting definitions.
import UM.Settings.InstanceContainer #To allow changing the intents.

from . import Print #To create a new entry in the prints database.
from . import Prints #To add prints to the database.

class PrintEvaluation(cura.Stages.CuraStage.CuraStage):
	"""
	A plug-in object that adds an additional stage to the top bar of Cura where
	the user can enter an evaluation of how good the print result is.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		self.intents_stack = None

		#Interoperatability with all the signals going 'round in this place.
		application = cura.CuraApplication.CuraApplication.getInstance()
		application.engineCreatedSignal.connect(self._add_sidebar_panel)
		application.engineCreatedSignal.connect(self._register_qml_types)
		application.getOutputDeviceManager().writeStarted.connect(self.save_print)
		application.initializationFinished.connect(self._register_container)

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
		this_print.evaluation()["print_time"] = sum((int(d) for d in print_info.printTimes().values())) #We already fill this information in beforehand from the estimate that Cura gives.
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

		#Make sure that the settings in the side bar are updated when switching prints.
		Prints.Prints.get_instance().selected_print_changed.connect(self._load_from_selected_print)

	def _load_from_selected_print(self):
		"""
		Called when the selected print changes.

		This copies the evaluation within the selected print into the setting
		stack with intents.
		"""
		prnt = Prints.Prints.get_instance().selected_print
		for intent in prnt.evaluation():
			self.intents_stack.getTop().setProperty(intent, "value", prnt.evaluation()[intent])

	def _on_evaluation_changed(self, key, property):
		"""
		Triggered when the user changes one of the evaluation entries.

		When this happens, we must update the evaluation in the currently
		active print entry.
		:param key: The entry that was changed.
		:param property: The property of the setting that was changed.
		Normally this can only be the "value" property.
		"""
		if property != "value":
			return
		prnt = Prints.Prints.get_instance().selected_print
		prnt.evaluation()[key] = self.intents_stack.getProperty(key, "value") #Update this new property in the current print.
		prnt.save()

	def _register_container(self):
		"""
		Adds a container to the container registry that defines all the
		possible intents and what the evaluation form can accept as values.
		"""
		registry = UM.Settings.ContainerRegistry.ContainerRegistry.getInstance()
		self.intents_stack = UM.Settings.ContainerStack.ContainerStack("intents_stack")
		self.intents_stack.setDirty(False)
		self.intents_stack.propertyChanged.connect(self._on_evaluation_changed)
		registry.addContainer(self.intents_stack)

		intents_container = UM.Settings.DefinitionContainer.DefinitionContainer("intents")
		with open(os.path.join(UM.PluginRegistry.PluginRegistry.getInstance().getPluginPath("R2D2"), "intents.def.json")) as f:
			intents_container_contents = f.read()
			intents_container.deserialize(intents_container_contents, "intents.def.json")
		registry.addContainer(intents_container)
		self.intents_stack.addContainer(intents_container)

		intents_changes = UM.Settings.InstanceContainer.InstanceContainer("intents_changes")
		intents_changes.setDefinition(intents_container.getId())
		intents_changes.setDirty(False)
		registry.addContainer(intents_changes)
		self.intents_stack.addContainer(intents_changes)

	def _register_qml_types(self):
		"""
		Registers QML objects that must be exposed to QML.
		"""
		PyQt5.QtQml.qmlRegisterSingletonType(Prints.Prints, "R2D2", 1, 0, "Prints", Prints.Prints.get_instance)
		PyQt5.QtQml.qmlRegisterType(Print.Print, "R2D2", 1, 0, "Print")
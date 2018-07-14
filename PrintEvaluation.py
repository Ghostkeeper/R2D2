#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper
#This plug-in is free software: you can distribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this library. If not, see <https://gnu.org/licenses/>.

import cura.Stages.CuraStage #We're implementing a Cura stage.
import os.path #To find the QML components.
import UM.PluginRegistry #To find resources in the plug-in folder.

class PrintEvaluation(cura.Stages.CuraStage.CuraStage):
	"""
	A plug-in object that adds an additional stage to the top bar of Cura where
	the user can enter an evaluation of how good the print result is.
	"""
	def __init__(self, parent = None):
		super().__init__(parent)

		UM.Application.Application.getInstance().engineCreatedSignal.connect(self._add_sidebar_panel)

	def _add_sidebar_panel(self):
		panel = os.path.join(UM.PluginRegistry.PluginRegistry.getInstance().getPluginPath("R2D2"), "EvaluationSidebar.qml")
		self.addDisplayComponent("sidebar", panel)
#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper
#This plug-in is free software: you can distribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this library. If not, see <https://gnu.org/licenses/>.

import UM.i18n

from . import PrintEvaluation #The plug-in object that implements the stage.

i18n_catalog = UM.i18n.i18nCatalog("r2d2")

def getMetaData():
	"""
	Gets the metadata of the plug-in.
	:return: A dictionary of metadata.
	"""
	return {
		"stage": {
			"name": i18n_catalog.i18nc("@item:inmenu", "Evaluation"),
			"weight": 2,
		}
	}

def register(app):
	"""
	Registers this plug-in with Uranium.
	:param app: The application instance to register to.
	:return: A dictionary of the types of plug-ins that this package implements
	and the plug-in objects belonging to each of them.
	"""
	return {
		"stage": PrintEvaluation.PrintEvaluation()
	}
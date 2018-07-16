#Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
#Copyright (C) 2018 Ghostkeeper

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
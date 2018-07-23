//Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
//Copyright (C) 2018 Ghostkeeper

import QtQuick 2.7
import QtQuick.Controls 1.4

import R2D2 1.0

Menu
{
	id: menu
	title: "Prints"

	Instantiator
	{
		model: Prints
		MenuItem
		{
			text: model.print.name
			checkable: true
			checked: Prints.selected_print == model.print
			exclusiveGroup: prints_group
			onTriggered: {
				Prints.selected_print = model.print;
			}
		}
		onObjectAdded: menu.insertItem(index, object)
		onObjectRemoved: menu.removeItem(object)
	}

	ExclusiveGroup {
		id: prints_group
	}
}
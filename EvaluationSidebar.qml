//Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
//Copyright (C) 2018 Ghostkeeper

import QtQuick 2.0
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import UM 1.2 as UM //For the theme.

Rectangle {
	id: base
	color: UM.Theme.getColor("sidebar")

	UM.I18nCatalog {
		id: catalog
		name: "r2d2"
	}

	//Print selection menu.
	ToolButton {
		anchors {
			left: parent.left
			right: parent.right
			top: parent.top
		}
		height: UM.Theme.getSize("sidebar_header").height
		style: ButtonStyle {
			background: Rectangle {
				color: {
					if(control.pressed) {
						return UM.Theme.getColor("sidebar_header_active");
					} else if(control.hovered) {
						return UM.Theme.getColor("sidebar_header_hover");
					} else {
						return UM.Theme.getColor("sidebar_header_bar");
					}
				}
				Behavior on color {
					ColorAnimation {
						duration: 50
					}
				}

				Label {
					id: print_selection
					color: UM.Theme.getColor("sidebar_header_text_active")
					text: catalog.i18nc("@label", "No print selected")
					elide: Text.ElideRight
					font: UM.Theme.getFont("medium_bold")
					anchors {
						left: parent.left
						leftMargin: UM.Theme.getSize("sidebar_margin").width
						verticalCenter: parent.verticalCenter
					}
				}

				UM.RecolorImage {
					id: down_arrow
					anchors {
						right: parent.right
						rightMargin: UM.Theme.getSize("default_margin").width
						verticalCenter: parent.verticalCenter
					}
					width: UM.Theme.getSize("standard_arrow").width
					height: UM.Theme.getSize("standard_arrow").height
					sourceSize.width: width
					sourceSize.height: height
					color: UM.Theme.getColor("text_emphasis")
					source: UM.Theme.getIcon("arrow_bottom")
				}
			}
		}
		menu: PrintsMenu {}
	}
}
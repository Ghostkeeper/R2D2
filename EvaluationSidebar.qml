//Plug-in to gather after-print feedback to tune your profiles, optimising for certain intent.
//Copyright (C) 2018 Ghostkeeper

import Cura 1.0 as Cura
import QtQuick 2.0
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import UM 1.2 as UM //For the theme.

import R2D2 1.0

Rectangle {
	id: base
	color: UM.Theme.getColor("sidebar")

	UM.I18nCatalog {
		id: catalog
		name: "r2d2"
	}

	//Print selection menu.
	ToolButton {
		id: print_selection
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
					color: UM.Theme.getColor("sidebar_header_text_active")
					text: Prints.selected_print ? Prints.selected_print.name : catalog.i18nc("@label", "No print selected")
					elide: Text.ElideRight
					font: UM.Theme.getFont("medium_bold")
					anchors {
						left: parent.left
						leftMargin: UM.Theme.getSize("sidebar_margin").width
						verticalCenter: parent.verticalCenter
					}
				}

				UM.RecolorImage {
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

	//The evaluation form.
	ScrollView {
		anchors {
			top: print_selection.bottom
			bottom: parent.bottom
			left: parent.left
			right: parent.right
		}
		visible: Prints.selected_print != null
		style: UM.Theme.styles.scrollview

		ListView {
			spacing: UM.Theme.getSize("default_lining").height
			model: UM.SettingDefinitionsModel {
				id: definitions_model
				containerId: "intents"
				showAll: true
			}
			delegate: Loader {
				id: setting_loader
				anchors {
					left: parent.left
					leftMargin: UM.Theme.getSize("sidebar_margin").width
					right: parent.right
					rightMargin: UM.Theme.getSize("sidebar_margin").width
				}
				height: {
					if(provider.properties.enabled === "True" && model.type != undefined) {
						return UM.Theme.getSize("section").height;
					} else {
						return 0;
					}
				}
				Behavior on height {
					NumberAnimation {
						duration: 100
					}
				}
				opacity: provider.properties.enabled == "True" ? 1 : 0
				Behavior on opacity {
					NumberAnimation {
						duration: 100
					}
				}
				enabled: opacity > 0
				property var definition: model
				property var settingDefinitionsModel: definitions_model
				property var propertyProvider: provider
				property var globalPropertyProvider: inherit_stack_provider
				asynchronous: model.type != "enum" && model.type != "extruder"

				onLoaded: {
					//Disable some of the normal buttons and features of the settings list.
					setting_loader.item.showRevertButton = false;
					setting_loader.item.showInheritButton = false;
					setting_loader.item.showLinkedSettingIcon = false;
					setting_loader.item.doDepthIndentation = false;
					setting_loader.item.doQualityUserSettingEmphasis = false;
				}

				sourceComponent: {
					switch(model.type) {
						case "int":
						case "float":
						case "str":
							return settingTextField;
						case "enum":
							return settingComboBox;
						case "bool":
							return settingCheckBox;
						case "category":
							return settingCategory;
						default:
							return settingUnknown;
					}
				}

				UM.SettingPropertyProvider {
					id: provider
					containerStackId: "intents_stack"
					key: model.key ? model.key : "None"
					watchedProperties: ["value", "enabled", "state", "validationState"]
					storeIndex: 0
				}
				UM.SettingPropertyProvider {
					id: inherit_stack_provider
					containerStackId: Cura.MachineManager.activeMachineId
					key: model.key ? model.key : "None"
					watchedProperties: ["limit_to_extruder"]
				}
			}
		}
	}

	Component {
		id: settingTextField
		Cura.SettingTextField {}
	}
	Component {
		id: settingComboBox
		Cura.SettingComboBox {}
	}
	Component {
		id: settingCheckBox
		Cura.SettingCheckBox {}
	}
	Component {
		id: settingCategory
		Cura.SettingCategory {}
	}
	Component {
		id: settingUnknown
		Cura.SettingUnknown {}
	}
}
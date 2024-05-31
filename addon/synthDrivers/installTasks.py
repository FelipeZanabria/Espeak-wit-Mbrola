# -*- coding: UTF-8 -*-
#Copyright (C) 2023 - 2024 Felipe Porciuncula Zanabria, released under the GPL.

import config, globalVars, os, shutil, addonHandler
# Code extracted from NVDA IBMTTS driver by David CM
def buildAddonAbsPath(addonName):
	return os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons", addonName))


def preserveFiles(addonName, folder):
	"""
	addonName: the unique identifier of the add-on
	folder: a path for a folder inside the addonName directory where the files must be preserved.
	"""
	print(os.path.dirname(__file__))
	absFolderPath = os.path.join(buildAddonAbsPath(addonName), folder)
	tempFolder = os.path.join(buildAddonAbsPath(addonName) + addonHandler.ADDON_PENDINGINSTALL_SUFFIX, folder)
	if os.path.isdir(absFolderPath):
		if os.path.isdir(tempFolder):
			shutil.rmtree(tempFolder)
		os.rename(absFolderPath, tempFolder)


def onInstall():
	preserveFiles("espeakWitMbrola", r"synthDrivers\espeak-data\mbrola")

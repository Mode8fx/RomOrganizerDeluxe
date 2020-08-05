import re
import xml.etree.ElementTree as ET
import zipfile
import numpy
import shutil
from pathlib import Path as plpath
from math import ceil
from tkinter import filedialog
from tkinter import *
from settings import *
from gatelib import makeChoice

# User settings
systemDirs = [d for d in listdir(romsetFolder) if path.isdir(path.join(romsetFolder, d))]
systemChoice = ""
systemName = ""
systemFolder = ""
xmdb = ""

biasPriority = ["World","USA","En","Europe","Australia","Canada","Japan","Ja","France","Fr","Germany","De","Spain","Es","Italy","It","Norway","Brazil","Sweden","China","Zh","Korea","Ko","Asia","Netherlands","Russia","Ru","Denmark","Nl","Pt","Sv","No","Da","Fi","Pl","Unknown"]
zoneBiasValues = {
	"World" : 0,
	"U" : 0,
	"USA" : 0,
	"En" : 1,
	"E" : 2,
	"Europe" : 2,
	"A" : 3,
	"Australia" : 3,
	"Ca" : 4,
	"Canada" : 4,
	"J" : 5,
	"Japan" : 5,
	"Ja" : 5,
	"F" : 6,
	"France" : 6,
	"Fr" : 6,
	"G" : 7,
	"Germany" : 7,
	"De" : 7,
	"S" : 8,
	"Spain" : 8,
	"Es" : 8,
	"I" : 9,
	"Italy" : 9,
	"It" : 9,
	"No" : 10,
	"Norway" : 10,
	"Br" : 11,
	"Brazil" : 11,
	"Sw" : 12,
	"Sweden" : 12,
	"Cn" : 13,
	"China" : 13,
	"Zh" : 13,
	"K" : 14,
	"Korea" : 14,
	"Ko" : 14,
	"As" : 15,
	"Asia" : 15,
	"Ne" : 16,
	"Netherlands" : 16,
	"Ru" : 17,
	"Russia" : 17,
	"Da" : 18,
	"Denmark" : 18,
	"Nl" : 19,
	"Pt" : 20,
	"Sv" : 21,
	"No" : 22,
	"Da" : 23,
	"Fi" : 24,
	"Pl" : 25
}

compilationArray = ["2 Games in 1 -", "2 Games in 1! -", "2 Disney Games -", "2 Great Games! -", "2 in 1 -", "2 in 1 Game Pack -", "2-in-1 Fun Pack -", "3 Games in 1 -", "4 Games on One Game Pak", "Double Game!", "Double Pack", "2 Jeux en 1", "Crash Superpack", "Spyro Superpack", "Crash & Spyro Superpack"]
classicNESArray = ["Classic NES Series", "Famicom Mini", "Hudson Best Collection"]

# -------------- #
# Main functions #
# -------------- #

def main():
	global systemChoice
	global systemName
	global deviceProfile
	global outputFolder
	global systemFolder
	global xmdb

	systemChoices = makeChoice("Choose romset(s):", systemDirs+["All"], True)
	if systemChoices is None:
		print("\nNo romsets found. Quitting.")
		sys.exit()
	if len(systemDirs)+1 in systemChoices:
		systemChoices = [range(1, len(systemChoices)+1)]
	for sc in systemChoices:
		systemChoice = systemDirs[sc-1]
		systemName = systemChoice.split("(")[0].strip()
		deviceProfiles = listdir(profilesFolder)
		dp = makeChoice("Which profile?", deviceProfiles)
		deviceProfile = path.join(profilesFolder, deviceProfiles[dp-1])
		print("Please select the ROM directory of your "+deviceProfiles[dp-1]+" (example: F:\\Roms).")
		root = Tk()
		root.withdraw()
		outputFolder = filedialog.askdirectory()
		romsetCategory = getRomsetCategory()
		if romsetCategory in ["Full", "1G1R"]:
			systemFolder = path.join(romsetFolder, systemChoice)
			for f in listdir(xmdbDir):
				if f.split("(")[0].strip() == systemName:
					xmdb = path.join(xmdbDir, f)
					break
			if xmdb == "":
				print("XMDB for current system not found.")
				print("Skipping current system.")
				continue
			fixNamesAndGenerateMergeDict()
			copyRomset(romsetCategory)
		otherCategory = getOtherCategory()
		# if otherCategory == "True":

def fixNamesAndGenerateMergeDict(verbose = False):
	global mergeDict
	global systemFolder

	mergedRoms = []
	mergedClones = []
	unmergedClones = []
	skipAll = False
	mergeDict = {}
	# contentsFile = path.join(textLogsFolder, "[Contents].txt")
	allFiles = [f for f in listdir(systemFolder) if path.isfile(path.join(systemFolder, f))]
	tree = ET.parse(xmdb)
	root = tree.getroot()
	numZoneds = len(root[0][1])
	step = (numZoneds // 20) + 1
	numCurrZoned = 0
	for currZoned in root[0][1]:
		allBiases = [bias.get("name") for bias in currZoned.findall("bias")]
		allZones = [bias.get("zone") for bias in currZoned.findall("bias")]
		allClones = [clone.get("name") for clone in currZoned.findall("clone")]
		allClonesLower = [clone.lower() for clone in allClones]
		for file in allFiles:
			# if the file exists, but the capitalization is wrong (example: "Sega" instead of "SEGA"), fix it
			fixedCap = False
			for i in range(len(allClones)):
				fileExt = path.splitext(file)[1]
				if file.lower() == allClonesLower[i] and file != allClones[i]+fileExt:
					currFilePath = path.join(systemFolder, file)
					newFilePath = path.join(systemFolder, allClones[i]+fileExt)
					print("Capitalization fix:")
					renameArchiveAndContent(currFilePath, newFilePath, allClones[i])
					fixedCap = True
					break
			# is breaking out here necessary/ideal?
			if fixedCap:
				break
		mergeRegionIndex, mergeName = getBestMergeName(allBiases, allZones)
		gameCurrLocation = getGameLocation(mergeName)
		if gameCurrLocation is not None:
			print("Attempting to resolve naming conflict for "+mergeName+"\n")
			mergeName = handleDuplicateName(mergeName, allClones, path.join(systemFolder, gameCurrLocation))
		allClonesList = list(dict.fromkeys(allClones))
		for currCloneName in allClonesList:
			currCloneNameWithExt = currCloneName+getFileExt(systemFolder, currCloneName)
			currCloneFile = path.join(systemFolder, currCloneNameWithExt)
			cloneExists = False
			if path.isfile(currCloneFile):
				cloneExists = True
			else:
				print("\nThe following ROM was not found:")
				print(currCloneName)
				print("\nAll clones for this game:")
				for c in allClonesList:
					print(c)
				recommendations = [f for f in allFiles if f.startswith(currCloneName.split("(")[0]+"(") and not path.splitext(f)[0] in mergedClones]
				if currCloneName+" [b].zip" in recommendations:
					print("Romset contains bad dump of this rom. Skipping.")
					currWrongName = "SKIP"
				else:
					cwn = guessOldName(recommendations, currCloneName)
					if cwn == 0:
						if skipAll:
							currWrongName = "SKIP"
						else:
							cwn = makeChoice("Which ROM in your romset matches the missing ROM? It will be renamed.", recommendations+["OTHER", "SKIP", "SKIP ALL"])
					if (not skipAll) or cwn > 0:
						if cwn == len(recommendations) + 1:
							print("Enter the exact name of this ROM file in your romset (with extension if the extension isn\'t ZIP), or type \"SKIP\" (no quotes) to skip this ROM.")
							currWrongName = input()
						elif cwn == len(recommendations) + 2:
							currWrongName = "SKIP"
						elif cwn == len(recommendations) + 3:
							currWrongName = "SKIP"
							skipAll = True
						else:
							currWrongName = recommendations[cwn-1]
						if (len(currWrongName) <= 4 or not "." in currWrongName[-4:]) and currWrongName != "SKIP":
							currWrongName = currWrongName + ".zip"
						currWrongClone = path.join(systemFolder, currWrongName)
				if currWrongName == "SKIP":
					print()
				elif path.isfile(currWrongClone):
					if zipfile.is_zipfile(currWrongClone):
						renameArchiveAndContent(currWrongClone, currCloneFile, currCloneName)
					else:
						rename(currWrongClone, path.splitext(currCloneFile)[0]+path.splitext(currWrongClone)[1])
					cloneExists = True
				else:
					print("\nInvalid name. Skipping.")
			if cloneExists:
				addGameFileLocationToDict((mergeName, mergeRegionIndex), currCloneNameWithExt)
				mergedRoms.append(currCloneNameWithExt)
				mergedClones.append(currCloneName)
			else:
				unmergedClones.append(currCloneName)
		if verbose:
			print("Scanned all versions of "+mergeName)
		numCurrZoned += 1
		if numCurrZoned % step == 0:
			print(str(round(numCurrZoned*100/numZoneds, 1))+"% - Scanned "+str(numCurrZoned)+" of "+str(numZoneds)+".")
	# print("\nDICTIONARY:\n")
	# print(mergeDict)
	print("Finished scanning romset.")

def getRomsetCategory():
	global systemName
	global deviceProfile

	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Romsets"):
				inCategory = True
			continue
		if lines[i].strip() == systemName:
			return lines[i+1].strip()
	return "None"

def getOtherCategory():
	global systemName
	global deviceProfile

	profile = open(deviceProfile,"r")
	lines = profile.readlines()
	inCategory = False
	for i in range(len(lines)):
		if not inCategory:
			if lines[i].startswith(": Other"):
				inCategory = True
			continue
		if lines[i].strip() == systemName:
			return lines[i+1].strip()
	return "False"

def copyRomset(romsetCategory):
	global systemName
	global systemFolder
	global mergeDict

	if romsetCategory not in ["Full", "1G1R"]:
		return
	numGames = len(mergeDict.keys())
	step = numGames // 20
	currGameNum = 0
	for gameNameAndRegionNum in mergeDict.keys():
		gameName, gameRegionNum = gameNameAndRegionNum
		currGame = mergeDict[gameNameAndRegionNum]
		bestRom = getBestRom(currGame)
		attributes = getAttributeSplit(bestRom)
		if gameName.startswith("[BIOS]"):
			gameRegion = "[BIOS]"
		elif "Test Program" in attributes:
			gameRegion = "[Test Program]"
		elif gameRegionNum == 0:
			gameRegion = "[USA]"
		elif gameRegionNum == 2:
			gameRegion = "[Europe]"
		elif gameRegionNum in [1,3,4]:
			gameRegion = "[Other (English)]"
		elif gameRegionNum == 5:
			gameRegion = "[Japan]"
		else:
			gameRegion = "[Other (non-English)]"
		unlicensedStr = "[Unlicensed]" if "Unl" in attributes else ""
		unreleasedStr = "[Unreleased]" if "Proto" in attributes else ""
		compilationStr = "[Compilation]" if (systemName == "Nintendo - Game Boy Advance" and any([gameName.startswith(comp) for comp in compilationArray])) else ""
		classicNESStr = "[NES & Famicom]" if (systemName == "Nintendo - Game Boy Advance" and any([gameName.startswith(nes) for nes in classicNESArray])) else ""
		gbaVideoStr = "[GBA Video]" if gameName.startswith("Game Boy Advance Video") else ""
		if romsetCategory == "Full":
			for rom in currGame:
				oldFile = path.join(systemFolder, rom)
				newDir = path.join(outputFolder, systemName, gameRegion, compilationStr, classicNESStr, gbaVideoStr, unlicensedStr, unreleasedStr, gameName)
				newFile = path.join(newDir, rom)
				if not path.isfile(newFile):
					createDir(newDir)
					shutil.copy(oldFile, newFile)
		else:
			oldFile = path.join(systemFolder, bestRom)
			newDir = path.join(outputFolder, systemName, gameRegion, compilationStr, classicNESStr, gbaVideoStr, unlicensedStr, unreleasedStr, gameName)
			newFile = path.join(newDir, bestRom)
			if not path.isfile(newFile):
				createDir(newDir)
				shutil.copy(oldFile, newFile)
		currGameNum += 1
		if currGameNum%step == 0:
			print(str(round(currGameNum*100.0/numGames, 1))+"% - Copied "+str(currGameNum)+" of "+str(numGames)+".")
	print("\nFinished copying romset.")

def getBestRom(clones):
	zoneValues = []
	cloneScores = []
	sortedClones = sorted(clones)
	for clone in sortedClones:
		attributes = getAttributeSplit(clone)[1:]
		revCheck = [a for a in attributes if len(a) >= 3]
		versionCheck = [a[0] for a in attributes]
		betaCheck = [a for a in attributes if len(a) >= 4]
		protoCheck = [a for a in attributes if len(a) >= 5]
		currZoneVal = 99
		for i in range(len(biasPriority)):
			if biasPriority[i] in attributes:
				currZoneVal = i
				break
		zoneValues.append(currZoneVal)
		currScore = 100
		if "Rev" in revCheck:
			currScore += 30
		if "v" in versionCheck:
			currScore += 30
		if "Beta" in betaCheck or "Proto" in protoCheck:
			currScore -= 50
		if "Virtual Console" in attributes or "GameCube" in attributes or "Collection" in attributes:
			currScore -= 10
		if "Sample" in attributes or "Demo" in attributes:
			currScore -= 90
		cloneScores.append(currScore)
	bestZones = numpy.where(zoneValues == numpy.min(zoneValues))[0].tolist()
	finalZone = 99
	bestScore = -500
	for zone in bestZones:
		currScore = cloneScores[zone]
		if currScore >= bestScore:
			bestScore = currScore
			finalZone = zone
	return sortedClones[finalZone]


# -------------- #
# Helper methods #
# -------------- #

def renameArchiveAndContent(currPath, newPath, newName):
	replaceArchive = False
	newFullFileName = ""
	fileExt = ""
	extractedFile = ""
	with zipfile.ZipFile(currPath, 'r', zipfile.ZIP_DEFLATED) as zippedClone:
		zippedFiles = zippedClone.namelist()
		if len(zippedFiles) > 1:
			print("\nThis archive contains more than one file. Skipping.")
		else:
			zippedClone.extract(zippedFiles[0], systemFolder)
			fileExt = path.splitext(zippedFiles[0])[1]
			extractedFile = path.join(systemFolder, zippedFiles[0])
			newFullFileName = path.splitext(newPath)[0]+fileExt
			rename(extractedFile, newFullFileName)
			replaceArchive = True
	if replaceArchive:
		remove(currPath)
		with zipfile.ZipFile(newPath, 'w', zipfile.ZIP_DEFLATED) as newZip:
			newZip.write(newFullFileName, arcname='\\'+newName+fileExt)
		remove(newFullFileName)
	print("Renamed "+path.splitext(path.basename(currPath))[0]+" to "+newName+"\n")

def getBestMergeName(biases, zones, indexOnly=False):
	zoneValues = []
	for zone in zones:
		currVal = zoneBiasValues.get(zone)
		if currVal is None:
			currVal = 99
		zoneValues.append(currVal)
	mergeIndex = numpy.min(zoneValues)
	if indexOnly:
		return mergeIndex, ""
	mergeName = biases[numpy.argmin(zoneValues)]
	mergeNameArray = getAttributeSplit(mergeName)
	regionIndex = 1
	for i in range(1, len(mergeNameArray)):
		if mergeNameArray[i] in biasPriority:
			# mergeName = "(".join(mergeNameArray[0:i]).strip()
			mergeName = mergeNameArray[0]
			for j in range(1,i):
				mergeName = mergeName + " (" + mergeNameArray[j] + ")"
			regionIndex = i+1
			break
	suffix = ""
	if len(mergeNameArray) > regionIndex:
		suffix = getSuffix(mergeNameArray[regionIndex:])
	mergeName = mergeName + suffix
	mergeName = mergeName.rstrip(".")
	return mergeIndex, mergeName

def getSuffix(attributes):
	skippedAttributes = ["Rev", "Beta", "Virtual Console", "Proto", "Unl", "v", "SGB Enhanced", "GB Compatible", "Demo", "Promo", "Sample", "GameCube", "Promotion Card"]
	for att in attributes:
		if att in biasPriority:
			continue
		skip = False
		for skippedAtt in skippedAttributes:
			if att.startswith(skippedAtt):
				skip = True
				break
		if skip:
			continue
		if "Collection" in att:
			continue
		if att.count("-") >= 2:
			continue
		return " ("+att+")"
	return ""

def addGameFileLocationToDict(key, game):
	global mergeDict

	if key not in mergeDict.keys():
		mergeDict[key] = []
	mergeDict[key].append(game)

def getGameLocation(game):
	global mergeDict

	for key in mergeDict.keys():
		if game in mergeDict[key]:
			return key[0]
	return None

def handleDuplicateName(mergeName, secondArchiveClones, mergeNameFirstLocation):
	mergeNameOnly = path.splitext(mergeName)[0]
	if "[BIOS]" in mergeName: # auto-merge BIOS files
		return mergeName
	firstArchiveClones = listdir(mergeNameFirstLocation)
	firstMatchingRegion = getMatchingRegion(firstArchiveClones)
	secondMatchingRegion = getMatchingRegion(secondArchiveClones)
	# rename first archive to region
	if firstMatchingRegion != "" and secondMatchingRegion == "":
		newName = mergeNameOnly+" ("+firstMatchingRegion+")"
		try:
			rename(mergeNameFirstLocation, path.join(mergedFolder, newName))
		except:
			pass
		return mergeName
	# rename second archive to region
	if firstMatchingRegion == "" and secondMatchingRegion != "":
		newName = mergeNameOnly+" ("+secondMatchingRegion+")"
		return newName
	# rename both archives to region
	if firstMatchingRegion != "" and secondMatchingRegion != "":
		newName1 = mergeNameOnly+" ("+firstMatchingRegion+")"
		try:
			rename(mergeNameFirstLocation, path.join(mergedFolder, newName1))
		except:
			pass
		newName2 = mergeNameOnly+" ("+secondMatchingRegion+")"
		return newName2
	# rename neither (merge)
	return mergeName

def getMatchingRegion(clones):
	try:
		matchingRegion = getAttributeSplit(clones[0])[1]
		for i in range(1, len(clones)):
			if matchingRegion != getAttributeSplit(clones[i])[1]:
				return ""
		return matchingRegion
	except:
		return ""

def getAttributeSplit(name):
	mna = [s.strip() for s in re.split('\(|\)', name) if s.strip() != ""]
	mergeNameArray = []
	mergeNameArray.append(mna[0])
	if len(mna) > 1:
		for i in range(1, len(mna)):
			if not ("," in mna[i] or "+" in mna[i]):
				mergeNameArray.append(mna[i])
			else:
				arrayWithComma = [s.strip() for s in re.split('\,|\+', mna[i]) if s.strip() != ""]
				for att2 in arrayWithComma:
					mergeNameArray.append(att2)
	return mergeNameArray

def guessOldName(recommendations, ccn):
	currCloneName = ccn.replace("&amp;", "&")
	array1 = ["(Rev A)", "(Rev B)", "(Rev C)", "(Rev D)", "(Rev E)", "(Beta A)", "(Beta B)", "(Beta C)", "(Beta D)", "(Beta E)", "(Proto A)", "(Proto B)", "(Proto C)", "(Proto D)", "(Proto E)", "(USA, Australia)", "(USA, Europe)"]
	array2 = ["(Rev 1)", "(Rev 2)", "(Rev 3)", "(Rev 4)", "(Rev 5)", "(Beta 1)", "(Beta 2)", "(Beta 3)", "(Beta 4)", "(Beta 5)", "(Proto 1)", "(Proto 2)", "(Proto 3)", "(Proto 4)", "(Proto 5)", "(USA)", "(USA)"]
	for i in range(len(recommendations)):
		currRec = path.splitext(recommendations[i])[0].replace("&amp;", "&")
		for j in range(len(array1)):
			elem1 = array1[j]
			elem2 = array2[j]
			if currRec.replace(elem1, elem2) == currCloneName or currRec.replace(elem2, elem1) == currCloneName:
				return i+1
	return 0

def getFileExt(folder, fileName):
	for f in listdir(folder):
		fName, fExt = path.splitext(f)
		if fName == fileName:
			return fExt
	return ""

def createDir(p):
	p1, p2 = path.split(p)
	if p2 == "":
		p = p1
	pathArray = []
	while True:
		p1, p2 = path.split(p)
		pathArray = [p2] + pathArray
		if p2 == "":
			pathArray = [p1] + pathArray
			break
		p = p1
	currPath = pathArray[0]
	for i in range(1, len(pathArray)):
		currPath = path.join(currPath, pathArray[i])
		if not path.isdir(currPath):
			mkdir(currPath)

if __name__ == '__main__':
	main()

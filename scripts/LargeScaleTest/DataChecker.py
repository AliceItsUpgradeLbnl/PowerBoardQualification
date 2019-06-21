#!/usr/bin/env python

from FileChecker import CheckBoardIdsFilesComplete

filename = "./ElectricalTests/PbIdList.txt"
file = open(filename, "r")
pbIds = file.readlines()
pbIds = [int(x.split("\n")[0]) for x in pbIds]
print CheckBoardIdsFilesComplete(pbIds)

#!/usr/bin/env python

import sqlite3 as lite
import PowerboardTestData as data

dbFile = "/home/its/Desktop/PB-production/PB_production/scripts/LargeScaleTest/TestData.db"

def fillDBFromFiles(filenames, directory):
	testInfo = data.TestInfo()
	testInfo.parseFilename(filenames[0])
	fillTestInfo(testInfo)

	thresholdScanFile = None
	voltageScanFile = None
	biasVoltageScanFile = None
	temperatureScanFile = None
	latchupTestFile = None
	preliminaryTestFile = None

	for filename in filenames:
		testName = filename.split("_")[6]
		if (testName == "ThresholdScan"):
			thresholdScanFile = filename
		elif (testName == "PowerVoltageScan"):
			voltageScanFile = filename
		elif (testName == "BiasVoltageScan"):
			biasVoltageScanFile = filename
		elif (testName == "TemperatureScan"):
			temperatureScanFile = filename
		elif (testName == "LatchupTest" or testName == "LachupTest"):
			latchupTestFile = filename
		elif (testName == "PreliminaryTest"):
			preliminaryTestFile = filename

	if thresholdScanFile:
		thresholdScan = data.ThresholdScan()
		thresholdScan.readFile(directory + thresholdScanFile)
		fillScan(thresholdScan, "ThresholdScan", testInfo.Id)

	if voltageScanFile:
		voltageScan = data.VoltageScan()
		voltageScan.readFile(directory + voltageScanFile)
		fillScan(voltageScan, "VoltageScan", testInfo.Id)

	if biasVoltageScanFile:
		biasVoltageScan = data.BiasVoltageScan()
		biasVoltageScan.readFile(directory + biasVoltageScanFile)
		fillScan(biasVoltageScan, "BiasVoltageScan", testInfo.Id)

	if temperatureScanFile:
		temperatureScan = data.TemperatureScan()
		temperatureScan.readFile(directory + temperatureScanFile)
		fillScan(temperatureScan, "TemperatureScan", testInfo.Id)

	if latchupTestFile:
		latchupTest = data.LatchupTest()
		latchupTest.readFile(directory + latchupTestFile)
		fillScan(latchupTest, "LatchupTest", testInfo.Id)

	if preliminaryTestFile:
		with open(directory + preliminaryTestFile, 'r') as file:
			result = file.read()
			fillPreliminaryTest(testInfo.Id, result)


def getTestId(boardNumber, testName):
	command = ""
	if (testName == "TestInfo"):
		command = "SELECT MAX(Id) FROM TestInfo WHERE BoardNumber=?"
	else:
		command = "SELECT MAX(TestInfo.Id) FROM TestInfo, " + testName + " WHERE TestInfo.BoardNumber=? AND TestInfo.Id=" + testName + ".Id"

	con = lite.connect(dbFile)
	with con:
		cur = con.cursor()
		cur.execute(command, (boardNumber,))
		return cur.fetchone()[0]


def getRows(testName, boardNumber, testId):
	rows = None

	if (testId == 0):
		testId = getTestId(boardNumber, testName)

	con = lite.connect(dbFile)
	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute("SELECT * FROM " + testName + "WHERE Id=?", (testId,))
		rows = cur.fetchall()

	return rows

def _buildInsert(row, testName, testId=0):
	columns = data.columns[testName]
	values = tuple([row[key] for key in columns])
	if testId:
		columns = ["Id"] + columns
		values = (testId,) + values
	command = "INSERT INTO " + testName + "(" + ",".join(columns) + ") VALUES(" + ",".join(["?" for i in range(len(columns))]) + ")"
	return (command, values)

def fillTestInfo(testInfo):
	con = lite.connect(dbFile)
	with con:
		cur = con.cursor()

		# increment the test number for the given board
		cur.execute("SELECT MAX(TestNumber) FROM TestInfo WHERE BoardNumber=?",(testInfo.Data["BoardNumber"],))
		# retrieve the highest test number for the given board
		testNumber = cur.fetchone()[0]
		# if this is the first time this board has been tested, set the test number to 0 so that it gets incremented to 1
		if testNumber == None:
			testNumber = 0
		testNumber += 1

		testInfo.Data["TestNumber"] = testNumber

		#insert the test info and retrieve the (newly created) test id
		cur.execute(*_buildInsert(testInfo.Data, "TestInfo"))
		testId = cur.lastrowid

		testInfo.Id = testId


def fillScan(scan, testName, testId):
	con = lite.connect(dbFile)
	with con:
		cur = con.cursor()
		for step in scan.Data:
			cur.execute(*_buildInsert(step, testName, testId))


def fillPreliminaryTest(testId, result):
	con = lite.connect(dbFile)
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO VisualAndSmoke(Id, Result) VALUES(?,?)", (testId, result))


def fillConfig(configId, text):
	con = lite.connect(dbFile)
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO Config(Id, Text) VALUES(?,?)", (configId, text))


def createDB():
	con = lite.connect(dbFile)

	with con:
		con.executescript("""
			CREATE TABLE IF NOT EXISTS Config(
				Id INTEGER,
				Text TEXT
			);
			CREATE TABLE IF NOT EXISTS TestInfo(
				Id INTEGER PRIMARY KEY,
				BoardNumber INTEGER,
				BoardVersion NUMERIC,
				TestNumber INTEGER,
				LoadType TEXT,
				PowerUnit TEXT,
				Config INTEGER,
				Tester TEXT,
				Timestamp TEXT
			);
			CREATE TABLE IF NOT EXISTS ThresholdScan(
				Id INTEGER,
				ChannelNumber INTEGER,
				ThDAC NUMERIC,
				VsetDAC NUMERIC,
				V NUMERIC,
				I NUMERIC,
				R NUMERIC,
				T NUMERIC,
				LUState TEXT
			);
			CREATE TABLE IF NOT EXISTS VoltageScan(
				Id INTEGER,
				ChannelNumber INTEGER,
				VsetDAC NUMERIC,
				V NUMERIC,
				Vrms NUMERIC,
				dV NUMERIC,
				I NUMERIC,
				Irms NUMERIC,
				dI NUMERIC,
				R NUMERIC,
				T NUMERIC,
				LUState TEXT
			);
			CREATE TABLE IF NOT EXISTS BiasVoltageScan(
				Id INTEGER,
				VsetDAC NUMERIC,
				V NUMERIC,
				Vrms NUMERIC,
				dV NUMERIC,
				I NUMERIC,
				Irms NUMERIC,
				dI NUMERIC,
				R NUMERIC,
				T NUMERIC
			);
			CREATE TABLE IF NOT EXISTS TemperatureScan(
				Id INTEGER,
				Vavg NUMERIC,
				Itot NUMERIC,
				T NUMERIC
			);
			CREATE TABLE IF NOT EXISTS LatchupTest(
				Id INTEGER,
				ChannelNumber INTEGER,
				BeforeEnabling INTEGER,
				AfterEnabling INTEGER,
				AfterLatching INTEGER
			);
			CREATE TABLE IF NOT EXISTS PreliminaryTest(
				Id INTEGER,
				Result TEXT
			);
			""")

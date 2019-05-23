import sqlite3 as lite

from dbconstants import STAGING_DB

createcommand = """
CREATE TABLE IF NOT EXISTS Activity(ActivityId INTEGER, ActivityName TEXT, Filename TEXT, Status TEXT);
CREATE TABLE IF NOT EXISTS ActivityComponent(ActivityId INTEGER, ComponentDbId INTEGER, ActCompTypeId INTEGER);
CREATE TABLE IF NOT EXISTS ActivityParameter(ActivityId INTEGER, ParameterId INTEGER);
CREATE TABLE IF NOT EXISTS ActivityAttachment(ActivityId INTEGER, Filename TEXT);
CREATE TABLE IF NOT EXISTS Component(ComponentTypeId INTEGER, ComponentId TEXT);
CREATE TABLE IF NOT EXISTS Composition(ParentId INTEGER, ChildId INTEGER);
"""

con = lite.connect(STAGING_DB)
with con:
    con.executescript(createcommand)
con.close()

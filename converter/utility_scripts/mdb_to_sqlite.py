#!/usr/bin/env python

# https://gist.github.com/mywarr/9908044
#
# mdb_to_sqlite.py <input mdb file> <output sqlite file>
#
# Depends upon the mdbtools suite:
#  http://sourceforge.net/projects/mdbtools/


# Python
import sys
import subprocess
import os
import os.path


def convertMdbToSqlite(i_mdbFilePath, i_sqliteFilePath, i_mdbToolsExeDirPath, i_sqliteExeFilePath):
    """
    Params:
     i_mdbFilePath:
      (str)
      Path of source Microsoft Access MDB file to convert from.
     i_sqliteFilePath:
      (str)
      Path of destination SQLite file to write to.
      If this file already exists, it will be overwritten.
     i_mdbToolsExeDirPath:
      Either (str)
       Directory that contains the mdbtools executables
      or (None)
       Assume they are on the system PATH.
     i_sqliteExeFilePath:
      Either (str)
       SQLite shell executable file
      or (None)
       Assume it is on the system PATH.
    """
    print("start of convertMdbToSqlite()")
    # If SQLite file already exists, delete it
    if os.path.exists(i_sqliteFilePath):
        os.remove(i_sqliteFilePath)

    #
    if i_mdbToolsExeDirPath == None:
        i_mdbToolsExeDirPath = ""
    else:
        if not i_mdbToolsExeDirPath.endswith(os.sep):
            i_mdbToolsExeDirPath += os.sep

    # Get SQL to create the schema
    schema = subprocess.Popen([i_mdbToolsExeDirPath + "mdb-schema", i_mdbFilePath, "sqlite"],
                              stdout=subprocess.PIPE).communicate()[0]
    #print(schema)
    sql = schema.decode("utf-8")

    # Get the list of table names
    tableNames = subprocess.Popen([i_mdbToolsExeDirPath + "mdb-tables", "-1", i_mdbFilePath],
                                   stdout=subprocess.PIPE).communicate()[0]
    tableNames = tableNames.splitlines()
    #print(tableNames)

    # Append SQL to begin a transaction
    sql += "\n"
    sql += "BEGIN;"

    # For each table,
    # append sqlite insert statements for the data
    allInserts = ""
    for tableName in tableNames:
        inserts = subprocess.Popen([i_mdbToolsExeDirPath + "mdb-export", "-I", "sqlite", i_mdbFilePath, tableName],
                                   stdout=subprocess.PIPE).communicate()[0]
        # Investigating Python text encoding
        # This picks Unicode 0x2018 '‘' out of CBM_PET.mdb conversion
        #print type(inserts)
        #if len(inserts) > 637736:
        #    print inserts[637720:637750]
        #    print inserts[637720:637750].decode("utf-8")
        sql += inserts.decode("utf-8")

    # Append SQL to commit the transaction
    sql += "\n"
    sql += "COMMIT;"

    # Run SQL in sqlite
    if i_sqliteExeFilePath == None:
        i_sqliteExeFilePath = "sqlite3"
    sqliteProcess = subprocess.Popen([i_sqliteExeFilePath, i_sqliteFilePath],
                                     stdin=subprocess.PIPE)

    sqliteProcess.communicate(sql.encode("utf-8"))
    print("end of convertMdbToSqlite()")


if __name__ == "__main__":
    # + Parse command line {{{

    COMMAND_NAME = "mdb_to_sqlite.py"

    def printUsage(i_outputStream):
        i_outputStream.write('''\
''' + COMMAND_NAME + ''', by Daniel Lopez, 03/05/2022
Microsoft Access to SQLite database converter

This script relies upon the mdbtools (http://sourceforge.net/projects/mdbtools/), and on sqlite.
The commands mdb-schema, mdb-tables, mdb-export and sqlite3 must be in your PATH.

Usage:
======
''' + COMMAND_NAME + ''' <MDB file> <SQLite file>

Params:
 MDB file:
   Path of source Microsoft Access MDB file to convert from.
 SQLite file:
   Path of destination SQLite file to write to.
   If this file already exists, it will be overwritten.

Options:
 --help
  Show this help.

 --mdbtools-exe-dir <directory path>
  Specify the directory that contains the mdbtools executables
  (mdb-schema, mdb-tables and mdb-export, which may have an ".exe" extension on Windows),
  if they are not already in your PATH.
 --sqlite3-exe <file path>
  Specify the SQLite shell executable file (sqlite3/sqlite3.exe),
  if it is not already in your PATH.
''')

    # Parameters, with their default values
    param_mdbFilePath = None
    param_sqliteFilePath = None
    param_mdbToolsExeDirPath = None
    param_sqliteExeFilePath = None

    # For each argument
    import sys
    argNo = 1
    while argNo < len(sys.argv):
        arg = sys.argv[argNo]
        argNo += 1

        # If it's an option
        if arg[0] == "-":
            if arg == "--help":
                printUsage(sys.stdout)
                sys.exit(0)

            elif arg == "--mdbtools-exe-dir":
                argNo += 1
                if argNo >= len(sys.argv):
                    print("ERROR: --mdbtools-exe-dir requires a value")
                    print("(Run with --help to show command usage.)")
                    sys.exit(0)

                param_mdbToolsExeDirPath = sys.argv[argNo]

            elif arg == "--sqlite3-exe":
                argNo += 1
                if argNo >= len(sys.argv):
                    print("ERROR: --sqlite3-exe requires a value")
                    print("(Run with --help to show command usage.)")
                    sys.exit(0)

                param_sqliteExeFilePath = sys.argv[argNo]

            else:
                print("ERROR: Unrecognised option: " + arg)
                print("(Run with --help to show command usage.)")
                sys.exit(-1)

        # Else if it's an argument
        else:
            if param_mdbFilePath == None:
                param_mdbFilePath = arg
            elif param_sqliteFilePath == None:
                param_sqliteFilePath = arg
            else:
                print("ERROR: Too many arguments.")
                print("(Run with --help to show command usage.)")
                sys.exit(-1)

    if param_sqliteFilePath == None:
        print("ERROR: Insufficient arguments.")
        print("(Run with --help to show command usage.)")
        sys.exit(-1)

    # + }}}

    convertMdbToSqlite(param_mdbFilePath, param_sqliteFilePath, param_mdbToolsExeDirPath, param_sqliteExeFilePath)
    print("end")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import shlex
import sqlite3


# + Quoting for different shells {{{

# + + Single argument {{{

import shlex
if hasattr(shlex, "quote"):
    quoteArgumentForBash = shlex.quote  # since Python 3.3
else:
    import pipes
    quoteArgumentForBash = pipes.quote  # before Python 3.3

def quoteArgumentForWindowsCmd(i_arg):
    return i_arg.replace("^", "^^") \
                .replace("(", "^(") \
                .replace(")", "^)") \
                .replace("%", "^%") \
                .replace("!", "^!") \
                .replace('"', '^"') \
                .replace('<', "^<") \
                .replace('>', "^>") \
                .replace('&', "^&") \
                .replace(" ", '" "')

import platform
if platform.system() == "Windows":
    quoteArgumentForNativeShell = quoteArgumentForWindowsCmd
else:
    quoteArgumentForNativeShell = quoteArgumentForBash

# + + }}}

# + }}}


def convertMdbToSqlite(i_mdbFilePath, i_sqliteFilePath, i_mdbToolsExeDirPath):
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
       Directory that contains the mdbtools executables.
      or (None)
       Assume they are on the system PATH.
    """
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
    commandAndArgs = [i_mdbToolsExeDirPath + "mdb-schema", i_mdbFilePath, "sqlite"]
    print("# " + " ".join(quoteArgumentForNativeShell(arg)  for arg in commandAndArgs))
    sys.stdout.flush()
    schema = subprocess.Popen(commandAndArgs, stdout=subprocess.PIPE).communicate()[0]
    #print(schema)
    sql = schema.decode("utf-8")

    # Get the list of table names
    commandAndArgs = [i_mdbToolsExeDirPath + "mdb-tables", "-1", i_mdbFilePath]
    print("# " + " ".join(quoteArgumentForNativeShell(arg)  for arg in commandAndArgs))
    sys.stdout.flush()
    tableNames = subprocess.Popen(commandAndArgs, stdout=subprocess.PIPE).communicate()[0]
    tableNames = tableNames.splitlines()
    #print(tableNames)

    # Append SQL to begin a transaction
    sql += "\n"
    sql += "BEGIN;"

    # For each table,
    # append sqlite insert statements for the data
    allInserts = ""
    for tableName in tableNames:
        commandAndArgs = [i_mdbToolsExeDirPath + "mdb-export", "-I", "sqlite", i_mdbFilePath, tableName.decode()]
        print("# " + " ".join(quoteArgumentForNativeShell(arg)  for arg in commandAndArgs))
        sys.stdout.flush()
        inserts = subprocess.Popen(commandAndArgs, stdout=subprocess.PIPE).communicate()[0]
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

    #print(sql)

    # Run SQL in sqlite
    print("Creating SQLite database...")
    sys.stdout.flush()
    db = sqlite3.connect("file:" + i_sqliteFilePath + "?mode=rwc", uri=True)
    db.executescript(sql)
    db.close()
    print("Done.")
    sys.stdout.flush()


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
 --mdbtools-exe-dir <directory path>
  Specify the directory that contains the mdbtools executables
  (mdb-schema, mdb-tables and mdb-export, which may have an ".exe" extension on Windows),
  if they are not already in your PATH.

 --help
  Show this help.
''')

    # Parameters, with their default values
    param_mdbFilePath = None
    param_sqliteFilePath = None
    param_mdbToolsExeDirPath = None

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
                if argNo >= len(sys.argv):
                    print("ERROR: --mdbtools-exe-dir requires a value")
                    print("(Run with --help to show command usage.)")
                    sys.exit(0)

                param_mdbToolsExeDirPath = sys.argv[argNo]
                argNo += 1

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

    convertMdbToSqlite(param_mdbFilePath, param_sqliteFilePath, param_mdbToolsExeDirPath)

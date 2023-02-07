
# Python std
import sys
import sqlite3
import copy
import os.path
import re
import collections

# This program
import qt_extras
import columns
import sql


def sqliteRowToDict(i_row):
    """
    Convert a sqlite3.Row object to a plain dict for easier viewing.

    Params:
     i_row:
      (sqlite3.Row)

    Returns:
     (dict)
    """
    return { keyName: i_row[keyName]  for keyName in i_row.keys() }

def sqliteRegexFunction(i_pattern, i_value):
    #print("sqliteRegexFunction(" + i_value + ", " + i_pattern + ")")
    #c_pattern = re.compile(r"\b" + i_pattern.lower() + r"\b")
    compiledPattern = re.compile(i_pattern)
    return compiledPattern.search(str(i_value)) is not None

g_containerDbs = []
# (list of ContainerDb)

# Type: ContainerDb
#  (dict)
#  Dictionary has specific key-value properties:
#   connection:
#    (sqlite3.Connection)
#    Connection to a temporary database, to which actually used databases are attached
#   maxAttachedDatabases:
#    (int)
#   attachedDatabases:
#    (dict)
#    Dictionary has:
#     Keys:
#      (str)
#      Schema name
#      ie. the alias specified in the ATTACH command
#     Values:
#      (AttachedDbInfo)

# Type: AttachedDbInfo
#  (dict)
#  Dictionary has specific key-value properties:
#   dbFilePath:
#    (str)
#   schema:
#    (dict)
#   fulfillableColumnIds:
#    (set of str)

def openContainerDb():
    """
    Returns:
     (ContainerDb)
    """
    # Open a new temporary database to contain some attached databases
    # and append it to the g_containerDbs list
    global g_containerDbs
    g_containerDbs.append({
        "connection": sqlite3.connect(""),
        "attachedDatabases": {}
    })
    # Add REGEXP function
    g_containerDbs[-1]["connection"].create_function("REGEXP", 2, sqliteRegexFunction)

    # Lookup maximum possible number of attached databases
    compileOptions = [record[0]  for record in g_containerDbs[-1]["connection"].execute("PRAGMA compile_options").fetchall()]
    for compileOption in compileOptions:
        if compileOption.startswith("MAX_ATTACHED="):
            g_containerDbs[-1]["maxAttachedDatabases"] = int(compileOption.split("=")[1])
    #g_containerDbs[-1]["maxAttachedDatabases"] = 2  # for testing

    #
    return g_containerDbs[-1]

def getNonFullContainerDb():
    """
    Returns:
     (ContainerDb)
    """
    # If no container DBs are open,
    # open one and return it
    if len(g_containerDbs) == 0:
        return openContainerDb()

    # Iterate existing container DBs and if find one with space for another attachment,
    # return it
    for containerDb in g_containerDbs:
        if len(containerDb["attachedDatabases"]) < containerDb["maxAttachedDatabases"]:
            return containerDb

    # Else if no free space in existing container DBs,
    # open another one and return it
    return openContainerDb()

def sanitizeSchemaName(i_name):
    """
    Params:
     i_name:
      (str)

    Returns:
     (str)
    """
    sanitized = ""

    # Normalize slashes and take stem name
    i_name = i_name.replace("\\", "/")
    i_name = os.path.splitext(os.path.basename(i_name))[0]

    # Replace awkward characters with underscores
    for char in i_name:
        if not ((char.upper() >= "A" and char.upper() <= "Z") or (char >= "0" and char <= "9") or char == "_"):
            char = "_"
        sanitized += char

    # If it starts with a numeric digit,
    # prepend an underscore
    if sanitized[0] >= "0" and sanitized[0] <= "9":
        sanitized = "_" + sanitized

    # If not unique,
    # append numeric suffix
    existingSchemaNames = []
    for containerDb in g_containerDbs:
        existingSchemaNames.extend(list(containerDb["attachedDatabases"].keys()))
    rv = sanitized
    nextNo = 2
    while rv in existingSchemaNames:
        rv = sanitized + "_" + str(nextNo)

    #
    return rv

def openDb(i_schemaName, i_dbFilePath):
    """
    Attach a new database.

    Params:
     i_schemaName:
      (str)
     i_dbFilePath:
      (str)
    """
    if not os.path.isfile(i_dbFilePath):
        raise RuntimeError("file doesn't exist")

    dbInfo = {
        "dbFilePath": i_dbFilePath
    }

    # Get a non-full container database and attach new database to it
    containerDb = getNonFullContainerDb()
    cursor = containerDb["connection"].execute("ATTACH DATABASE '" + i_dbFilePath.replace("'", "''") + "' AS " + i_schemaName)

    try:
        # Get names of tables
        cursor = containerDb["connection"].execute("SELECT name FROM " + i_schemaName + ".sqlite_master WHERE type = 'table'")
        rows = cursor.fetchall()
        dbTableNames = [row[0]  for row in rows]

        # Get info about tables
        dbInfo["schema"] = {}
        containerDb["connection"].row_factory = sqlite3.Row
        for tableName in ["Games", "Years", "Genres", "PGenres", "Publishers", "Developers", "Programmers", "Languages", "Crackers", "Artists", "Licenses", "Rarities", "Musicians"]:
            if tableName in dbTableNames:
                cursor = containerDb["connection"].execute("PRAGMA " + i_schemaName + ".table_info(" + tableName + ")")
                rows = cursor.fetchall()
                rows = [sqliteRowToDict(row)  for row in rows]
                dbInfo["schema"][tableName] = rows

        # Note which table column specs can be realized from this database
        fulfillableColumnIds = set()
        def validateTableColumnSpec(i_dbSchema, i_dbTableNames, i_tableColumnSpec):
            rv = True
            if "dbTableNames" in i_tableColumnSpec:
                for dbTableName in i_tableColumnSpec["dbTableNames"]:
                    if not (dbTableName in i_dbTableNames):
                        rv = False
            if "dbColumnNames" in i_tableColumnSpec:
                for dbColumnName in i_tableColumnSpec["dbColumnNames"]:
                    tableName, columnName = dbColumnName.split(".")
                    if not (tableName in i_dbSchema.keys()):
                        rv = False
                    else:
                        columnNames = [row["name"]  for row in i_dbSchema[tableName]]
                        if not (columnName in columnNames):
                            rv = False
            #if rv == False:
            #    print("Schema: "  + i_schemaName + ", missing column: " + i_tableColumnSpec["id"])
            return rv
        for tableColumnSpec in columns.g_tableColumnSpecs:
            if validateTableColumnSpec(dbInfo["schema"], dbTableNames, tableColumnSpec):
                fulfillableColumnIds.add(tableColumnSpec["id"])
        dbInfo["fulfillableColumnIds"] = fulfillableColumnIds

        ## Only use the columns that the database actually has
        #columns.filterColumnsByDb(dbTableNames, dbInfo["schema"])

        #
        containerDb["attachedDatabases"][i_schemaName] = dbInfo

    except:
        containerDb["connection"].execute("DETACH DATABASE " + i_schemaName)

    ##
    #print("DBs:")
    #for containerDbNo, containerDb in enumerate(g_containerDbs):
    #    print(" " + str(containerDbNo))
    #    for schemaName in containerDb["attachedDatabases"].keys():
    #        print("  " + schemaName)

def closeDb(i_schemaName):
    """
    Params:
     i_schemaName:
      (str)
    """
    for containerDb in g_containerDbs:
        if i_schemaName in containerDb["attachedDatabases"]:
            cursor = containerDb["connection"].execute("DETACH DATABASE " + i_schemaName)
            del(containerDb["attachedDatabases"][i_schemaName])
            break

def getAttachDatabaseStatements():
    """
    Returns:
     (list of list of str)
    """
    containerDbs = []

    for containerDb in g_containerDbs:
        attachDatabaseStatements = []
        for schemaName, attachedDbInfo in containerDb["attachedDatabases"].items():
            attachDatabaseStatements.append("ATTACH DATABASE '" + attachedDbInfo["dbFilePath"].replace("'", "''") + "' AS " + schemaName)
        containerDbs.append(attachDatabaseStatements)

    return containerDbs

def getContainerDbForSchemaName(i_schemaName):
    """
    Params:
     i_schemaName:
      (str)

    Returns:
     Either (ContainerDb)
     or (None)
    """
    for containerDb in g_containerDbs:
        if i_schemaName in containerDb["attachedDatabases"]:
            return containerDb
    return None

def getDbInfoForSchemaName(i_schemaName):
    """
    Params:
     i_schemaName:
      (str)

    Returns:
     Either (DbInfo)
     or (None)
    """
    containerDb = getContainerDbForSchemaName(i_schemaName)
    if containerDb != None:
        return containerDb["attachedDatabases"][i_schemaName]
    else:
        return None

def tableColumnSpecToTableNamesAndSelectTerms(i_tableColumnSpec, i_schemaName):
    """
    Given a table column spec,
    get the (real or placeholder) SELECT and FROM (table name) terms to use in an SQL statement to get information for that column from a given database.

    Params:
     i_tableColumnSpec:
      (columns.TableColumnSpec)
     i_schemaName:
      (str)

    Returns:
     (tuple)
     Tuple has elements:
      0:
       (list)
       Table names
      1:
       (list)
       SQL SELECT terms
    """
    # Find DB info
    dbInfo = getDbInfoForSchemaName(i_schemaName)

    #
    dbTableNames = collections.OrderedDict()
    dbSelectTerms = collections.OrderedDict()
    if i_tableColumnSpec["id"] in dbInfo["fulfillableColumnIds"]:
        if "dbTableNames" in i_tableColumnSpec:
            for dbTableName in i_tableColumnSpec["dbTableNames"]:
                dbTableNames[dbTableName] = True
        if "dbSelect" in i_tableColumnSpec:
            dbSelectTerms[i_tableColumnSpec["dbSelect"]] = True
    else:
        if "dbSelectPlaceholder" in i_tableColumnSpec:
            dbSelectTerms[i_tableColumnSpec["dbSelectPlaceholder"]] = True

    return list(dbTableNames.keys()), list(dbSelectTerms.keys())


# + Gamebase-specified schema {{{

def getJoinTermsToTable(i_tableName, io_tableConnections):
    """
    Params:
     i_tableName:
      (str)
     io_tableConnections:
      (dict)
      Mapping of table names to join clauses and dependencies
      eg.
       {
           "PGenres": {
               "dependencies": ["Genres"],
               "fromTerm": "LEFT JOIN PGenres ON Genres.PG_Id = PGenres.PG_Id"
           },
           "Genres": {
               "dependencies": [],
               "fromTerm": "LEFT JOIN Genres ON Games.GE_Id = Genres.GE_Id"
           },
       }

    Returns:
     Function return value:
      (list of str)
     io_tableConnections:
      The used connections will be removed from the list.
    """
    rv = []

    if i_tableName in io_tableConnections:
        tableConnection = io_tableConnections[i_tableName]
        for dependency in tableConnection["dependencies"]:
            rv += getJoinTermsToTable(dependency, io_tableConnections)
        rv.append(tableConnection["fromTerm"])
        del(io_tableConnections[i_tableName])

    return rv

connectionsFromGamesTable = {
    "Years": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Years ON Games.YE_Id = Years.YE_Id"
    },
    "Genres": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Genres ON Games.GE_Id = Genres.GE_Id"
    },
    "PGenres": {
        "dependencies": ["Genres"],
        "fromTerm": "LEFT JOIN <schema name>.PGenres ON Genres.PG_Id = PGenres.PG_Id"
    },
    "Publishers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Publishers ON Games.PU_Id = Publishers.PU_Id"
    },
    "Developers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Developers ON Games.DE_Id = Developers.DE_Id"
    },
    "Programmers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Programmers ON Games.PR_Id = Programmers.PR_Id"
    },
    "Languages": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Languages ON Games.LA_Id = Languages.LA_Id"
    },
    "Crackers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Crackers ON Games.CR_Id = Crackers.CR_Id"
    },
    "Artists": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Artists ON Games.AR_Id = Artists.AR_Id"
    },
    "Licenses": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Licenses ON Games.LI_Id = Licenses.LI_Id"
    },
    "Rarities": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Rarities ON Games.RA_Id = Rarities.RA_Id"
    },
    "Musicians": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Musicians ON Games.MU_Id = Musicians.MU_Id"
    },
}

# + }}}

# + Run queries {{{

#def getGameList_getSql(i_tableColumnSpecIds, i_whereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns=True):
#    """
#    Params:
#     i_tableColumnSpecIds:
#      (list of str)
#     i_whereExpression:
#      (str)
#     i_sortOperations:
#      (list)
#      See ColumnNameBar.sort_operations
#     i_whereExpressionMightUseNonVisibleColumns:
#      (bool)
#
#    Returns:
#     Either (list)
#      Each element is:
#       (tuple)
#       Tuple has elements:
#        0:
#         (sqlite3.Connection)
#        1:
#         (str)
#     or raise exception (SqlParseError)
#      args[0]:
#       (str)
#       Description of error.
#    """
#    attachedDbCount = sum([len(containerDb["attachedDatabases"])  for containerDb in g_containerDbs])
#    if attachedDbCount == 0:
#        return []
#
#    connectionsAndSqlTexts = []
#
#    for containerDb in g_containerDbs:
#
#        sqlTexts = []
#
#        # For each attached database in this container
#        for schemaName in list(containerDb["attachedDatabases"].keys()):
#            #print(schemaName)
#
#            # Start with fields/tables that are always selected
#            selectTerms = [
#                "'" + schemaName + "' AS \"SchemaName\"",
#                "Games.GA_Id AS [Games.GA_Id]"
#            ]
#            fromTerms = [
#                schemaName + ".Games"
#            ]
#
#            # + Determine what extra fields to select {{{
#
#            neededTableNames = collections.OrderedDict()
#            neededSelectTerms = collections.OrderedDict()
#
#            #  For all visible table columns,
#            #  collect FROM and SELECT terms
#            for tableColumnSpecId in i_tableColumnSpecIds:
#                tableColumnSpec = columns.tableColumnSpec_getById(tableColumnSpecId)
#                newNeededTableNames, newNeededSelectTerms = tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, schemaName)
#                for newNeededTableName in newNeededTableNames:
#                    neededTableNames[newNeededTableName] = True
#                for newNeededSelectTerm in newNeededSelectTerms:
#                    neededSelectTerms[newNeededSelectTerm] = True
#
#            #  If needed, parse WHERE expression for column names and add those too
#            if i_whereExpressionMightUseNonVisibleColumns:
#                #columnIdentifiers = sql.sqlWhereExpressionToColumnIdentifiers(i_whereExpression)
#                #for columnIdentifier in columnIdentifiers:
#                #    tableColumnSpec = columns.tableColumnSpec_getByDbIdentifier(columnIdentifier)
#                #    newNeededTableNames, newNeededSelectTerms = tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, schemaName)
#                #    neededTableNames |= newNeededTableNames
#                #    neededSelectTerms |= newNeededSelectTerms
#                try:
#                    normalizedWhereExpression, newNeededTableNames, newNeededSelectTerms = sql.normalizeSqlWhereExpressionToTableNamesAndSelectTerms(i_whereExpression, schemaName)
#                    if normalizedWhereExpression != None:
#                        i_whereExpression = normalizedWhereExpression
#                        for newNeededTableName in newNeededTableNames:
#                            neededTableNames[newNeededTableName] = True
#                        for newNeededSelectTerm in newNeededSelectTerms:
#                            neededSelectTerms[newNeededSelectTerm] = True
#                except sql.SqlParseError as e:
#                    raise
#
#            # Get terms as lists instead of OrderedDict
#            neededTableNames = list(neededTableNames.keys())
#            neededSelectTerms = list(neededSelectTerms.keys())
#
#            # + }}}
#
#            # Add the extra selectTerms and fromTerms
#            for neededSelectTerm in neededSelectTerms:
#                if neededSelectTerm == "Games.GA_Id" or neededSelectTerm == "GA_Id":
#                    continue
#                selectTerms.append(neededSelectTerm)
#            tableConnections = copy.deepcopy(connectionsFromGamesTable)
#            for neededTableName in neededTableNames:
#                fromTerms += [fromTerm.replace("<schema name>", schemaName)  for fromTerm in getJoinTermsToTable(neededTableName, tableConnections)]
#
#            # Concatenate terms to actual SELECT and FROM clauses
#            selectAndFromSql = "SELECT " + ", ".join(selectTerms) + "\nFROM " + " ".join(fromTerms)
#            sqlTexts.append(selectAndFromSql)
#
#        #for sqlText in sqlTexts:
#        #    print(sqlText)
#
#        # WHERE
#        i_whereExpression = i_whereExpression.strip()
#        if i_whereExpression != "":
#            sqlTexts = [sqlText + "\nWHERE " + i_whereExpression  for sqlText in sqlTexts]
#            #sqlText += "\nWHERE " + i_whereExpression
#
#        sqlText = "\nUNION ALL\n".join(sqlTexts)
#
#        # ORDER BY
#        if len(i_sortOperations) > 0:
#            sqlText += "\nORDER BY "
#
#            orderByTerms = []
#            for columnId, direction in i_sortOperations:
#                tableColumnSpec = columns.tableColumnSpec_getById(columnId)
#                term = '"' + tableColumnSpec["dbIdentifiers"][0] + '"'
#                term += " COLLATE NOCASE"
#                if direction == -1:
#                    term += " DESC"
#                orderByTerms.append(term)
#            sqlText += ", ".join(orderByTerms)
#
#        connectionsAndSqlTexts.append((containerDb["connection"], sqlText))
#
#    #
#    return connectionsAndSqlTexts


def getGameList_getContainerDbSelectAndFromTerms(i_containerDb, i_tableColumnSpecIds, i_whereExpression, i_whereExpressionMightUseNonVisibleColumns=True):
    """
    Params:
     i_containerDb:
      (ContainerDb)
     i_tableColumnSpecIds:
      (list of str)
     i_whereExpression:
      (str)
     i_whereExpressionMightUseNonVisibleColumns:
      (bool)

    Returns:
     Either (tuple)
      Tuple has elements:
       0:
        (list)
       1:
        (str)
        Normalized i_whereExpression
     or raise exception (SqlParseError)
      args[0]:
       (str)
       Description of error.
    """
    attachedDbsSelectAndFromTerms = []

    # For each attached database in the container
    for schemaName in list(i_containerDb["attachedDatabases"].keys()):
        #print(schemaName)

        # Start with fields/tables that are always selected
        selectTerms = [
            "'" + schemaName + "' AS \"SchemaName\"",
            "Games.GA_Id AS [Games.GA_Id]"
        ]
        fromTerms = [
            schemaName + ".Games"
        ]

        # + Determine what extra fields to select {{{

        neededTableNames = collections.OrderedDict()
        neededSelectTerms = collections.OrderedDict()

        #  For all visible table columns,
        #  collect FROM and SELECT terms
        for tableColumnSpecId in i_tableColumnSpecIds:
            tableColumnSpec = columns.tableColumnSpec_getById(tableColumnSpecId)
            newNeededTableNames, newNeededSelectTerms = tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, schemaName)
            for newNeededTableName in newNeededTableNames:
                neededTableNames[newNeededTableName] = True
            for newNeededSelectTerm in newNeededSelectTerms:
                neededSelectTerms[newNeededSelectTerm] = True

        #  If needed, parse WHERE expression for column names and add those too
        if i_whereExpressionMightUseNonVisibleColumns:
            #columnIdentifiers = sql.sqlWhereExpressionToColumnIdentifiers(i_whereExpression)
            #for columnIdentifier in columnIdentifiers:
            #    tableColumnSpec = columns.tableColumnSpec_getByDbIdentifier(columnIdentifier)
            #    newNeededTableNames, newNeededSelectTerms = tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, schemaName)
            #    neededTableNames |= newNeededTableNames
            #    neededSelectTerms |= newNeededSelectTerms
            try:
                normalizedWhereExpression, newNeededTableNames, newNeededSelectTerms = sql.normalizeSqlWhereExpressionToTableNamesAndSelectTerms(i_whereExpression, schemaName)
                if normalizedWhereExpression != None:
                    i_whereExpression = normalizedWhereExpression
                    for newNeededTableName in newNeededTableNames:
                        neededTableNames[newNeededTableName] = True
                    for newNeededSelectTerm in newNeededSelectTerms:
                        neededSelectTerms[newNeededSelectTerm] = True
            except sql.SqlParseError as e:
                raise

        # Get terms as lists instead of OrderedDict
        neededTableNames = list(neededTableNames.keys())
        neededSelectTerms = list(neededSelectTerms.keys())

        # + }}}

        # Add the extra selectTerms and fromTerms
        for neededSelectTerm in neededSelectTerms:
            if neededSelectTerm == "Games.GA_Id" or neededSelectTerm == "GA_Id":
                continue
            selectTerms.append(neededSelectTerm)
        tableConnections = copy.deepcopy(connectionsFromGamesTable)
        for neededTableName in neededTableNames:
            fromTerms += [fromTerm.replace("<schema name>", schemaName)  for fromTerm in getJoinTermsToTable(neededTableName, tableConnections)]

        # Append selectTerms and fromTerms to return array
        attachedDbsSelectAndFromTerms.append({
            "selectTerms": selectTerms,
            "fromTerms": fromTerms
        })

    return (attachedDbsSelectAndFromTerms, i_whereExpression.strip())

def getGameList_getSql(i_tableColumnSpecIds, i_whereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns=True):
    """
    Params:
     i_tableColumnSpecIds:
      (list of str)
     i_whereExpression:
      (str)
     i_sortOperations:
      (list)
      See ColumnNameBar.sort_operations
     i_whereExpressionMightUseNonVisibleColumns:
      (bool)

    Returns:
     Either (list)
      Each element is:
       (tuple)
       Tuple has elements:
        0:
         (sqlite3.Connection)
        1:
         (str)
     or raise exception (SqlParseError)
      args[0]:
       (str)
       Description of error.
    """
    attachedDbCount = sum([len(containerDb["attachedDatabases"])  for containerDb in g_containerDbs])
    if attachedDbCount == 0:
        return []

    connectionsAndSqlTexts = []

    # For each container
    for containerDb in g_containerDbs:
        # For each attached db,
        # get SELECT and FROM terms, while normalizing WHERE expression
        attachedDbsSelectAndFromTerms, i_whereExpression = getGameList_getContainerDbSelectAndFromTerms(containerDb, i_tableColumnSpecIds, i_whereExpression, i_whereExpressionMightUseNonVisibleColumns)

        # For each attached db,
        # concatenate SELECT and FROM terms into the beginnings of actual SQL statements
        attachedDbsSqlTexts = []
        for attachedDbSelectAndFromTerms in attachedDbsSelectAndFromTerms:
            selectAndFromSql = "SELECT " + ", ".join(attachedDbSelectAndFromTerms["selectTerms"]) + "\nFROM " + " ".join(attachedDbSelectAndFromTerms["fromTerms"])
            attachedDbsSqlTexts.append(selectAndFromSql)

        # For each attached db,
        # append WHERE clause
        if i_whereExpression != "":
            attachedDbsSqlTexts = [sqlText + "\nWHERE " + i_whereExpression  for sqlText in attachedDbsSqlTexts]
            #sqlText += "\nWHERE " + i_whereExpression

        # Concatenate all attached db SQL statements so far with "UNION ALL"
        sqlText = "\nUNION ALL\n".join(attachedDbsSqlTexts)

        # Append ORDER BY clause
        if len(i_sortOperations) > 0:
            sqlText += "\nORDER BY "

            orderByTerms = []
            for columnId, direction in i_sortOperations:
                tableColumnSpec = columns.tableColumnSpec_getById(columnId)
                term = '"' + tableColumnSpec["dbIdentifiers"][0] + '"'
                term += " COLLATE NOCASE"
                if direction == -1:
                    term += " DESC"
                orderByTerms.append(term)
            sqlText += ", ".join(orderByTerms)

        connectionsAndSqlTexts.append((containerDb["connection"], sqlText))

    #
    return connectionsAndSqlTexts

def getGameList_executeSql(i_connectionsAndSqlTexts):
    """
    Params:
     i_connectionsAndSqlTexts:
      (list)
      As returned from getGameList_getSql().

    Returns:
     (list of sqlite3.Cursor)
    """
    rv = []
    for connectionAndSqlText in i_connectionsAndSqlTexts:
        rv.append(connectionAndSqlText[0].execute(connectionAndSqlText[1]))
    return rv

def getGameList_executeSqlAndFetchAll(i_connectionsAndSqlTexts, i_sortOperations):
    """
    Params:
     i_connectionsAndSqlTexts:
      (list)
      As returned from getGameList_getSql().
     i_sortOperations:
      (list)
      See ColumnNameBar.sort_operations

    Returns:
     (tuple)
     Tuple has elements:
      0:
       (list of str)
       Column names
      1:
       (list)
       Records
    """
    cursors = getGameList_executeSql(i_connectionsAndSqlTexts)

    columnNames = [column[0]  for column in cursors[0].description]

    sortedRecords = []
    if len(cursors) == 1:
        sortedRecords.extend(cursors[0].fetchall())
    elif len(cursors) > 1:
        # If no sorting,
        # just concatenate all result sets
        if len(i_sortOperations) == 0:
            for cursor in cursors:
                sortedRecords.extend(cursor.fetchall())
        # Else if want sorting,
        # re-sort
        else:
            for cursor in cursors:
                sortedRecords.extend(cursor.fetchall())

            # Convert sort operation column IDs to column numbers
            sortColumnNosAndDirections = []
            for columnId, direction in i_sortOperations:
                tableColumnSpec = columns.tableColumnSpec_getById(columnId)
                term = tableColumnSpec["dbIdentifiers"][0]
                sortColumnNosAndDirections.append((columnNames.index(term), direction))

            #
            sortColumnNosAndDirections.reverse()
            for sortColumnNo, sortDirection in sortColumnNosAndDirections:
                def keyFunc(i_record):
                    value = i_record[sortColumnNo]
                    if isinstance(value, str):
                        return value.upper()
                    else:
                        return value
                sortedRecords.sort(key=keyFunc, reverse=(sortDirection == -1))

    #
    return columnNames, sortedRecords

def getGameRecord(i_schemaName, i_gameId, i_includeRelatedGameNames=False):
    """
    Params:
     i_schemaName:
      (str)
     i_gameId:
      (int)
     i_includeRelatedGameNames:
      (bool)

    Returns:
     (dict)
    """
    containerDb = getContainerDbForSchemaName(i_schemaName)
    dbInfo = containerDb["attachedDatabases"][i_schemaName]

    # From Games table, select all fields
    fromTerms = [
        i_schemaName + ".Games"
    ]

    selectTerms = [
        "'" + i_schemaName + "' AS \"SchemaName\""
    ]
    fullyQualifiedFieldNames = True
    if fullyQualifiedFieldNames:
        for field in dbInfo["schema"]["Games"]:
            selectTerms.append("Games." + field["name"] + " AS [Games." + field["name"] + "]")
    else:
        selectTerms.append("Games.*")

    #
    if i_includeRelatedGameNames:
        gamesColumnNames = [row["name"]  for row in dbInfo["schema"]["Games"]]
        if "CloneOf" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS CloneOf_Games ON Games.CloneOf = CloneOf_Games.GA_Id")
            selectTerms.append("CloneOf_Games.Name AS [Games.CloneOf_Name]")
        if "Prequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS Prequel_Games ON Games.Prequel = Prequel_Games.GA_Id")
            selectTerms.append("Prequel_Games.Name AS [Games.Prequel_Name]")
        if "Sequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS Sequel_Games ON Games.Sequel = Sequel_Games.GA_Id")
            selectTerms.append("Sequel_Games.Name AS [Games.Sequel_Name]")
        if "Related" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS Related_Games ON Games.Related = Related_Games.GA_Id")
            selectTerms.append("Related_Games.Name AS [Games.Related_Name]")

    # For all other tables connected to Games
    # that are present in this database
    tableConnections = copy.deepcopy(connectionsFromGamesTable)
    tableNames = [tableName  for tableName in tableConnections.keys()  if tableName in dbInfo["schema"].keys()]
    for tableName in tableNames:
        # Join to it
        fromTerms += [fromTerm.replace("<schema name>", i_schemaName)  for fromTerm in getJoinTermsToTable(tableName, tableConnections)]
        # Select all fields from it
        if fullyQualifiedFieldNames:
            for field in dbInfo["schema"][tableName]:
                selectTerms.append(tableName + "." + field["name"] + " AS [" + tableName + "." + field["name"] + "]")
        else:
            selectTerms.append(tableName + ".*")

    # Build SQL string
    #  SELECT
    sql = "SELECT " + ", ".join(selectTerms)
    #  FROM
    sql += "\nFROM " + " ".join(fromTerms)
    #  WHERE
    sql += "\nWHERE Games.GA_Id = " + str(i_gameId)

    # Execute
    containerDb["connection"].row_factory = sqlite3.Row
    #print(sql)
    cursor = containerDb["connection"].execute(sql)

    row = cursor.fetchone()
    row = sqliteRowToDict(row)
    return row

def getExtrasRecords(i_schemaName, i_gameId):
    """
    Params:
     i_schemaName:
      (str)
     i_gameId:
      (int)

    Returns:
     (dict)
    """
    # Build SQL string
    sql = "SELECT '" + i_schemaName + "' AS \"SchemaName\", * FROM " + i_schemaName + ".Extras"
    sql += "\nWHERE GA_Id = " + str(i_gameId)
    sql += "\nORDER BY DisplayOrder"

    # Execute
    containerDb = getContainerDbForSchemaName(i_schemaName)
    containerDb["connection"].row_factory = sqlite3.Row
    cursor = containerDb["connection"].execute(sql)

    rows = cursor.fetchall()
    rows = [sqliteRowToDict(row)  for row in rows]
    return rows

# + }}}

import collections
class DbRecordDict(collections.UserDict):
    """
    A dictionary intended to hold keys which are fully qualified '<table name>.<column name>' names,
    and overrides __getitem__ so that you can get items by either that full name or just '<column name>'.
    """
    def __getitem__(self, i_key):
        # Try matching the key name as given
        if i_key in self.data:
            return self.data[i_key]

        # Try matching just the last name component
        for realKey, value in self.data.items():
            if realKey.rsplit(".", 1)[-1] == i_key:
                return value

        # Raise KeyError
        return self.data[i_key]

    def __contains__(self, i_key):
        # Try matching the key name as given
        if i_key in self.data:
            return True

        # Try matching just the last name component
        for realKey in self.data.keys():
            if realKey.rsplit(".", 1)[-1] == i_key:
                return True

        #
        return False

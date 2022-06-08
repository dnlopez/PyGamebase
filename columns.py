
# + Usable {{{

# g_usableColumns:
#  (list)
#  Each element is:
#   (dict)
#   Dict has specific key-value properties:
#    id:
#     (str)
#     A unique internal identifier for the column.
#    screenName:
#     The text that will appear in the heading for this column and in column selection menus.
#    dbColumnNames:
#     (list of str)
#     Fully-qualified (ie. "<table name>.<column name>") names of columns that all must exist in the database
#     for this to be a usable column.
#    dbTableNames:
#     (list of str)
#     Names of tables that all must exist in the database for this to be a usable column,
#     and which will be joined to when doing a database query to get the information for this column.
#    dbSelect:
#     (str)
#     The term to add to the SELECT clause to get the data for this column.
#     It should end with an "AS ..." alias for predictable referencing in filters and so on.
#     For a simple column select (as opposed to an expression) use "AS [<table name>.<column name>]".
#    dbIdentifiers:
#     (list of str)
#     Identifiers which can be used to refer to this column in the WHERE clause.
#     The first of these should be the fully qualified (for a simple column select) or otherwise chosen (for an expression)
#     name given after "AS" in 'dbSelect'.
#     Further identifiers may be shorter, still valid alternatives, eg. "<column name>" alone.
#     These alternatives will consequently be recognised if used in an expression on the  SQL filter bar.
#    defaultWidth:
#     (int)
#     Initial width for the column in pixels.
#    sortable:
#     (bool)
#     True: Give the column a visible heading which can be clicked to sort by it.
#    filterable:
#     (bool)
#     True: Give the column a filter box under its heading.
#    textAlignment:
#     (str)
#     How to align text in the column.
#     One of
#      "left"
#      "center"
#    dbType:
#     (str)
#     As exported from a GameBase 64 MDB file. Not currently used by this program.
#    comment:
#     (str)
#     As exported from a GameBase 64 MDB file. Not currently used by this program.

g_usableColumns = [
    {
        "id": "detail",
        "screenName": "Show detail (+)",
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
    },
    {
        "id": "play",
        "screenName": "Start game (▶)",
        "dbColumnNames": ["Games.Filename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Filename AS [Games.Filename]",
        "dbIdentifiers": ["Games.Filename", "Filename"],
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
    },
    {
        "id": "pic",
        "screenName": "Picture",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[1]",
        "screenName": "Picture 2",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[2]",
        "screenName": "Picture 3",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[3]",
        "screenName": "Picture 4",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[4]",
        "screenName": "Picture 5",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "id",
        "screenName": "ID",
        "dbColumnNames": ["Games.GA_Id"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.GA_Id AS [Games.GA_Id]",
        "dbIdentifiers": ["Games.GA_Id", "GA_Id"],
        "dbType": "Long Integer",
        "defaultWidth": 50,
        "sortable": False,
        "filterable": False,
        "textAlignment": "left",
        "comment": "Unique ID"
    },
    {
        "id": "name",
        "screenName": "Name",
        "dbColumnNames": ["Games.Name"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Name AS [Games.Name]",
        "dbIdentifiers": ["Games.Name", "Name"],
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Game Name"
    },
    {
        "id": "year",
        "screenName": "Year",
        "dbColumnNames": ["Games.YE_Id", "Years.Year"],
        "dbTableNames": ["Years"],
        "dbSelect": "Years.Year AS [Years.Year]",
        "dbIdentifiers": ["Years.Year", "Year"],
        "dbType": "Long Integer",
        "defaultWidth": 75,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "The Year (9999 = Unknown year)"
    },
    {
        "id": "publisher",
        "screenName": "Publisher",
        "dbColumnNames": ["Games.PU_Id", "Publishers.Publisher"],
        "dbTableNames": ["Publishers"],
        "dbSelect": "Publishers.Publisher AS [Publishers.Publisher]",
        "dbIdentifiers": ["Publishers.Publisher", "Publisher"],
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "developer",
        "screenName": "Developer",
        "dbColumnNames": ["Games.DE_Id", "Developers.Developer"],
        "dbTableNames": ["Developers"],
        "dbSelect": "Developers.Developer AS [Developers.Developer]",
        "dbIdentifiers": ["Developers.Developer", "Developer"],
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "programmer",
        "screenName": "Programmer",
        "dbColumnNames": ["Games.PR_Id", "Programmers.Programmer"],
        "dbTableNames": ["Programmers"],
        "dbSelect": "Programmers.Programmer AS [Programmers.Programmer]",
        "dbIdentifiers": ["Programmers.Programmer", "Programmer"],
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "parent_genre",
        "screenName": "Parent genre",
        "dbColumnNames": ["Games.GE_Id", "Genres.PG_Id", "PGenres.ParentGenre"],
        "dbTableNames": ["PGenres"],
        "dbSelect": "PGenres.ParentGenre AS [PGenres.ParentGenre]",
        "dbIdentifiers": ["PGenres.ParentGenre", "ParentGenre"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "genre",
        "screenName": "Genre",
        "dbColumnNames": ["Games.GE_Id", "Genres.Genre"],
        "dbTableNames": ["Genres"],
        "dbSelect": "Genres.Genre AS [Genres.Genre]",
        "dbIdentifiers": ["Genres.Genre", "Genre"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "language",
        "screenName": "Language",
        "dbColumnNames": ["Games.LA_Id", "Languages.Language"],
        "dbTableNames": ["Languages"],
        "dbSelect": "Languages.Language AS [Languages.Language]",
        "dbIdentifiers": ["Languages.Language", "Language"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "cracker",
        "screenName": "Cracker",
        "dbColumnNames": ["Games.CR_Id", "Crackers.Cracker"],
        "dbTableNames": ["Crackers"],
        "dbSelect": "Crackers.Cracker AS [Crackers.Cracker]",
        "dbIdentifiers": ["Crackers.Cracker", "Cracker"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "artist",
        "screenName": "Artist",
        "dbColumnNames": ["Games.AR_Id", "Artists.Artist"],
        "dbTableNames": ["Artists"],
        "dbSelect": "Artists.Artist AS [Artists.Artist]",
        "dbIdentifiers": ["Artists.Artist", "Artist"],
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "license",
        "screenName": "License",
        "dbColumnNames": ["Games.LI_Id", "Licenses.License"],
        "dbTableNames": ["Licenses"],
        "dbSelect": "Licenses.License AS [Licenses.License]",
        "dbIdentifiers": ["Licenses.License", "License"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "rarity",
        "screenName": "Rarity",
        "dbColumnNames": ["Games.RA_Id", "Rarities.Rarity"],
        "dbTableNames": ["Rarities"],
        "dbSelect": "Rarities.Rarity AS [Rarities.Rarity]",
        "dbIdentifiers": ["Rarities.Rarity", "Rarity"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "musician_name",
        "screenName": "Musician",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Musician"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Musician AS [Musicians.Musician]",
        "dbIdentifiers": ["Musicians.Musician", "Musician"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "musician_photo",
        "screenName": "Musician photo",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Photo"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Photo AS [Musicians.Photo]",
        "dbIdentifiers": ["Musicians.Photo", "Photo"],
        "dbType": "Text (510)",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Musician Photo within Photo Path"
    },
    {
        "id": "musician_group",
        "screenName": "Musician group",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Grp"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Grp AS [Musicians.Grp]",
        "dbIdentifiers": ["Musicians.Grp", "Grp"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "musician_nick",
        "screenName": "Musician nick",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Nick"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Nick AS [Musicians.Nick]",
        "dbIdentifiers": ["Musicians.Nick", "Nick"],
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "music",
        "screenName": "Start music (M)",
        "dbColumnNames": ["Games.SidFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.SidFilename AS [Games.SidFilename]",
        "dbIdentifiers": ["Games.SidFilename", "SidFilename"],
        "dbType": "Memo/Hyperlink (255)",
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
        "comment": "Music Filename within Music Path"
    },
    {
        "id": "pal_ntsc",
        "screenName": "PAL/NTSC",
        "dbColumnNames": ["Games.V_PalNTSC"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_PalNTSC AS [Games.V_PalNTSC]",
        "dbIdentifiers": ["Games.V_PalNTSC", "V_PalNTSC"],
        "dbType": "Long Integer",
        "type": "enum",
        "enumMap": {
            0: "PAL",
            1: "both",
            2: "NTSC",
            3: "PAL[+NTSC?]"
        },
        "defaultWidth": 75,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Game version is PAL, NTSC or BOTH (0=PAL, 1=BOTH, 2=NTSC, 3=PAL[+NTSC?])"
    },
    {
        "id": "control",
        "screenName": "Control",
        "dbColumnNames": ["Games.Control"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Control AS [Games.Control]",
        "dbIdentifiers": ["Games.Control", "Control"],
        "dbType": "Long Integer",
        "type": "enum",
        "enumMap": {
            0: "JoyPort2",
            1: "JoyPort1",
            2: "Keyboard",
            3: "PaddlePort2",
            4: "PaddlePort1",
            5: "Mouse",
            6: "LightPen",
            7: "KoalaPad",
            8: "LightGun"
        },
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Game's control method (0=JoyPort2, 1=JoyPort1, 2=Keyboard, 3=PaddlePort2, 4=PaddlePort1, 5=Mouse, 6=LightPen, 7=KoalaPad, 8=LightGun"
    },
    {
        "id": "clone_of",
        "screenName": "Clone of",
        "dbColumnNames": ["Games.CloneOf"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.CloneOf AS [Games.CloneOf]",
        "dbIdentifiers": ["Games.CloneOf", "CloneOf"],
        "dbType": "Long Integer",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "prequel",
        "screenName": "Prequel",
        "dbColumnNames": ["Games.Prequel"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Prequel AS [Games.Prequel]",
        "dbIdentifiers": ["Games.Prequel", "Prequel"],
        "dbType": "Long Integer NOT NULL",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Link to GA_ID of prequel game (0 if no prequel)"
    },
    {
        "id": "sequel",
        "screenName": "Sequel",
        "dbColumnNames": ["Games.Sequel"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Sequel AS [Games.Sequel]",
        "dbIdentifiers": ["Games.Sequel", "Sequel"],
        "dbType": "Long Integer NOT NULL",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Link to GA_ID of sequel game (0 if no sequel)"
    },
    {
        "id": "related",
        "screenName": "Related",
        "dbColumnNames": ["Games.Related"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Related AS [Games.Related]",
        "dbIdentifiers": ["Games.Related", "Related"],
        "dbType": "Long Integer NOT NULL",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Link to GA_ID of related game (0 if no related game)"
    },
    {
        "id": "gemus",
        "screenName": "Gemus",
        "dbColumnNames": ["Games.Gemus"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Gemus AS [Games.Gemus]",
        "dbIdentifiers": ["Games.Gemus", "Gemus"],
        "dbType": "Memo/Hyperlink (255)",
        "defaultWidth": 200,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },

    {
        "id": "players_from",
        "screenName": "Players from",
        "dbColumnNames": ["Games.PlayersFrom"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.PlayersFrom AS [Games.PlayersFrom]",
        "dbIdentifiers": ["Games.PlayersFrom", "PlayersFrom"],
        "dbType": "Long Integer",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Minimum number of players the game supports (-1=Unknown)"
    },
    {
        "id": "players_to",
        "screenName": "Players to",
        "dbColumnNames": ["Games.PlayersTo"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.PlayersTo AS [Games.PlayersTo]",
        "dbIdentifiers": ["Games.PlayersTo", "PlayersTo"],
        "dbType": "Long Integer",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Maximum number of players the game supports (-1=Unknown)"
    },
    {
        "id": "players_sim",
        "screenName": "Players simultaneous",
        "dbColumnNames": ["Games.PlayersSim"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.PlayersSim AS [Games.PlayersSim]",
        "dbIdentifiers": ["Games.PlayersSim", "PlayersSim"],
        "dbType": "Boolean NOT NULL",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "The Game can be played by more than one player simultaneously"
    },
    {
        "id": "players",
        "screenName": "Players",
        "dbColumnNames": ["Games.PlayersFrom", "Games.PlayersTo", "Games.PlayersSim"],
        "dbTableNames": ["Games"],
        "dbSelect": "iif(Games.PlayersFrom == Games.PlayersTo, Games.PlayersFrom, Games.PlayersFrom || ' - ' || Games.PlayersTo) || iif(Games.PlayersSim, ' (simultaneous)', '') AS Players",
        "dbIdentifiers": ["Players"],
        #"dbType": "Long Integer",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left"
    },
]

def usableColumn_getBySlice(i_startPos=None, i_endPos=None):
    """
    Params:
     i_startPos, i_endPos:
      Either (int)
      or (None)

    Returns:
     (list of UsableColumn)
    """
    return g_usableColumns[i_startPos:i_endPos]

def usableColumn_getById(i_id):
    """
    Params:
     i_id:
      (str)

    Returns:
     Either (UsableColumn)
     or (None)
    """
    columns = [column  for column in g_usableColumns  if column["id"] == i_id]
    if len(columns) == 0:
        return None
    return columns[0]

def usableColumn_getByDbIdentifier(i_identifier):
    """
    Params:
     i_identifier:
      (str)
      A column name, with optional table name prefix.
      eg.
       "Name"
       "Games.Name"

    Returns:
     Either (UsableColumn)
     or (None)
    """
    for usableColumn in g_usableColumns:
        if "dbIdentifiers" in usableColumn:
            for dbIdentifier in usableColumn["dbIdentifiers"]:
                if dbIdentifier == i_identifier:
                    return usableColumn
    return None

# + }}}

# + In GUI table view {{{

g_tableColumns = []
# (list of TableColumn)

# Type: TableColumn
#  (dict)
#  Has keys:
#   screenName:
#    (str)
#    Used in
#     heading button, if it's visible
#     list of fields on right-click menu
#   width:
#    (int)
#    In pixels

# + + New column accessors {{{

def tableColumn_add(i_id, i_width=None, i_beforeColumnId=None):
    """
    Add a column to the live table view.

    Params:
     i_id:
      (str)
      ID of column to add to the table view.
      Details of it should exist in g_usableColumns.
     i_width:
      Either (int)
       Width for new column in pixels
      or (None)
       Use default width from g_usableColumns.
     i_beforeColumnId:
      Either (str)
       ID of column already present in the table view to insert this column before.
      or (None)
       Add the new column as the last one.

    Returns:
     Either (TableColumn)
     or (None)
      The given i_id does not correspond to a usable column (it may not exist in the current Gamebase database).
    """
    usableColumn = usableColumn_getById(i_id)
    if usableColumn == None:
        return None

    newTableColumn = {
        "id": usableColumn["id"],
        "screenName": usableColumn["screenName"],
        "sortable": usableColumn["sortable"],
        "filterable": usableColumn["filterable"]
    }
    if i_width != None:
        newTableColumn["width"] = i_width
    else:
        newTableColumn["width"] = usableColumn["defaultWidth"]
    if "textAlignment" in usableColumn:
        newTableColumn["textAlignment"] = usableColumn["textAlignment"]

    # Either append column at end or insert it before i_beforeColumnId
    if i_beforeColumnId == None:
        g_tableColumns.append(newTableColumn)
    else:
        g_tableColumns.insert(tableColumn_idToPos(i_beforeColumnId), newTableColumn)

    # Return the new table column
    return newTableColumn

def tableColumn_remove(i_id):
    foundColumnNo = None
    for columnNo, column in enumerate(g_tableColumns):
        if column["id"] == i_id:
            foundColumnNo = columnNo
            break
    if foundColumnNo != None:
        del(g_tableColumns[foundColumnNo])

def tableColumn_toggle(i_id, i_addBeforeColumnId=None):
    """
    Params:
     i_id:
      (str)
      ID of column to toggle the visibility of.
      Details of it should exist in g_usableColumns.
     i_addBeforeColumnId:
      If the column is to be shown
      Either (str)
       ID of column already present in the table view to insert this column before.
      or (None)
       Add the new column as the last one.

    Returns:
     (bool)
     True: the column is now visible
     False: the column is now hidden
    """
    present = tableColumn_getById(i_id)
    if not present:
        tableColumn_add(i_id, None, i_addBeforeColumnId)
        return True
    else:
        tableColumn_remove(i_id)
        return False

def tableColumn_move(i_moveColumn, i_beforeColumn):
    """
    Move a column.

    Params:
     i_moveColumn:
      (TableColumn)
      Column to move.
     i_beforeColumn:
      Either (TableColumn)
       Move to before of this column.
      or (None)
       Move to the end.
    """
    # Delete column from original position
    del(g_tableColumns[g_tableColumns.index(i_moveColumn)])

    # Reinsert/append in new position
    if i_beforeColumn == None:
        g_tableColumns.append(i_moveColumn)
    else:
        g_tableColumns.insert(g_tableColumns.index(i_beforeColumn), i_moveColumn)

def tableColumn_count():
    """
    Count the visible columns.

    Returns:
     (int)
    """
    return len(g_tableColumns)

def tableColumn_getBySlice(i_startPos=None, i_endPos=None):
    """
    Get the objects of a range of visible columns.

    Params:
     i_startPos, i_endPos:
      Either (int)
      or (None)

    Returns:
     (list of TableColumn)
    """
    return g_tableColumns[i_startPos:i_endPos]

def tableColumn_getByPos(i_pos):
    """
    Get the object of the n'th column.

    Params:
     i_pos:
      (int)

    Returns:
     Either (TableColumn)
     or (None)
    """
    if i_pos < 0 or i_pos >= len(g_tableColumns):
        return None
    return g_tableColumns[i_pos]

def tableColumn_getById(i_id):
    """
    Get the object of the column with some ID.

    Params:
     i_id:
      (str)

    Returns:
     Either (TableColumn)
     or (None)
    """
    # [could shorten with next()]
    for column in g_tableColumns:
        if column["id"] == i_id:
            return column
    return None

def tableColumn_idToPos(i_id):
    """
    Get the visible position of the column with some ID.

    Params:
     i_id:
      (str)

    Returns:
     (int)
     Visible position of the column with the given ID.
     -1: There was no visible column with this ID.
    """
    visiblePos = -1
    for column in g_tableColumns:
        visiblePos += 1
        if i_id == column["id"]:
            return visiblePos
    return -1

# + + }}}

# + }}}

def filterColumnsByDb(i_dbTableNames, i_dbSchema):
    """
    """
    # Remove columns from g_usableColumns that rely on tables and columns that don't exist in the database
    global g_usableColumns
    def validateUsableColumn(i_usableColumn):
        rv = True
        if "dbTableNames" in i_usableColumn:
            for dbTableName in i_usableColumn["dbTableNames"]:
                if not (dbTableName in i_dbTableNames):
                    rv = False
        if "dbColumnNames" in i_usableColumn:
            for dbColumnName in i_usableColumn["dbColumnNames"]:
                tableName, columnName = dbColumnName.split(".")
                if not (tableName in i_dbSchema.keys()):
                    rv = False
                else:
                    columnNames = [row["name"]  for row in i_dbSchema[tableName]]
                    if not (columnName in columnNames):
                        rv = False
        return rv
    g_usableColumns = [column  for column in g_usableColumns  if validateUsableColumn(column)]

    # Remove columns from g_tableColumns that don't exist in g_usableColumns
    global g_tableColumns
    g_tableColumns = [column  for column in g_tableColumns  if usableColumn_getById(column["id"])]

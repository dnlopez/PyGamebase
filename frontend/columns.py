
# + Table column specs {{{

# g_tableColumnSpecs:
#  (list of TableColumnSpec)
#
# type: TableColumnSpec
#  (dict)
#  Dict has specific key-value properties:
#   id:
#    (str)
#    A unique internal identifier for the column.
#   menuPath:
#    (list of str)
#    Path under which to show this column in column selection menus.
#    All components except the last are submenu names, and the last component is the actual menu item name.
#   headingName:
#    (str)
#    The text that will appear in the heading for this column.
#   dbTableNames:
#    (list of str)
#    Names of tables,
#    that must all exist in the database, for the value of this column spec to be able to be assembled from it.
#    These tables will be joined to when doing a database query to get the information for this column.
#   dbColumnNames:
#    (list of str)
#    Fully-qualified (ie. "<table name>.<column name>") names of columns,
#    that must all exist in the database, for the value of this column spec to be able to be assembled from it.
#   dbSelect:
#    Either (str)
#     The term to add to the SELECT clause to assemble a value for this column spec,
#     which will be used when the presence in the database of everything named by dbTableNames and dbColumnNames implies that this is possible.
#     It should end with an "AS ..." alias for predictable referencing in filters and so on.
#     For a simple, single database column select (as opposed to an expression) use "AS [<table name>.<column name>]".
#    or unspecified
#     Don't add any terms to the SELECT clause for this column.
#   dbSelectPlaceholder:
#    (str)
#    The term to add to the SELECT clause to assemble a fallback value for this column spec,
#    which will be used when the absence of something in the database named by dbTableNames and dbColumnNames implies that this is not possible.
#    Normally this fallback value could be NULL. It could also possibly be a string like 'Unknown'.
#    It should end with the "AS ..." alias as dbSelect does.
#   dbIdentifiers:
#    (list of str)
#    Identifiers which can be used to refer to this column in the WHERE clause.
#    The first of these should be the fully qualified (for a simple column select) or otherwise chosen (for an expression)
#    name given after "AS" in 'dbSelect'.
#    Further identifiers may be shorter, still valid alternatives, eg. "<column name>" alone.
#    These alternatives will consequently be recognised if used in an expression on the  SQL filter bar.
#   defaultWidth:
#    (int)
#    Initial width for the column in pixels.
#   sortable:
#    (bool)
#    True: Give the column a visible heading which can be clicked to sort by it.
#   filterable:
#    (bool)
#    True: Give the column a filter box under its heading.
#   textAlignment:
#    (str)
#    How to align text in the column.
#    One of
#     "left"
#     "center"
#   mdbType:
#    (str)
#    As exported from a GameBase 64 MDB file. Not currently used by this program.
#   mdbComment:
#    (str)
#    As exported from a GameBase 64 MDB file. Not currently used by this program.

g_tableColumnSpecs = [
    # Gamebase
    {
        "id": "schema",
        "menuPath": ["Gamebase", "Name"],
        "headingName": "GB",
        "dbColumnNames": [],
        "dbTableNames": [],
        #"dbSelect": "SchemaName",
        #"dbSelectPlaceholder": "NULL AS [Games.PlayersSim]",
        "dbIdentifiers": ["SchemaName"],
        "defaultWidth": 80,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "schema_title",
        "menuPath": ["Gamebase", "Title"],
        "headingName": "GB",
        "dbColumnNames": [],
        "dbTableNames": [],
        #"dbSelect": "SchemaName",
        #"dbSelectPlaceholder": "NULL AS [Games.PlayersSim]",
        "dbIdentifiers": ["SchemaName"],
        "defaultWidth": 80,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "schema_image",
        "menuPath": ["Gamebase", "Image"],
        "headingName": "GB",
        "dbColumnNames": [],
        "dbTableNames": [],
        #"dbSelect": "SchemaName",
        #"dbSelectPlaceholder": "NULL AS [Games.PlayersSim]",
        "dbIdentifiers": ["SchemaName"],
        "defaultWidth": 80,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },

    # Launch
    {
        "id": "detail",
        "menuPath": ["Launch", "Show detail (+)"],
        "headingName": "Show detail (+)",
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
    },
    {
        "id": "play",
        "menuPath": ["Launch", "Start game (▶)"],
        "headingName": "Start game (▶)",
        "dbColumnNames": ["Games.Filename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Filename AS [Games.Filename]",
        "dbSelectPlaceholder": "NULL AS [Games.Filename]",
        "dbIdentifiers": ["Games.Filename", "Filename"],
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
    },
    {
        "id": "music",
        "menuPath": ["Launch", "Start music (M)"],
        "headingName": "Start music (M)",
        "dbColumnNames": ["Games.SidFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.SidFilename AS [Games.SidFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.SidFilename]",
        "dbIdentifiers": ["Games.SidFilename", "SidFilename"],
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
        "mdbType": "Memo/Hyperlink (255)",
        "mdbComment": "Music Filename within Music Path"
    },

    # Screenshots
    {
        "id": "pic[0]",
        "menuPath": ["Screenshots", "1"],
        "headingName": "1",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[1]",
        "menuPath": ["Screenshots", "2"],
        "headingName": "2",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[2]",
        "menuPath": ["Screenshots", "3"],
        "headingName": "3",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[3]",
        "menuPath": ["Screenshots", "4"],
        "headingName": "4",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[4]",
        "menuPath": ["Screenshots", "5"],
        "headingName": "5",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[5]",
        "menuPath": ["Screenshots", "6"],
        "headingName": "6",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[6]",
        "menuPath": ["Screenshots", "7"],
        "headingName": "7",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[7]",
        "menuPath": ["Screenshots", "8"],
        "headingName": "8",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[8]",
        "menuPath": ["Screenshots", "9"],
        "headingName": "9",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "pic[9]",
        "menuPath": ["Screenshots", "10"],
        "headingName": "10",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },

    # Screenshots (random order)
    {
        "id": "random_pic[0]",
        "menuPath": ["Screenshots (random order)", "1"],
        "headingName": "1",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[1]",
        "menuPath": ["Screenshots (random order)", "2"],
        "headingName": "2",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[2]",
        "menuPath": ["Screenshots (random order)", "3"],
        "headingName": "3",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[3]",
        "menuPath": ["Screenshots (random order)", "4"],
        "headingName": "4",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[4]",
        "menuPath": ["Screenshots (random order)", "5"],
        "headingName": "5",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[5]",
        "menuPath": ["Screenshots (random order)", "6"],
        "headingName": "6",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[6]",
        "menuPath": ["Screenshots (random order)", "7"],
        "headingName": "7",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[7]",
        "menuPath": ["Screenshots (random order)", "8"],
        "headingName": "8",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[8]",
        "menuPath": ["Screenshots (random order)", "9"],
        "headingName": "9",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "random_pic[9]",
        "menuPath": ["Screenshots (random order)", "10"],
        "headingName": "10",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },

    #
    {
        "id": "name",
        "menuPath": ["Name"],
        "headingName": "Name",
        "dbColumnNames": ["Games.Name"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Name AS [Games.Name]",
        "dbSelectPlaceholder": "NULL AS [Games.Name]",
        "dbIdentifiers": ["Games.Name", "Name"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
        "mdbComment": "Game Name"
    },
    {
        "id": "year",
        "menuPath": ["Year"],
        "headingName": "Year",
        "dbColumnNames": ["Games.YE_Id", "Years.Year"],
        "dbTableNames": ["Years"],
        "dbSelect": "Years.Year AS [Years.Year]",
        "dbSelectPlaceholder": "NULL AS [Years.Year]",
        "dbIdentifiers": ["Years.Year", "Year"],
        "defaultWidth": 75,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "The Year (9999 = Unknown year)"
    },

    # Staff
    {
        "id": "publisher",
        "menuPath": ["Staff", "Publisher"],
        "headingName": "Publisher",
        "dbColumnNames": ["Games.PU_Id", "Publishers.Publisher"],
        "dbTableNames": ["Publishers"],
        "dbSelect": "Publishers.Publisher AS [Publishers.Publisher]",
        "dbSelectPlaceholder": "NULL AS [Publishers.Publisher]",
        "dbIdentifiers": ["Publishers.Publisher", "Publisher"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "mdbType": "Text (510)",
        "textAlignment": "left",
    },
    {
        "id": "developer",
        "menuPath": ["Staff", "Developer"],
        "headingName": "Developer",
        "dbColumnNames": ["Games.DE_Id", "Developers.Developer"],
        "dbTableNames": ["Developers"],
        "dbSelect": "Developers.Developer AS [Developers.Developer]",
        "dbSelectPlaceholder": "NULL AS [Developers.Developer]",
        "dbIdentifiers": ["Developers.Developer", "Developer"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "mdbType": "Text (510)",
        "textAlignment": "left",
    },
    {
        "id": "programmer",
        "menuPath": ["Staff", "Programmer"],
        "headingName": "Programmer",
        "dbColumnNames": ["Games.PR_Id", "Programmers.Programmer"],
        "dbTableNames": ["Programmers"],
        "dbSelect": "Programmers.Programmer AS [Programmers.Programmer]",
        "dbSelectPlaceholder": "NULL AS [Programmers.Programmer]",
        "dbIdentifiers": ["Programmers.Programmer", "Programmer"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "artist",
        "menuPath": ["Staff", "Artist"],
        "headingName": "Artist",
        "dbColumnNames": ["Games.AR_Id", "Artists.Artist"],
        "dbTableNames": ["Artists"],
        "dbSelect": "Artists.Artist AS [Artists.Artist]",
        "dbSelectPlaceholder": "NULL AS [Artists.Artist]",
        "dbIdentifiers": ["Artists.Artist", "Artist"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "musician_name",
        "menuPath": ["Staff", "Musician", "Musician"],
        "headingName": "Musician",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Musician"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Musician AS [Musicians.Musician]",
        "dbSelectPlaceholder": "NULL AS [Musicians.Musician]",
        "dbIdentifiers": ["Musicians.Musician", "Musician"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "musician_photo",
        "menuPath": ["Staff", "Musician", "Musician photo"],
        "headingName": "Musician photo",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Photo"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Photo AS [Musicians.Photo]",
        "dbSelectPlaceholder": "NULL AS [Musicians.Photo]",
        "dbIdentifiers": ["Musicians.Photo", "Photo"],
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
        "mdbComment": "Musician Photo within Photo Path"
    },
    {
        "id": "musician_group",
        "menuPath": ["Staff", "Musician", "Musician group"],
        "headingName": "Musician group",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Grp"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Grp AS [Musicians.Grp]",
        "dbSelectPlaceholder": "NULL AS [Musicians.Grp]",
        "dbIdentifiers": ["Musicians.Grp", "Grp"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "musician_nick",
        "menuPath": ["Staff", "Musician", "Musician nick"],
        "headingName": "Musician nick",
        "dbColumnNames": ["Games.MU_Id", "Musicians.Nick"],
        "dbTableNames": ["Musicians"],
        "dbSelect": "Musicians.Nick AS [Musicians.Nick]",
        "dbSelectPlaceholder": "NULL AS [Musicians.Nick]",
        "dbIdentifiers": ["Musicians.Nick", "Nick"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },

    # Genre
    {
        "id": "genre_combined",
        "menuPath": ["Genre", "Genre (combined info)"],
        "headingName": "Genre",
        "dbColumnNames": ["Games.GE_Id", "Genres.Genre", "Genres.PG_Id", "PGenres.ParentGenre"],
        "dbTableNames": ["Genres", "PGenres"],
        "dbSelect": "iif(PGenres.ParentGenre IS NOT NULL, (PGenres.ParentGenre || ' : ' || Genres.Genre), Genres.Genre) AS GenreCombined",
        "dbSelectPlaceholder": "NULL AS GenreCombined",
        "dbIdentifiers": ["GenreCombined"],
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left"
    },
    {
        "id": "parent_genre",
        "menuPath": ["Genre", "Parent genre"],
        "headingName": "Parent genre",
        "dbColumnNames": ["Games.GE_Id", "Genres.PG_Id", "PGenres.ParentGenre"],
        "dbTableNames": ["PGenres"],
        "dbSelect": "PGenres.ParentGenre AS [PGenres.ParentGenre]",
        "dbSelectPlaceholder": "NULL AS [PGenres.ParentGenre]",
        "dbIdentifiers": ["PGenres.ParentGenre", "ParentGenre"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "genre",
        "menuPath": ["Genre", "Genre"],
        "headingName": "Genre",
        "dbColumnNames": ["Games.GE_Id", "Genres.Genre"],
        "dbTableNames": ["Genres"],
        "dbSelect": "Genres.Genre AS [Genres.Genre]",
        "dbSelectPlaceholder": "NULL AS [Genres.Genre]",
        "dbIdentifiers": ["Genres.Genre", "Genre"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },

    {
        "id": "control",
        "menuPath": ["Control"],
        "headingName": "Control",
        "dbColumnNames": ["Games.Control"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Control AS [Games.Control]",
        "dbSelectPlaceholder": "NULL AS [Games.Control]",
        "dbIdentifiers": ["Games.Control", "Control"],
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
        "mdbType": "Long Integer",
        "mdbComment": "Game's control method (0=JoyPort2, 1=JoyPort1, 2=Keyboard, 3=PaddlePort2, 4=PaddlePort1, 5=Mouse, 6=LightPen, 7=KoalaPad, 8=LightGun"
    },

    # Players
    {
        "id": "players",
        "menuPath": ["Players", "Players (combined info)"],
        "headingName": "Players",
        "dbColumnNames": ["Games.PlayersFrom", "Games.PlayersTo", "Games.PlayersSim"],
        "dbTableNames": ["Games"],
        "dbSelect": "iif(Games.PlayersFrom == Games.PlayersTo, Games.PlayersFrom, Games.PlayersFrom || ' - ' || Games.PlayersTo) || iif(Games.PlayersSim, ' (simultaneous)', '') AS Players",
        "dbSelectPlaceholder": "NULL AS Players",
        "dbIdentifiers": ["Players"],
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left"
    },
    {
        "id": "players_from",
        "menuPath": ["Players", "Players from"],
        "headingName": "Players from",
        "tooltip": "Minimum number of players the game supports (-1=Unknown)",
        "dbColumnNames": ["Games.PlayersFrom"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.PlayersFrom AS [Games.PlayersFrom]",
        "dbSelectPlaceholder": "NULL AS [Games.PlayersFrom]",
        "dbIdentifiers": ["Games.PlayersFrom", "PlayersFrom"],
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "Minimum number of players the game supports (-1=Unknown)"
    },
    {
        "id": "players_to",
        "menuPath": ["Players", "Players to"],
        "headingName": "Players to",
        "dbColumnNames": ["Games.PlayersTo"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.PlayersTo AS [Games.PlayersTo]",
        "dbSelectPlaceholder": "NULL AS [Games.PlayersTo]",
        "dbIdentifiers": ["Games.PlayersTo", "PlayersTo"],
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "Maximum number of players the game supports (-1=Unknown)"
    },
    {
        "id": "players_sim",
        "menuPath": ["Players", "Players simultaneous"],
        "headingName": "Players simultaneous",
        "dbColumnNames": ["Games.PlayersSim"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.PlayersSim AS [Games.PlayersSim]",
        "dbSelectPlaceholder": "NULL AS [Games.PlayersSim]",
        "dbIdentifiers": ["Games.PlayersSim", "PlayersSim"],
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Boolean NOT NULL",
        "mdbComment": "The Game can be played by more than one player simultaneously"
    },

    # Content
    {
        "id": "v_trainers",
        "menuPath": ["Content", "V Trainers"],
        "headingName": "V Trainers",
        "dbColumnNames": ["Games.V_Trainers"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_Trainers AS [Games.V_Trainers]",
        "dbSelectPlaceholder": "NULL AS [Games.V_Trainers]",
        "dbIdentifiers": ["Games.V_Trainers", "V_Trainers"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "Game version's number of trainers (-1=Unknown)"
    },
    {
        "id": "adult",
        "menuPath": ["Content", "Adult"],
        "headingName": "Adult",
        "dbColumnNames": ["Games.Adult"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Adult AS [Games.Adult]",
        "dbSelectPlaceholder": "NULL AS [Games.Adult]",
        "dbIdentifiers": ["Games.Adult", "Adult"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Boolean NOT NULL",
        "mdbComment": "The game has adult content"
    },
    {
        "id": "v_loading_screen",
        "menuPath": ["Content", "V Loading screen"],
        "headingName": "V Loading screen",
        "dbColumnNames": ["Games.V_LoadingScreen"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_LoadingScreen AS [Games.V_LoadingScreen]",
        "dbSelectPlaceholer": "NULL AS [Games.V_LoadingScreen]",
        "dbIdentifiers": ["Games.V_LoadingScreen", "V_LoadingScreen"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "v_high_score_saver",
        "menuPath": ["Content", "V High score saver"],
        "headingName": "V High score saver",
        "dbColumnNames": ["Games.V_HighScoreSaver"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_HighScoreSaver AS [Games.V_HighScoreSaver]",
        "dbSelectPlaceholder": "NULL AS [Games.V_HighScoreSaver]",
        "dbIdentifiers": ["Games.V_HighScoreSaver", "V_HighScoreSaver"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "v_included_docs",
        "menuPath": ["Content", "V Included docs"],
        "headingName": "V Included docs",
        "dbColumnNames": ["Games.V_IncludedDocs"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_IncludedDocs AS [Games.V_IncludedDocs]",
        "dbSelectPlaceholder": "NULL AS [Games.V_IncludedDocs]",
        "dbIdentifiers": ["Games.V_IncludedDocs", "V_IncludedDocs"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "v_title_screen",
        "menuPath": ["Content", "V Title screen"],
        "headingName": "V Title screen",
        "dbColumnNames": ["Games.V_TitleScreen"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_TitleScreen AS [Games.V_TitleScreen]",
        "dbSelectPlaceholder": "NULL AS [Games.V_TitleScreen]",
        "dbIdentifiers": ["Games.V_TitleScreen", "V_TitleScreen"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },

    # Region
    {
        "id": "language",
        "menuPath": ["Region", "Language"],
        "headingName": "Language",
        "dbColumnNames": ["Games.LA_Id", "Languages.Language"],
        "dbTableNames": ["Languages"],
        "dbSelect": "Languages.Language AS [Languages.Language]",
        "dbSelectPlaceholder": "NULL AS [Languages.Language]",
        "dbIdentifiers": ["Languages.Language", "Language"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "pal_ntsc",
        "menuPath": ["Region", "PAL/NTSC"],
        "headingName": "PAL/NTSC",
        "dbColumnNames": ["Games.V_PalNTSC"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_PalNTSC AS [Games.V_PalNTSC]",
        "dbSelectPlaceholder": "NULL AS [Games.V_PalNTSC]",
        "dbIdentifiers": ["Games.V_PalNTSC", "V_PalNTSC"],
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
        "mdbType": "Long Integer",
        "mdbComment": "Game version is PAL, NTSC or BOTH (0=PAL, 1=BOTH, 2=NTSC, 3=PAL[+NTSC?])"
    },

    # Related games
    {
        "id": "clone_of",
        "menuPath": ["Related games", "Clone of"],
        "headingName": "Clone of",
        "dbColumnNames": ["Games.CloneOf"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.CloneOf AS [Games.CloneOf]",
        "dbSelectPlaceholder": "NULL AS [Games.CloneOf]",
        "dbIdentifiers": ["Games.CloneOf", "CloneOf"],
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "mdbType": "Long Integer",
        "textAlignment": "left",
    },
    {
        "id": "prequel",
        "menuPath": ["Related games", "Prequel"],
        "headingName": "Prequel",
        "dbColumnNames": ["Games.Prequel"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Prequel AS [Games.Prequel]",
        "dbSelectPlaceholder": "NULL AS [Games.Prequel]",
        "dbIdentifiers": ["Games.Prequel", "Prequel"],
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer NOT NULL",
        "mdbComment": "Link to GA_ID of prequel game (0 if no prequel)"
    },
    {
        "id": "sequel",
        "menuPath": ["Related games", "Sequel"],
        "headingName": "Sequel",
        "dbColumnNames": ["Games.Sequel"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Sequel AS [Games.Sequel]",
        "dbSelectPlaceholder": "NULL AS [Games.Sequel]",
        "dbIdentifiers": ["Games.Sequel", "Sequel"],
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer NOT NULL",
        "mdbComment": "Link to GA_ID of sequel game (0 if no sequel)"
    },
    {
        "id": "related",
        "menuPath": ["Related games", "Related"],
        "headingName": "Related",
        "dbColumnNames": ["Games.Related"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Related AS [Games.Related]",
        "dbSelectPlaceholder": "NULL AS [Games.Related]",
        "dbIdentifiers": ["Games.Related", "Related"],
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer NOT NULL",
        "mdbComment": "Link to GA_ID of related game (0 if no related game)"
    },

    #
    {
        "id": "cracker",
        "menuPath": ["Cracker"],
        "headingName": "Cracker",
        "dbColumnNames": ["Games.CR_Id", "Crackers.Cracker"],
        "dbTableNames": ["Crackers"],
        "dbSelect": "Crackers.Cracker AS [Crackers.Cracker]",
        "dbSelectPlaceholder": "NULL AS [Crackers.Cracker]",
        "dbIdentifiers": ["Crackers.Cracker", "Cracker"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },

    {
        "id": "license",
        "menuPath": ["License"],
        "headingName": "License",
        "dbColumnNames": ["Games.LI_Id", "Licenses.License"],
        "dbTableNames": ["Licenses"],
        "dbSelect": "Licenses.License AS [Licenses.License]",
        "dbSelectPlaceholder": "NULL AS [Licenses.License]",
        "dbIdentifiers": ["Licenses.License", "License"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "rarity",
        "menuPath": ["Rarity"],
        "headingName": "Rarity",
        "dbColumnNames": ["Games.RA_Id", "Rarities.Rarity"],
        "dbTableNames": ["Rarities"],
        "dbSelect": "Rarities.Rarity AS [Rarities.Rarity]",
        "dbSelectPlaceholder": "NULL AS [Rarities.Rarity]",
        "dbIdentifiers": ["Rarities.Rarity", "Rarity"],
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },

    {
        "id": "difficulty",
        "menuPath": ["Difficulty"],
        "headingName": "Difficulty",
        "dbColumnNames": ["Difficulty.Difficulty"],
        "dbTableNames": ["Difficulty"],
        "dbSelect": "Difficulty.Difficulty AS [Difficulty.Difficulty]",
        "dbSelectPlaceholder": "NULL AS [Difficulty.Difficulty]",
        "dbIdentifiers": ["Difficulty.Difficulty", "Difficulty"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },

    {
        "id": "classic",
        "menuPath": ["Classic"],
        "headingName": "Classic",
        "dbColumnNames": ["Games.Classic"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Classic AS [Games.Classic]",
        "dbSelectPlaceholder": "NULL AS [Games.Classic]",
        "dbIdentifiers": ["Games.Classic", "Classic"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Boolean NOT NULL",
        "mdbComment": "Game is a classic flag"
    },

    {
        "id": "version",
        "menuPath": ["Version information", "Version"],
        "headingName": "Version",
        "dbColumnNames": ["Games.Version"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Version AS [Games.Version]",
        "dbSelectPlaceholder": "NULL AS [Games.Version]",
        "dbIdentifiers": ["Games.Version", "Version"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "v_length",
        "menuPath": ["Version information", "V Length"],
        "headingName": "V Length",
        "dbColumnNames": ["Games.V_Length"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_Length AS [Games.V_Length]",
        "dbSelectPlaceholder": "NULL AS [Games.V_Length]",
        "dbIdentifiers": ["Games.V_Length", "V_Length"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "Length of Game version (in blocks or disks  - a minus value indicates disks)"
    },
    {
        "id": "v_length_type",
        "menuPath": ["Version information", "V Length type"],
        "headingName": "V Length type",
        "dbColumnNames": ["Games.V_LengthType"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_LengthType AS [Games.V_LengthType]",
        "dbSelectPlaceholder": "NULL AS [Games.V_LengthType]",
        "dbIdentifiers": ["Games.V_LengthType", "V_LengthType"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "v_true_drive_emu",
        "menuPath": ["Version information", "V True drive emu"],
        "headingName": "V True drive emu",
        "dbColumnNames": ["Games.V_TrueDriveEmu"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_TrueDriveEmu AS [Games.V_TrueDriveEmu]",
        "dbSelectPlaceholder": "NULL AS [Games.V_TrueDriveEmu]",
        "dbIdentifiers": ["Games.V_TrueDriveEmu", "V_TrueDriveEmu"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "weblink_name",
        "menuPath": ["Weblinks", "Weblink name"],
        "headingName": "Weblink name",
        "dbColumnNames": ["Games.WebLink_Name"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.WebLink_Name AS [Games.WebLink_Name]",
        "dbSelectPlaceholder": "NULL AS [Games.WebLink_Name]",
        "dbIdentifiers": ["Games.WebLink_Name", "WebLink_Name"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "weblink_url",
        "menuPath": ["Weblinks", "Weblink URL"],
        "headingName": "Weblink URL",
        "dbColumnNames": ["Games.WebLink_URL"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.WebLink_URL AS [Games.WebLink_URL]",
        "dbSelectPlaceholder": "NULL AS [Games.WebLink_URL]",
        "dbIdentifiers": ["Games.WebLink_URL", "WebLink_URL"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
    },
    {
        "id": "v_weblink_name",
        "menuPath": ["Weblinks", "V Weblink name"],
        "headingName": "V Weblink name",
        "dbColumnNames": ["Games.V_WebLink_Name"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_WebLink_Name AS [Games.V_WebLink_Name]",
        "dbSelectPlaceholder": "NULL AS [Games.V_WebLink_Name]",
        "dbIdentifiers": ["Games.V_WebLink_Name", "V_WebLink_Name"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "v_weblink_url",
        "menuPath": ["Weblinks", "V Weblink URL"],
        "headingName": "V Weblink URL",
        "dbColumnNames": ["Games.V_WebLink_URL"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_WebLink_URL AS [Games.V_WebLink_URL]",
        "dbSelectPlaceholder": "NULL AS [Games.V_WebLink_URL]",
        "dbIdentifiers": ["Games.V_WebLink_URL", "V_WebLink_URL"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
    },
    {
        "id": "v_playable",
        "menuPath": ["Version information", "V Playable"],
        "headingName": "V Playable",
        "dbColumnNames": ["Games.V_Playable"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_Playable AS [Games.V_Playable]",
        "dbSelectPlaceholder": "NULL AS [Games.V_Playable]",
        "dbIdentifiers": ["Games.V_Playable", "V_Playable"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },
    {
        "id": "v_original",
        "menuPath": ["Version information", "V Original"],
        "headingName": "V Original",
        "dbColumnNames": ["Games.V_Original"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_Original AS [Games.V_Original]",
        "dbSelectPlaceholder": "NULL AS [Games.V_Original]",
        "dbIdentifiers": ["Games.V_Original", "V_Original"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
    },

    # Comments
    {
        "id": "comment",
        "menuPath": ["Comments", "Comment"],
        "headingName": "Comment",
        "dbColumnNames": ["Games.Comment"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Comment AS [Games.Comment]",
        "dbSelectPlaceholder": "NULL AS [Games.Comment]",
        "dbIdentifiers": ["Games.Comment", "Comment"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "v_comment",
        "menuPath": ["Comments", "V Comment"],
        "headingName": "V Comment",
        "dbColumnNames": ["Games.V_Comment"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.V_Comment AS [Games.V_Comment]",
        "dbSelectPlaceholder": "NULL AS [Games.V_Comment]",
        "dbIdentifiers": ["Games.V_Comment", "V_Comment"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Text (510)",
    },
    {
        "id": "memo_text",
        "menuPath": ["Comments", "Memo text"],
        "headingName": "Memo text",
        "dbColumnNames": ["Games.MemoText"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.MemoText AS [Games.MemoText]",
        "dbSelectPlaceholder": "NULL AS [Games.MemoText]",
        "dbIdentifiers": ["Games.MemoText", "MemoText"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
        "mdbComment": "User Notes field"
    },

    # Internal
    {
        "id": "id",
        "menuPath": ["Internal", "ID"],
        "headingName": "ID",
        "dbColumnNames": ["Games.GA_Id"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.GA_Id AS [Games.GA_Id]",
        "dbSelectPlaceholder": "NULL AS [Games.GA_Id]",
        "dbIdentifiers": ["Games.GA_Id", "GA_Id"],
        "defaultWidth": 50,
        "sortable": False,
        "filterable": False,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "Unique ID"
    },
    {
        "id": "gemus",
        "menuPath": ["Internal", "Gemus"],
        "headingName": "Gemus",
        "dbColumnNames": ["Games.Gemus"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Gemus AS [Games.Gemus]",
        "dbSelectPlaceholder": "NULL AS [Games.Gemus]",
        "dbIdentifiers": ["Games.Gemus", "Gemus"],
        "defaultWidth": 200,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
    },

    #  Filenames
    {
        "id": "filename",
        "menuPath": ["Internal", "Filenames", "Filename"],
        "headingName": "Filename",
        "dbColumnNames": ["Games.Filename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.Filename AS [Games.Filename]",
        "dbSelectPlaceholder": "NULL AS [Games.Filename]",
        "dbIdentifiers": ["Games.Filename", "Filename"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
        "mdbComment": "Game Filename within Game Paths"
    },
    {
        "id": "file_to_run",
        "menuPath": ["Internal", "Filenames", "File to run"],
        "headingName": "File to run",
        "dbColumnNames": ["Games.FileToRun"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.FileToRun AS [Games.FileToRun]",
        "dbSelectPlaceholder": "NULL AS [Games.FileToRun]",
        "dbIdentifiers": ["Games.FileToRun", "FileToRun"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
        "mdbComment": "File to Run within Filename if Filename is an archive containing more than one compatible emulator file"
    },
    {
        "id": "filename_index",
        "menuPath": ["Internal", "Filenames", "Filename index"],
        "headingName": "Filename index",
        "dbColumnNames": ["Games.FilenameIndex"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.FilenameIndex AS [Games.FilenameIndex]",
        "dbSelectPlaceholder": "NULL AS [Games.FilenameIndex]",
        "dbIdentifiers": ["Games.FilenameIndex", "FilenameIndex"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Long Integer",
        "mdbComment": "Image Index inside Game file"
    },
    {
        "id": "screenshot_filename",
        "menuPath": ["Internal", "Filenames", "Screenshot filename"],
        "headingName": "Screenshot filename",
        "dbColumnNames": ["Games.ScrnshotFilename"],
        "dbTableNames": ["Games"],
        "dbSelect": "Games.ScrnshotFilename AS [Games.ScrnshotFilename]",
        "dbSelectPlaceholder": "NULL AS [Games.ScrnshotFilename]",
        "dbIdentifiers": ["Games.ScrnshotFilename", "ScrnshotFilename"],
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "mdbType": "Memo/Hyperlink (255)",
        "mdbComment": "Screenshot Filename (1st screenshot) within Screenshot Paths"
    },
]

def tableColumnSpec_getBySlice(i_startPos=None, i_endPos=None):
    """
    Params:
     i_startPos, i_endPos:
      Either (int)
      or (None)

    Returns:
     (list of TableColumnSpec)
    """
    return g_tableColumnSpecs[i_startPos:i_endPos]

def tableColumnSpec_getById(i_id):
    """
    Params:
     i_id:
      (str)

    Returns:
     Either (TableColumnSpec)
     or (None)
    """
    columns = [column  for column in g_tableColumnSpecs  if column["id"] == i_id]
    if len(columns) == 0:
        return None
    return columns[0]

def tableColumnSpec_getByDbIdentifier(i_identifier, i_caseInsensitive=False):
    """
    Params:
     i_identifier:
      (str)
      A column name, with optional table name prefix.
      eg.
       "Name"
       "Games.Name"
     i_caseInsensitive:
      (bool)

    Returns:
     Either (TableColumnSpec)
     or (None)
    """
    for tableColumnSpec in g_tableColumnSpecs:
        if "dbIdentifiers" in tableColumnSpec:
            for dbIdentifier in tableColumnSpec["dbIdentifiers"]:
                if dbIdentifier == i_identifier or (i_caseInsensitive and dbIdentifier.upper() == i_identifier.upper()):
                    return tableColumnSpec
    return None

# + }}}

# + Currently visible table columns {{{

g_tableColumns = []
# (list of TableColumn)

# Type: TableColumn
#  (dict)
#  Has keys:
#   id
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
      Details of it should exist in g_tableColumnSpecs.
     i_width:
      Either (int)
       Width for new column in pixels
      or (None)
       Use default width from g_tableColumnSpecs.
     i_beforeColumnId:
      Either (str)
       ID of column already present in the table view to insert this column before.
      or (None)
       Add the new column as the last one.

    Returns:
     Either (TableColumn)
     or (None)
      The given i_id does not correspond to a table column spec.
    """
    tableColumnSpec = tableColumnSpec_getById(i_id)
    if tableColumnSpec == None:
        return None

    newTableColumn = {
        "id": tableColumnSpec["id"],
    }
    if i_width != None:
        newTableColumn["width"] = i_width
    else:
        newTableColumn["width"] = tableColumnSpec["defaultWidth"]

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
      Details of it should exist in g_tableColumnSpecs.
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
    # Remove columns from g_tableColumnSpecs that rely on tables and columns that don't exist in the database
    global g_tableColumnSpecs
    def validateTableColumnSpec(i_tableColumnSpec):
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
        return rv
    g_tableColumnSpecs = [column  for column in g_tableColumnSpecs  if validateTableColumnSpec(column)]

    # Remove columns from g_tableColumns that don't exist in g_tableColumnSpecs
    global g_tableColumns
    g_tableColumns = [column  for column in g_tableColumns  if tableColumnSpec_getById(column["id"])]

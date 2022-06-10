_PyGamebase converter_ is a helper app for converting databases from their typical Microsoft Access (.mdb) format to the SQLite (version 3) format which PyGamebase understands. It can also create an initial adapter file for the Gamebase, as needed by the frontend.


# Usage

Start the application by running `python converter.py`.

The application has three tab pages corresponding to common Gamebase setup steps. The steps are independent actions and you don't have to run them all (though the later tab pages do use some settings entered on the previous ones). If you click the button 'Try and auto-fill everything by choosing a GameBase folder...' and direct it to your Gamebase folder, it will try and fill in as many boxes as possible across all three tabs automatically, with some light guessing.


## Step 1: Convert database

The conversion process relies upon the [MDB Tools](https://github.com/mdbtools/mdbtools) suite of programs. Specifically, the `mdb-schema`, `mdb-tables` and `mdb-export` tools must be present on your system. The aforementioned link outlines installation instructions for Linux (on Debian, `apt install mdbtools`; on Arch, search the AUR for `mdbtools`) and MacOS (via Homebrew or MacPorts, in both cases also called `mdbtools`). For Windows users, binary versions of these tools can currently be downloaded from [mdbtools-win Releases page](https://github.com/lsgunth/mdbtools-win) (note that although the download link says "Source code", there are executables inside).

On the form, fill in the location of the MDB Tools (unless they're already in your system's PATH), locate the Access (.mdb) database file to be read, and enter a name for the new SQLite database file to be created. Then click 'Go'.

This tab page is a frontend for the Python script `utility_scripts/mdb_to_sqlite.py`, which you could run instead to do the same thing from the command line.


## Step 2: Fix file paths in database

A Gamebase database contains many paths to external files - games, screenshots, music, photos and extras - and in downloaded Gamebases you will often find that the case (ie. upper/lower) of these paths don't always fully match with the folder and file names that actually exist on disk. On Windows, where Gamebase started out, this doesn't matter, but on Unix filesystems and usually on Mac they need to match. Fill in the base paths to each of the above categories of file (if the Gamebase provides them - else leave that category blank), and click 'Go' - this will search through and change the paths in the SQLite database (as selected on the 'Step 1' tab) to match what actually exists on the disk.

This tab page is a frontend for the Python script `utility_scripts/fix_path_case.py`, which you could run instead to do the same thing from the command line.


## Step 3: Create frontend adapter file

The frontend needs to be run with an 'adapter' file that points it to the new SQLite database to use and the external file directories (so it can show the screenshots, for example). This file is a Python code module that should also contain functions with particular names that do the actual launching of games, extras, music and the like. Naturally being a Python program the possibilities are vast and you should read the frontend guide to [Gamebase adapter files](../frontend/gamebase_adapter_files.html) to best set everything up for your purposes. However this tab page can create a template-like adapter file that might help just to get started.

The "GameBase title" is just for display purposes (in the frontend window title bar). In "Emulator executable", locate the emulator used to launch a game. This will be launched via the system shell, so if it is on your PATH you only really need to provide the name, instead of an absolute path. It will be run with the game file path(s) immediately following the command name as arguments. If you need to specify emulator options or do any kind of argument processing, you should edit the Python script after it's been generated. If the Gamebase comes with music, enter a compatible player into "Music player executable", else leave it blank. In "Adapter file" enter the path of the file to be created (with extension '.py').

This step also uses the 'SQLite database file' setting from 'Step 1' and all of the paths from 'Step 2', so ensure those are also filled in before hitting 'Go'.

This step is written directly into the converter application and there is no seperate command-line script for it at this time.


# Next

Start the frontend

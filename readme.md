_PyGamebase_ is a frontend and launcher for ['Gamebase'](https://www.bu22.com/) game collections.

(pics)

# Getting the program and its dependencies

Clone the repository.

The frontend and helper programs are written in Python 3 with an external library dependency on [PySide2](https://pypi.org/project/PySide2/). Typically, you would install this library with your operating system's package manager, or with the Python-specific command `pip install PySide2`.

# Preparing a Gamebase

This frontend works with Gamebase databases in SQLite format. Since Gamebase databases are normally distributed in Microsoft Access (.mdb) format, you'll need to convert them. The 'PyGamebase converter' app in the ['converter'](converter) directory is provided to help do this. The converter app can also create a starter 'adapter' file for each Gamebase - a Python module which configures file paths, launches emulators, and so on, which the frontend needs to run.

# Running the frontend

Enter the 'frontend' folder and run `python pygamebase.py <adapter file path>`.

If you omit the adapter file you will be prompted with a file selector.

See the full [User guide](frontend/docs/user_guide.html) for more.

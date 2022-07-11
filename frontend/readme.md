_PyGamebase frontend_


# Before you start

This frontend works with Gamebase databases in SQLite format. Since Gamebase databases are normally distributed in Microsoft Access (.mdb) format, you'll need to convert them. The 'PyGamebase converter' app in the ['converter'](../converter) directory is provided to help do this. The converter app can also create a starter 'adapter' file for each Gamebase - a Python module which configures file paths, launches emulators, and so on, which the frontend needs to run.

# Running the frontend

Enter the 'frontend' folder and run `python3 main.py <adapter file path>`.

If you omit an adapter file you will be prompted with a file selector.

See the full [User guide](http://htmlpreview.github.io/?https://github.com/dnlopez/PyGamebase/blob/master/frontend/docs/user_guide.html) for more.
